import triton
import triton.language as tl
import torch

@triton.jit
def rate_encoding_kernel(
    X_ptr,
    S_out_ptr,
    n_elements,
    n_steps,
    gain,
    seed,
    BLOCK_SIZE: tl.constexpr,
):
    """
    Triton kernel for rate encoding.
    Generates spikes based on input probabilities.
    
    Parameters
    ----------
    X_ptr : pointer
        Input tensor pointer. Shape: (n_elements,).
    S_out_ptr : pointer
        Output spikes pointer. Shape: (n_steps, n_elements).
    n_elements : int
        Number of input elements (batch * channels * height * width).
    n_steps : int
        Number of time steps.
    gain : float
        Gain factor to scale input probabilities.
    seed : int
        Random seed.
    BLOCK_SIZE : int
        Block size.
    """
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    
    # Load input probability for this block of elements
    # Input is static over time
    x_val = tl.load(X_ptr + offsets, mask=mask, other=0.0)
    prob = x_val * gain
    # Clamp probability
    prob = tl.minimum(tl.maximum(prob, 0.0), 1.0)
    
    # Loop over time steps
    # We could also parallelize over time if we want, but usually n_steps is small (10-100)
    # and we want to write contiguous memory for output if possible.
    # Actually, X is (N,), Output is (T, N).
    # Strides: Output [N, 1] if T is leading dim?
    # Usually shape is (T, B, C, H, W) -> (T, N).
    # So stride for T is N.
    
    for t in range(n_steps):
        # Generate random value for each element at this time step
        # Philox RNG: seed, offset
        # offset should be unique per (t, element_idx)
        rand_offset = t * n_elements + offsets
        rand_val = tl.rand(seed, rand_offset)
        
        spike = rand_val < prob
        
        # Store spike
        # Output pointer offset: t * n_elements + offsets
        output_offset = t * n_elements + offsets
        tl.store(S_out_ptr + output_offset, spike.to(tl.float32), mask=mask)

def rate_encoding_triton(x: torch.Tensor, n_steps: int, gain: float = 1.0) -> torch.Tensor:
    """
    Apply rate encoding using Triton kernel.
    """
    if not x.is_cuda:
        # Fallback to CPU implementation or move to CUDA?
        # For now, let's assume we want to support CPU inputs by moving them, 
        # or just fallback. The prompt implies x might be on CPU initially.
        # "if the input tensor x is passed from a standard DataLoader, it may still be on the CPU... 
        # Moving the entire encoding process into a GPU-side Triton kernel..."
        x = x.cuda()
    
    # Flatten input
    x_flat = x.reshape(-1)
    n_elements = x_flat.numel()
    
    # Allocate output
    # Shape: (n_steps, *x.shape)
    out_shape = (n_steps,) + x.shape
    spikes = torch.empty(out_shape, device=x.device, dtype=torch.float32)
    
    grid = lambda meta: (triton.cdiv(n_elements, meta['BLOCK_SIZE']),)
    
    # Generate a random seed
    seed = torch.randint(0, 2**31, (1,), device=x.device).item()
    
    rate_encoding_kernel[grid](
        x_flat,
        spikes,
        n_elements,
        n_steps,
        gain,
        seed,
        BLOCK_SIZE=1024,
    )
    
    return spikes
