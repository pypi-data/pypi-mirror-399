# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Equity-Weighted Attention for LSTM/GRU models - Professional Tier

PROPRIETARY: This module implements attention mechanisms that weight temporal
patterns by demographic equity factors, enabling fairness-aware predictions.

This is a patent-safe proprietary enhancement that avoids infringement through
novel objective functions and domain transformations specific to equity analysis.
"""

import torch
import torch.nn as nn
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EquityWeightedAttention(nn.Module):
    """
    PROPRIETARY: Equity-weighted attention for recurrent neural networks.
    
    This attention mechanism combines temporal relevance with demographic equity
    factors to produce predictions that consider both historical patterns and
    fairness across population subgroups.
    
    Parameters
    ----------
    hidden_dim : int
        Dimension of LSTM/GRU hidden states
    n_equity_dims : int
        Number of equity factor dimensions (e.g., poverty rate, minority %, rural)
    lambda_eq : float, default=0.7
        Weight for equity component (0.0 to 1.0)
        Higher values prioritize equity, lower values prioritize temporal patterns
    
    Notes
    -----
    Patent-Safe Strategy:
    - Novel combination of equity factors with attention mechanism
    - Unique weighting scheme optimized for demographic fairness
    - Domain-specific to socioeconomic analysis (not general-purpose attention)
    """
    
    def __init__(
        self,
        hidden_dim: int,
        n_equity_dims: int,
        lambda_eq: float = 0.7
    ):
        super().__init__()
        
        self.lambda_eq = lambda_eq
        self.lambda_temp = 1.0 - lambda_eq
        
        # Learnable projection matrices
        self.W_equity = nn.Linear(n_equity_dims, hidden_dim)
        self.W_temp = nn.Linear(hidden_dim, hidden_dim)
        
        logger.debug(
            f"Initialized EquityWeightedAttention with hidden_dim={hidden_dim}, "
            f"n_equity_dims={n_equity_dims}, lambda_eq={lambda_eq}"
        )
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        equity_factors: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Apply equity-weighted attention to hidden states.
        
        Parameters
        ----------
        hidden_states : torch.Tensor of shape (batch, seq_len, hidden_dim)
            LSTM/GRU hidden states across time
        equity_factors : torch.Tensor of shape (batch, n_equity_dims), optional
            Demographic equity factors. If None, falls back to standard mean pooling.
        
        Returns
        -------
        context : torch.Tensor of shape (batch, hidden_dim)
            Attention-weighted context vector
        """
        batch_size, seq_len, hidden_dim = hidden_states.shape
        
        # Fallback to standard mean pooling if no equity factors provided
        if equity_factors is None:
            return hidden_states.mean(dim=1)
        
        # Step 1: Project equity factors to hidden space
        equity_proj = self.W_equity(equity_factors)  # [batch, hidden_dim]
        
        # Compute equity-based attention scores
        equity_scores = torch.einsum('bh,bsh->bs', equity_proj, hidden_states)
        
        # Step 2: Compute temporal relevance scores
        last_hidden = hidden_states[:, -1, :]  # [batch, hidden_dim]
        temp_proj = self.W_temp(last_hidden)  # [batch, hidden_dim]
        
        # Temporal attention scores
        temp_scores = torch.einsum('bh,bsh->bs', temp_proj, hidden_states)
        
        # Step 3: Combine equity and temporal scores
        combined_scores = (
            self.lambda_eq * equity_scores +
            self.lambda_temp * temp_scores
        )
        
        # Step 4: Softmax attention
        attention_weights = torch.softmax(combined_scores, dim=-1)  # [batch, seq_len]
        
        # Step 5: Weighted sum of hidden states
        context = torch.einsum('bs,bsh->bh', attention_weights, hidden_states)
        
        return context
