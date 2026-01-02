import torch
import torch.nn as nn
from .lif import LIF


class SpikingSelfAttention(nn.Module):
    def __init__(self, dim, num_heads=8, decay=0.9, threshold=1.0):
        """
        Initialize the SpikingSelfAttention module.

        Parameters
        ----------
        dim : int
            Model dimension.
        num_heads : int, optional
            Number of attention heads (default is 8).
        decay : float, optional
            Decay factor for LIF neurons (default is 0.9).
        threshold : float, optional
            Threshold for LIF neurons (default is 1.0).
        """
        super().__init__()
        self.num_heads = num_heads
        self.dim = dim
        self.head_dim = dim // num_heads
        self.scale = self.head_dim**-0.5

        self.q_linear = nn.Linear(dim, dim, bias=False)
        self.k_linear = nn.Linear(dim, dim, bias=False)
        self.v_linear = nn.Linear(dim, dim, bias=False)

        self.q_lif = LIF(dim, decay=decay, threshold=threshold)
        self.k_lif = LIF(dim, decay=decay, threshold=threshold)
        self.v_lif = LIF(dim, decay=decay, threshold=threshold)
        self.proj = nn.Linear(dim, dim)

        # Buffer to store the running sum of KV for streaming inference
        self.register_buffer("kv_state", None)

    def reset_states(self):
        """
        Reset the KV state buffer to zeros.
        """
        if self.kv_state is not None:
            self.kv_state.zero_()

    def forward(self, x_seq):
        """
        Forward pass of the SpikingSelfAttention.

        Parameters
        ----------
        x_seq : torch.Tensor
            Input sequence of shape (T, B, N, D).

        Returns
        -------
        torch.Tensor
            Output sequence of shape (T, B, N, D).
        """
        T, B, N, D = x_seq.shape
        x_flat = x_seq.view(T, B * N, D)

        # Q, K, V Generation through LIF neurons
        # Output spikes are (T, B*N, D)
        q = self.q_lif(self.q_linear(x_flat)).view(
            T, B, self.num_heads, N, self.head_dim
        )
        k = self.k_lif(self.k_linear(x_flat)).view(
            T, B, self.num_heads, N, self.head_dim
        )
        v = self.v_lif(self.v_linear(x_flat)).view(
            T, B, self.num_heads, N, self.head_dim
        )

        # Causal Linear Spike-Driven Attention
        if torch.cuda.is_available():
            try:
                from ..kernels.attention import causal_linear_attention_fused
                
                # Check state compatibility
                if self.kv_state is not None:
                    if self.kv_state.shape[0] != B:
                        self.kv_state = None
                
                out, self.kv_state = causal_linear_attention_fused(q, k, v, self.kv_state)
                # self.kv_state is already detached in the kernel return logic if we implemented it right?
                # Actually my kernel wrapper returns a new tensor. It is attached to graph if created via torch.empty?
                # Wait, the wrapper returns `out` (attached?) and `state_out` (attached?).
                # `out` should be attached for gradients. `state_out` is needed for next step.
                # Usually we want `state_out` to be detached for the next iteration if it's truncated BPTT?
                # The original code did `self.kv_state = context[-1].detach()`.
                self.kv_state = self.kv_state.detach()
                
            except (ImportError, RuntimeError):
                # Fallback
                kv = k * v
                context = torch.cumsum(kv, dim=0)

                if self.kv_state is not None:
                    if self.kv_state.shape[0] != B:
                        self.kv_state = torch.zeros(
                            B, self.num_heads, N, self.head_dim, device=x_seq.device
                        )
                    context = context + self.kv_state

                self.kv_state = context[-1].detach()
                out = q * context
        else:
             kv = k * v
             context = torch.cumsum(kv, dim=0)

             if self.kv_state is not None:
                 if self.kv_state.shape[0] != B:
                     self.kv_state = torch.zeros(
                         B, self.num_heads, N, self.head_dim, device=x_seq.device
                     )
                 context = context + self.kv_state

             self.kv_state = context[-1].detach()
             out = q * context

        out = out.view(T, B * N, D)
        return self.proj(out).view(T, B, N, D)
