import triton
import triton.language as tl
import torch

@triton.jit
def linear_lif_fwd_kernel(
    X_ptr, W_ptr,           # Inputs: X (T, B, In), W (Out, In)
    S_out_ptr,              # Output: S (T, B, Out)
    V_init_ptr, V_final_ptr,# States
    stride_xt, stride_xb, stride_xi, # X strides
    stride_wo, stride_wi,            # W strides
    stride_st, stride_sb, stride_so, # S strides
    T, B, In, Out,          # Dimensions
    decay, threshold,       # LIF params
    BLOCK_B: tl.constexpr, BLOCK_O: tl.constexpr, BLOCK_I: tl.constexpr
):
    # Parallelize over Batch (B) and Output Features (Out)
    pid_b = tl.program_id(0)
    pid_o = tl.program_id(1)
    
    # Offsets for Batch and Out dimensions
    offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
    offs_o = pid_o * BLOCK_O + tl.arange(0, BLOCK_O)
    
    # Masks for boundary checks
    mask_b = offs_b < B
    mask_o = offs_o < Out
    
    # Initialize Voltage state for this tile
    # If V_init_ptr is provided, load it. Assume 0 for now or handled outside.
    # We maintain V in registers for this tile.
    v = tl.zeros((BLOCK_B, BLOCK_O), dtype=tl.float32)
    if V_init_ptr is not None:
        # Load V_init (B, Out)
        # stride for B is Out, stride for Out is 1 (assumed contiguous)
        # actually we should pass strides for V too if we want to be safe, but let's assume contiguous (B, Out)
        offs_v = offs_b[:, None] * Out + offs_o[None, :]
        v = tl.load(V_init_ptr + offs_v, mask=(mask_b[:, None] & mask_o[None, :]), other=0.0)

    # Loop over Time Steps
    for t in range(T):
        
        # 1. Compute Matrix Multiplication (Block GEMM) for this time step
        # Y_tile = X[t, offs_b, :] @ W[offs_o, :].T
        #        = X[t, offs_b, :] @ W.T[:, offs_o]
        
        # Accumulator for dot product
        acc = tl.zeros((BLOCK_B, BLOCK_O), dtype=tl.float32)
        
        # Loop over Inner dimension (In) in blocks
        for k in range(0, In, BLOCK_I):
            offs_i = k + tl.arange(0, BLOCK_I)
            mask_i = offs_i < In
            
            # Load X tile: (BLOCK_B, BLOCK_I)
            # Pointer: X_ptr + t*stride_xt + offs_b*stride_xb + offs_i*stride_xi
            x_ptrs = X_ptr + t * stride_xt + offs_b[:, None] * stride_xb + offs_i[None, :] * stride_xi
            x_tile = tl.load(x_ptrs, mask=(mask_b[:, None] & mask_i[None, :]), other=0.0)
            
            # Load W tile: (BLOCK_O, BLOCK_I)
            # W is (Out, In). We need W[offs_o, offs_i]
            # Pointer: W_ptr + offs_o*stride_wo + offs_i*stride_wi
            w_ptrs = W_ptr + offs_o[:, None] * stride_wo + offs_i[None, :] * stride_wi
            w_tile = tl.load(w_ptrs, mask=(mask_o[:, None] & mask_i[None, :]), other=0.0)
            
            # Dot product: (BLOCK_B, BLOCK_I) @ (BLOCK_O, BLOCK_I).T -> (BLOCK_B, BLOCK_O)
            # tl.dot expects (M, K) and (K, N).
            # We have X (B, I) and W (O, I). We need X @ W.T
            # So W.T is (I, O).
            # We can transpose w_tile before dot? tl.trans(w_tile) -> (I, O)
            
            acc += tl.dot(x_tile, tl.trans(w_tile))
            
        # 2. LIF Update
        # acc now holds Y[t] for this block
        v = v * decay + acc
        
        spike_bool = v >= threshold
        spike_float = spike_bool.to(tl.float32)
        
        # 3. Store Spikes
        # S_out (T, B, Out)
        # Pointer: S_out_ptr + t*stride_st + offs_b*stride_sb + offs_o*stride_so
        s_ptrs = S_out_ptr + t * stride_st + offs_b[:, None] * stride_sb + offs_o[None, :] * stride_so
        tl.store(s_ptrs, spike_float, mask=(mask_b[:, None] & mask_o[None, :]))
        
        # 4. Reset Voltage
        v = tl.where(spike_bool, 0.0, v)
        
    # Store Final Voltage
    if V_final_ptr is not None:
        offs_v = offs_b[:, None] * Out + offs_o[None, :]
        tl.store(V_final_ptr + offs_v, v, mask=(mask_b[:, None] & mask_o[None, :]))

def linear_lif_fwd(x, weight, v_init=None, decay=0.9, threshold=1.0):
    """
    Fused Linear-LIF forward pass.
    x: (T, B, In)
    weight: (Out, In)
    """
    T, B, In = x.shape
    Out, _ = weight.shape
    
    assert weight.shape[1] == In, "Weight input dimension mismatch"
    
    s_out = torch.empty((T, B, Out), device=x.device, dtype=torch.float32)
    v_final = torch.empty((B, Out), device=x.device, dtype=torch.float32)
    
    grid = lambda meta: (
        triton.cdiv(B, meta['BLOCK_B']),
        triton.cdiv(Out, meta['BLOCK_O'])
    )
    
    linear_lif_fwd_kernel[grid](
        x, weight,
        s_out,
        v_init, v_final,
        x.stride(0), x.stride(1), x.stride(2),
        weight.stride(0), weight.stride(1),
        s_out.stride(0), s_out.stride(1), s_out.stride(2),
        T, B, In, Out,
        decay, threshold,
        BLOCK_B=32, BLOCK_O=32, BLOCK_I=32
    )
    
    return s_out, v_final
