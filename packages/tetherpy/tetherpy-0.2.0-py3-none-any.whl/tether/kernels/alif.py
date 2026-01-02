import triton
import triton.language as tl


@triton.jit
def alif_fwd_kernel(
    X_ptr,
    V_init_ptr,
    A_init_ptr,
    S_out_ptr,
    S_packed_ptr,
    V_seq_ptr,
    V_final_ptr,
    A_seq_ptr,
    A_final_ptr,
    n_neurons,
    n_steps,
    decay_v,
    decay_a,
    threshold_base,
    beta,
    BLOCK_SIZE: tl.constexpr,
):
    """
    Triton kernel for the Adaptive Leaky Integrate-and-Fire (ALIF) forward pass.

    This kernel performs the iterative update of membrane potential and adaptive
    threshold for a batch of neurons over a temporal sequence.

    Parameters
    ----------
    X_ptr : pointer
        Input current sequence pointer. Shape: (n_steps, n_neurons).
    V_init_ptr : pointer
        Initial membrane potential pointer. Shape: (n_neurons,).
    A_init_ptr : pointer
        Initial adaptation variable pointer. Shape: (n_neurons,).
    S_out_ptr : pointer
        Output spikes pointer (float). Shape: (n_steps, n_neurons).
    S_packed_ptr : pointer
        Packed output spikes pointer (int32). Shape: (ceil(n_steps/32), n_neurons).
    V_seq_ptr : pointer
        Membrane potential sequence pointer. Shape: (n_steps, n_neurons).
    V_final_ptr : pointer
        Final membrane potential pointer. Shape: (n_neurons,).
    A_seq_ptr : pointer
        Adaptation variable sequence pointer. Shape: (n_steps, n_neurons).
    A_final_ptr : pointer
        Final adaptation variable pointer. Shape: (n_neurons,).
    n_neurons : int
        Number of neurons.
    n_steps : int
        Number of time steps.
    decay_v : float
        Membrane potential decay factor (scalar).
    decay_a : float
        Adaptation variable decay factor (scalar).
    threshold_base : float
        Base spiking threshold (scalar).
    beta : float
        Adaptive threshold scaling factor (scalar).
    BLOCK_SIZE : int
        Triton block size configuration.
    """
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_neurons

    v = tl.load(V_init_ptr + offsets, mask=mask)
    a = tl.load(A_init_ptr + offsets, mask=mask)

    packed_spikes = tl.zeros([BLOCK_SIZE], dtype=tl.int32)

    for t in range(n_steps):
        x = tl.load(X_ptr + t * n_neurons + offsets, mask=mask)
        v = v * decay_v + x

        # Store v before reset
        tl.store(V_seq_ptr + t * n_neurons + offsets, v, mask=mask)
        # Store a
        tl.store(A_seq_ptr + t * n_neurons + offsets, a, mask=mask)

        thresh = threshold_base + beta * a

        spike_bool = v >= thresh
        spike_float = spike_bool.to(tl.float32)

        tl.store(S_out_ptr + t * n_neurons + offsets, spike_float, mask=mask)

        # Packing
        bit_idx = t % 32
        bit_val = 1 << bit_idx
        added_bit = tl.where(spike_bool, bit_val, 0)
        packed_spikes = packed_spikes | added_bit

        if bit_idx == 31:
            block_idx = t // 32
            tl.store(
                S_packed_ptr + block_idx * n_neurons + offsets, packed_spikes, mask=mask
            )
            packed_spikes = tl.zeros([BLOCK_SIZE], dtype=tl.int32)

        # Reset and Update
        v = tl.where(spike_bool, 0.0, v)
        a = a * decay_a + spike_float

    tl.store(V_final_ptr + offsets, v, mask=mask)
    tl.store(A_final_ptr + offsets, a, mask=mask)

    if (n_steps % 32) != 0:
        block_idx = n_steps // 32
        tl.store(
            S_packed_ptr + block_idx * n_neurons + offsets, packed_spikes, mask=mask
        )


