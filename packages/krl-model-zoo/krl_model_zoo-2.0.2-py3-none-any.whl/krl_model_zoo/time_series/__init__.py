# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Time Series Models - Community Tier

3 essential time series models:
- LSTM: Long Short-Term Memory networks
- GRU: Gated Recurrent Units
- TabNet: Attention-based tabular model

Professional Tier Enhancements (Sprint 7):
- LSTM with Equity-Weighted Attention
- GRU with Causal Recurrence Gates
- Transformer with Causal Positional Encoding
"""

import torch
import torch.nn as nn
from typing import Optional

# Professional tier enhancements (Sprint 7)
try:
    from krl_model_zoo.core.equity_attention import EquityWeightedAttention
    from krl_model_zoo.core.causal_gates import CausalRecurrenceGates
    from krl_model_zoo.core.causal_positional_encoding import CausalPositionalEncoding
    HAS_ENHANCEMENTS = True
except ImportError:
    HAS_ENHANCEMENTS = False
    EquityWeightedAttention = None
    CausalRecurrenceGates = None
    CausalPositionalEncoding = None

def load_time_series_model(model_name: str, **kwargs):
    """
    Load a time series model from Community tier.
    
    Args:
        model_name: One of: lstm, gru, tabnet
        **kwargs: Model-specific configuration
            
    Returns:
        Model instance
    """
    if model_name == "lstm":
        return load_lstm(**kwargs)
    elif model_name == "gru":
        return load_gru(**kwargs)
    elif model_name == "tabnet":
        return load_tabnet(**kwargs)
    else:
        raise ValueError(f"Unknown time series model: {model_name}")

def load_lstm(
    input_size: int = 1,
    hidden_size: int = 50,
    num_layers: int = 2,
    output_size: int = 1,
    dropout: float = 0.2,
    bidirectional: bool = False,
    use_equity_attention: bool = False,
    n_equity_dims: int = 0,
    **kwargs
):
    """
    Load LSTM for time series forecasting.
    
    Args:
        input_size: Number of input features
        hidden_size: Number of hidden units
        num_layers: Number of LSTM layers
        output_size: Number of output features
        dropout: Dropout probability
        bidirectional: Use bidirectional LSTM
        use_equity_attention: Enable equity-weighted attention (Professional tier)
        n_equity_dims: Number of equity factor dimensions (required if use_equity_attention=True)
    """
    
    class LSTMModel(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers, output_size, dropout, 
                     bidirectional, use_equity_attention, n_equity_dims):
            super().__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            self.bidirectional = bidirectional
            self.use_equity_attention = use_equity_attention
            
            self.lstm = nn.LSTM(
                input_size,
                hidden_size,
                num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0,
                bidirectional=bidirectional
            )
            
            lstm_output_size = hidden_size * 2 if bidirectional else hidden_size
            
            # SPRINT 7 ENHANCEMENT: Equity-Weighted Attention (Professional tier)
            if use_equity_attention and HAS_ENHANCEMENTS:
                if n_equity_dims == 0:
                    raise ValueError(
                        "n_equity_dims must be specified when use_equity_attention=True"
                    )
                self.equity_attention = EquityWeightedAttention(
                    hidden_dim=lstm_output_size,
                    n_equity_dims=n_equity_dims
                )
            else:
                self.equity_attention = None
            
            self.fc = nn.Linear(lstm_output_size, output_size)
        
        def forward(self, x, hidden=None, equity_factors=None):
            # x: (batch_size, seq_len, input_size)
            lstm_out, hidden = self.lstm(x, hidden)
            # lstm_out: (batch_size, seq_len, hidden_size * num_directions)
            
            # SPRINT 7: Apply equity-weighted attention if enabled
            if self.equity_attention is not None and equity_factors is not None:
                # Use attention mechanism
                context = self.equity_attention(lstm_out, equity_factors)
                out = self.fc(context)
            else:
                # Standard: use the output from the last time step
                out = self.fc(lstm_out[:, -1, :])
            # out: (batch_size, output_size)
            
            return out, hidden
        
        def init_hidden(self, batch_size, device='cpu'):
            num_directions = 2 if self.bidirectional else 1
            h0 = torch.zeros(self.num_layers * num_directions, batch_size, self.hidden_size).to(device)
            c0 = torch.zeros(self.num_layers * num_directions, batch_size, self.hidden_size).to(device)
            return (h0, c0)
    
    model = LSTMModel(input_size, hidden_size, num_layers, output_size, dropout, 
                     bidirectional, use_equity_attention, n_equity_dims)
    return model

def load_gru(
    input_size: int = 1,
    hidden_size: int = 50,
    num_layers: int = 2,
    output_size: int = 1,
    dropout: float = 0.2,
    bidirectional: bool = False,
    use_causal_gates: bool = False,
    n_variables: int = 0,
    causal_dag: Optional[object] = None,
    **kwargs
):
    """
    Load GRU for time series forecasting.
    
    Args:
        input_size: Number of input features
        hidden_size: Number of hidden units
        num_layers: Number of GRU layers
        output_size: Number of output features
        dropout: Dropout probability
        bidirectional: Use bidirectional GRU
        use_causal_gates: Enable causal recurrence gates (Professional tier)
        n_variables: Number of variables (required if use_causal_gates=True)
        causal_dag: networkx.DiGraph encoding causal relationships (optional)
    """
    
    class GRUModel(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers, output_size, dropout, 
                     bidirectional, use_causal_gates, n_variables, causal_dag):
            super().__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            self.bidirectional = bidirectional
            self.use_causal_gates = use_causal_gates
            
            self.gru = nn.GRU(
                input_size,
                hidden_size,
                num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0,
                bidirectional=bidirectional
            )
            
            gru_output_size = hidden_size * 2 if bidirectional else hidden_size
            
            # SPRINT 7 ENHANCEMENT: Causal Recurrence Gates (Professional tier)
            if use_causal_gates and HAS_ENHANCEMENTS:
                if n_variables == 0:
                    raise ValueError(
                        "n_variables must be specified when use_causal_gates=True"
                    )
                self.causal_gates = CausalRecurrenceGates(
                    hidden_size=hidden_size,
                    n_variables=n_variables,
                    causal_dag=causal_dag
                )
            else:
                self.causal_gates = None
            
            self.fc = nn.Linear(gru_output_size, output_size)
        
        def forward(self, x, hidden=None):
            # x: (batch_size, seq_len, input_size)
            
            # SPRINT 7: Apply causal gates if enabled
            if self.causal_gates is not None:
                # Apply causal mask to inputs before GRU
                # Note: This is a simplified integration. Full implementation
                # would integrate masks into gate activations.
                x_masked = self.causal_gates.apply_causal_mask(x)
                gru_out, hidden = self.gru(x_masked, hidden)
            else:
                gru_out, hidden = self.gru(x, hidden)
            # gru_out: (batch_size, seq_len, hidden_size * num_directions)
            
            # Use the output from the last time step
            out = self.fc(gru_out[:, -1, :])
            # out: (batch_size, output_size)
            
            return out, hidden
        
        def init_hidden(self, batch_size, device='cpu'):
            num_directions = 2 if self.bidirectional else 1
            h0 = torch.zeros(self.num_layers * num_directions, batch_size, self.hidden_size).to(device)
            return h0
    
    model = GRUModel(input_size, hidden_size, num_layers, output_size, dropout, 
                    bidirectional, use_causal_gates, n_variables, causal_dag)
    return model

def load_tabnet(
    input_dim: int,
    output_dim: int,
    n_d: int = 8,
    n_a: int = 8,
    n_steps: int = 3,
    gamma: float = 1.3,
    n_independent: int = 2,
    n_shared: int = 2,
    epsilon: float = 1e-15,
    **kwargs
):
    """
    Load TabNet for tabular data.
    
    TabNet uses sequential attention to select important features at each decision step.
    
    Args:
        input_dim: Number of input features
        output_dim: Number of output classes (1 for regression)
        n_d: Width of the decision prediction layer
        n_a: Width of the attention embedding
        n_steps: Number of sequential steps
        gamma: Relaxation factor for feature reusage
        n_independent: Number of independent GLU layers
        n_shared: Number of shared GLU layers
        epsilon: Numerical stability constant
    """
    try:
        from pytorch_tabnet.tab_model import TabNetClassifier, TabNetRegressor
    except ImportError:
        raise ImportError("Please install pytorch-tabnet: pip install pytorch-tabnet")
    
    # Determine if classification or regression
    if output_dim == 1 or kwargs.get('task') == 'regression':
        model = TabNetRegressor(
            n_d=n_d,
            n_a=n_a,
            n_steps=n_steps,
            gamma=gamma,
            n_independent=n_independent,
            n_shared=n_shared,
            epsilon=epsilon
        )
    else:
        model = TabNetClassifier(
            n_d=n_d,
            n_a=n_a,
            n_steps=n_steps,
            gamma=gamma,
            n_independent=n_independent,
            n_shared=n_shared,
            epsilon=epsilon
        )
    
    return model

def load_transformer(
    d_model: int = 64,
    nhead: int = 4,
    num_layers: int = 2,
    dim_feedforward: int = 256,
    dropout: float = 0.1,
    input_size: int = 1,
    output_size: int = 1,
    use_causal_pe: bool = False,
    causal_dag: Optional[object] = None,
    variable_names: Optional[list] = None,
    **kwargs
):
    """
    Load Transformer for time series forecasting.
    
    Args:
        d_model: Dimension of model embeddings (must be divisible by nhead)
        nhead: Number of attention heads
        num_layers: Number of transformer encoder layers
        dim_feedforward: Dimension of feedforward network
        dropout: Dropout probability
        input_size: Number of input features
        output_size: Number of output features
        use_causal_pe: Enable causal positional encoding (Professional tier)
        causal_dag: networkx.DiGraph encoding causal relationships (optional)
        variable_names: List of variable names matching DAG nodes (optional)
    """
    
    class TransformerModel(nn.Module):
        def __init__(self, d_model, nhead, num_layers, dim_feedforward, dropout,
                     input_size, output_size, use_causal_pe, causal_dag, variable_names):
            super().__init__()
            self.d_model = d_model
            self.use_causal_pe = use_causal_pe
            
            # Input projection
            self.input_projection = nn.Linear(input_size, d_model)
            
            # SPRINT 7 ENHANCEMENT: Causal Positional Encoding (Professional tier)
            if use_causal_pe and HAS_ENHANCEMENTS:
                if variable_names is None:
                    raise ValueError(
                        "variable_names must be specified when use_causal_pe=True"
                    )
                self.pos_encoder = CausalPositionalEncoding(
                    d_model=d_model,
                    causal_dag=causal_dag,
                    variable_names=variable_names,
                    dropout=dropout
                )
            else:
                # Standard positional encoding
                self.pos_encoder = self._create_standard_pe(d_model, dropout)
            
            # Transformer encoder
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=dim_feedforward,
                dropout=dropout,
                batch_first=True
            )
            self.transformer_encoder = nn.TransformerEncoder(
                encoder_layer,
                num_layers=num_layers
            )
            
            # Output projection
            self.output_projection = nn.Linear(d_model, output_size)
        
        def _create_standard_pe(self, d_model, dropout):
            """Create standard sinusoidal positional encoding as fallback."""
            import math
            
            class StandardPositionalEncoding(nn.Module):
                def __init__(self, d_model, dropout=0.1, max_len=5000):
                    super().__init__()
                    self.dropout = nn.Dropout(p=dropout)
                    
                    pe = torch.zeros(max_len, d_model)
                    position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
                    div_term = torch.exp(
                        torch.arange(0, d_model, 2).float() * 
                        (-math.log(10000.0) / d_model)
                    )
                    
                    pe[:, 0::2] = torch.sin(position * div_term)
                    pe[:, 1::2] = torch.cos(position * div_term)
                    pe = pe.unsqueeze(0)
                    self.register_buffer('pe', pe)
                
                def forward(self, x):
                    x = x + self.pe[:, :x.size(1), :]
                    return self.dropout(x)
            
            return StandardPositionalEncoding(d_model, dropout)
        
        def forward(self, x, src_mask=None):
            # x: (batch_size, seq_len, input_size)
            
            # Project to d_model
            x = self.input_projection(x)  # (batch, seq_len, d_model)
            
            # Add positional encoding (causal or standard)
            x = self.pos_encoder(x)
            
            # Pass through transformer encoder
            x = self.transformer_encoder(x, src_mask)
            
            # Use the last timestep for prediction
            x = x[:, -1, :]  # (batch, d_model)
            
            # Project to output
            out = self.output_projection(x)  # (batch, output_size)
            
            return out
    
    model = TransformerModel(d_model, nhead, num_layers, dim_feedforward, dropout,
                            input_size, output_size, use_causal_pe, causal_dag, 
                            variable_names)
    return model

__all__ = [
    "load_time_series_model",
    "load_lstm",
    "load_gru",
    "load_tabnet",
    "load_transformer"
]
