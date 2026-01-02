import torch
import torch.nn as nn
import torch.nn.functional as F

class LinearLIF(nn.Module):
    """
    Fused Linear layer followed by Leaky Integrate-and-Fire (LIF) activation.
    Optimized with Triton kernel for fused computation (Linear + LIF) to reduce HBM access.
    """
    def __init__(
        self,
        in_features,
        out_features,
        decay=0.9,
        threshold=1.0,
        bias=False, # Bias not supported in fused kernel yet
        device=None,
        dtype=None,
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.decay = decay
        self.threshold = threshold
        
        self.weight = nn.Parameter(torch.empty((out_features, in_features), device=device, dtype=dtype))
        self.reset_parameters()
        
        # State
        self.register_buffer("v", None)
        
    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=5**0.5)

    def forward(self, x):
        """
        Forward pass.
        Args:
            x: Input tensor of shape (T, B, In)
        Returns:
            spikes: Output tensor of shape (T, B, Out)
        """
        # Assume input is (T, B, In)
        if x.dim() != 3:
            raise ValueError(f"Expected 3D input (T, B, In), got {x.shape}")
            
        T, B, _ = x.shape
        
        # Initialize state if needed
        if self.v is None or self.v.shape != (B, self.out_features):
            self.v = torch.zeros((B, self.out_features), device=x.device, dtype=x.dtype)
            
        if torch.cuda.is_available() and x.is_cuda:
            try:
                from ..kernels.linear_lif import linear_lif_fwd
                spikes, v_next = linear_lif_fwd(
                    x, self.weight, self.v, self.decay, self.threshold
                )
                self.v = v_next.detach()
                return spikes
            except (ImportError, RuntimeError) as e:
                # Fallback if kernel fails or not found
                pass

        # Fallback Implementation
        # 1. Linear Projection
        # x: (T, B, In) -> (T*B, In)
        x_flat = x.reshape(-1, self.in_features)
        y_flat = F.linear(x_flat, self.weight)
        y = y_flat.reshape(T, B, self.out_features)
        
        # 2. LIF Dynamics
        spikes_list = []
        v = self.v
        
        for t in range(T):
            v = v * self.decay + y[t]
            spike = (v >= self.threshold).float()
            spikes_list.append(spike)
            v = v * (1.0 - spike) # Reset
            
        self.v = v.detach()
        return torch.stack(spikes_list)