@triton.jit
def alif_bwd_kernel(
    GRAD_OUT_ptr,
    S_packed_ptr,
    V_seq_ptr,
    A_seq_ptr,
    GRAD_X_ptr,
    GRAD_V_FINAL_ptr,
    GRAD_A_FINAL_ptr,
    V_init_ptr,
    A_init_ptr,
    n_neurons,
    n_steps,
    decay_v_ptr,
    decay_a_ptr,
    threshold_ptr,
    beta_ptr,
    alpha_ptr,
    GRAD_DECAY_V_ptr,
    GRAD_DECAY_A_ptr,
    GRAD_THRESHOLD_ptr,
    GRAD_BETA_ptr,
    GRAD_ALPHA_ptr,
    BLOCK_SIZE: tl.constexpr,
):
    """
    Triton kernel for the Adaptive Leaky Integrate-and-Fire (ALIF) backward pass.

    Computes gradients for inputs and parameters using Backpropagation Through Time (BPTT)
    with a surrogate gradient for the non-differentiable spiking step.

    Parameters
    ----------
    GRAD_OUT_ptr : pointer
        Gradient w.r.t. output spikes. Shape: (n_steps, n_neurons).
    S_packed_ptr : pointer
        Packed spikes from forward pass. Shape: (ceil(n_steps/32), n_neurons).
    V_seq_ptr : pointer
        Membrane potential sequence. Shape: (n_steps, n_neurons).
    A_seq_ptr : pointer
        Adaptation variable sequence. Shape: (n_steps, n_neurons).
    GRAD_X_ptr : pointer
        Output gradient w.r.t. input current. Shape: (n_steps, n_neurons).
    GRAD_V_FINAL_ptr : pointer
        Gradient w.r.t. final membrane potential. Shape: (n_neurons,).
    GRAD_A_FINAL_ptr : pointer
        Gradient w.r.t. final adaptation variable. Shape: (n_neurons,).
    V_init_ptr : pointer
        Initial membrane potential. Shape: (n_neurons,).
    A_init_ptr : pointer
        Initial adaptation variable. Shape: (n_neurons,).
    n_neurons : int
        Number of neurons.
    n_steps : int
        Number of time steps.
    decay_v_ptr : pointer
        Pointer to membrane potential decay parameter (scalar).
    decay_a_ptr : pointer
        Pointer to adaptation variable decay parameter (scalar).
    threshold_ptr : pointer
        Pointer to base threshold parameter (scalar).
    beta_ptr : pointer
        Pointer to beta parameter (scalar).
    alpha_ptr : pointer
        Pointer to alpha parameter (scalar).
    GRAD_DECAY_V_ptr : pointer
        Output gradient w.r.t. decay_v.
    GRAD_DECAY_A_ptr : pointer
        Output gradient w.r.t. decay_a.
    GRAD_THRESHOLD_ptr : pointer
        Output gradient w.r.t. threshold.
    GRAD_BETA_ptr : pointer
        Output gradient w.r.t. beta.
    GRAD_ALPHA_ptr : pointer
        Output gradient w.r.t. alpha.
    BLOCK_SIZE : int
        Triton block size configuration.
    """
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_neurons

    alpha = tl.load(alpha_ptr)
    decay_v = tl.load(decay_v_ptr)
    decay_a = tl.load(decay_a_ptr)
    threshold = tl.load(threshold_ptr)
    beta = tl.load(beta_ptr)

    grad_v = tl.load(GRAD_V_FINAL_ptr + offsets, mask=mask)
    grad_a = tl.load(
        GRAD_A_FINAL_ptr + offsets, mask=mask
    )  # Usually 0 or from next chunk

    d_decay_v = 0.0
    d_decay_a = 0.0
    d_threshold = 0.0
    d_beta = 0.0
    d_alpha = 0.0

    current_packed = tl.zeros([BLOCK_SIZE], dtype=tl.int32)

    for t in range(n_steps - 1, -1, -1):
        bit_idx = t % 32
        if t == n_steps - 1 or bit_idx == 31:
            block_idx = t // 32
            current_packed = tl.load(
                S_packed_ptr + block_idx * n_neurons + offsets, mask=mask
            )

        spike_int = (current_packed >> bit_idx) & 1
        spike = spike_int.to(tl.float32)

        grad_out = tl.load(GRAD_OUT_ptr + t * n_neurons + offsets, mask=mask)
        v = tl.load(V_seq_ptr + t * n_neurons + offsets, mask=mask)
        a = tl.load(A_seq_ptr + t * n_neurons + offsets, mask=mask)

        # Total gradient w.r.t spike
        # grad_a contains dL/da[t+1]. Since a[t+1] = a[t]*da + s[t], d_a[t+1]/ds[t] = 1.
        # So add grad_a to grad_s
        total_grad_s = grad_out + grad_a

        # Surrogate
        thresh_dynamic = threshold + beta * a
        pi = 3.14159265359
        diff = alpha * pi * (v - thresh_dynamic)
        denom = 1.0 + diff * diff
        surrogate = alpha / denom

        # dL/dU where U = v - thresh_dynamic
        grad_u = total_grad_s * surrogate

        # Update gradients for params
        d_threshold -= tl.sum(grad_u)
        d_alpha += tl.sum(total_grad_s * (v - thresh_dynamic) * surrogate / alpha)
        d_beta -= tl.sum(grad_u * a)

        # Gradient flow to v[t]
        # grad_v comes from future v[t+1]
        # v[t+1] = v[t]*dv * (1-s) + x
        # dL/dv[t] = dL/dv[t+1] * dv[t+1]/dv[t] + dL/ds * ds/dv
        #          = grad_v * dv * (1-s) + total_grad_s * surrogate

        grad_v_new = grad_u + grad_v * decay_v * (1.0 - spike)
        tl.store(GRAD_X_ptr + t * n_neurons + offsets, grad_v_new, mask=mask)

        # Gradient flow to a[t]
        # a[t+1] = a[t]*da + s[t]
        # dL/da[t] = dL/da[t+1] * da + dL/ds * ds/da
        #          = grad_a * da + total_grad_s * surrogate * (-beta)
        # Wait, ds/da = ds/dU * dU/da = surrogate * (-beta)

        grad_a_new = grad_a * decay_a - grad_u * beta

        # Update grad_v and grad_a for next step (t-1)
        grad_v = grad_v_new
        grad_a = grad_a_new

        # Gradients for decays
        # dL/d(decay_v) += grad_v_new * v[t-1] * (1-s[t-1])
        # Actually v[t] = v[t-1]*dv + ...
        # so dL/d(decay_v) += dL/dv[t] * v[t-1]
        # dL/dv[t] is grad_v_new.

        if t > 0:
            v_prev = tl.load(V_seq_ptr + (t - 1) * n_neurons + offsets, mask=mask)
            a_prev = tl.load(A_seq_ptr + (t - 1) * n_neurons + offsets, mask=mask)

            # Retrieve spike[t-1] for reset handling
            if bit_idx > 0:
                s_prev_int = (current_packed >> (bit_idx - 1)) & 1
                s_prev = s_prev_int.to(tl.float32)
            else:
                prev_packed = tl.load(
                    S_packed_ptr + (t // 32 - 1) * n_neurons + offsets, mask=mask
                )
                s_prev_int = (prev_packed >> 31) & 1
                s_prev = s_prev_int.to(tl.float32)

            v_prev_post = v_prev * (1.0 - s_prev)
            d_decay_v += tl.sum(grad_v * v_prev_post)
            d_decay_a += tl.sum(
                grad_a * a_prev
            )  # grad_a is currently dL/da[t]. a[t] = a[t-1]*da + ...
            # Wait, at this point `grad_a` is `grad_a_new` which is dL/da[t].
            # a[t] = a[t-1] * decay_a + s[t-1].
            # d a[t] / d decay_a = a[t-1].
            # Correct.

        else:
            v_prev_post = tl.load(V_init_ptr + offsets, mask=mask)
            a_prev = tl.load(A_init_ptr + offsets, mask=mask)
            d_decay_v += tl.sum(grad_v * v_prev_post)
            d_decay_a += tl.sum(grad_a * a_prev)

    tl.atomic_add(GRAD_DECAY_V_ptr, d_decay_v)
    tl.atomic_add(GRAD_DECAY_A_ptr, d_decay_a)
    tl.atomic_add(GRAD_THRESHOLD_ptr, d_threshold)
    tl.atomic_add(GRAD_BETA_ptr, d_beta)
    tl.atomic_add(GRAD_ALPHA_ptr, d_alpha)
