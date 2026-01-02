import triton
import triton.language as tl
import torch

@triton.jit
def causal_linear_attention_kernel(
    Q_ptr, K_ptr, V_ptr,
    Out_ptr,
    State_in_ptr, State_out_ptr,
    n_elements, n_steps,
    has_initial_state: tl.constexpr,
    store_final_state: tl.constexpr,
    BLOCK_SIZE: tl.constexpr
):
    """
    Fused kernel for Causal Linear Spike-Driven Attention.
    Computes: out_t = q_t * cumsum(k_t * v_t)
    
    Parallelized over the batch/feature dimensions (n_elements).
    Loops over time (n_steps).
    """
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    
    # Initialize state (accumulator)
    accumulator = tl.zeros([BLOCK_SIZE], dtype=tl.float32)
    
    if has_initial_state:
        # Load initial state if provided
        # State shape is (n_elements,) (collapsed B, H, N, D)
        accumulator = tl.load(State_in_ptr + offsets, mask=mask, other=0.0)
    
    # Loop over time
    for t in range(n_steps):
        # Calculate offset for this time step
        # Data layout: (T, n_elements)
        # stride for T is n_elements
        curr_offset = t * n_elements + offsets
        
        q = tl.load(Q_ptr + curr_offset, mask=mask, other=0.0)
        k = tl.load(K_ptr + curr_offset, mask=mask, other=0.0)
        v = tl.load(V_ptr + curr_offset, mask=mask, other=0.0)
        
        # KV term
        kv = k * v
        
        # Accumulate
        accumulator += kv
        
        # Compute Output
        out = q * accumulator
        
        # Store Output
        tl.store(Out_ptr + curr_offset, out, mask=mask)
        
    if store_final_state:
        tl.store(State_out_ptr + offsets, accumulator, mask=mask)

def causal_linear_attention_fused(q, k, v, state_in=None):
    """
    Args:
        q, k, v: (T, B, H, N, D)
        state_in: (B, H, N, D) or None
        
    Returns:
        out: (T, B, H, N, D)
        state_out: (B, H, N, D)
    """
    T, B, H, N, D = q.shape
    n_elements = B * H * N * D
    
    # Flatten non-time dimensions
    q_flat = q.contiguous()
    k_flat = k.contiguous()
    v_flat = v.contiguous()
    
    out = torch.empty_like(q_flat)
    
    state_out = torch.empty((B, H, N, D), device=q.device, dtype=q.dtype) if state_in is not None or True else None
    # We always return state_out to update the buffer
    
    grid = lambda meta: (triton.cdiv(n_elements, meta['BLOCK_SIZE']),)
    
    has_initial_state = state_in is not None
    
    # Use state_out as dummy ptr if state_in is None
    state_in_ptr = state_in if has_initial_state else state_out

    causal_linear_attention_kernel[grid](
        q_flat, k_flat, v_flat,
        out,
        state_in_ptr,
        state_out,
        n_elements, T,
        has_initial_state=has_initial_state,
        store_final_state=True,
        BLOCK_SIZE=1024
    )
    
    return out, state_out
