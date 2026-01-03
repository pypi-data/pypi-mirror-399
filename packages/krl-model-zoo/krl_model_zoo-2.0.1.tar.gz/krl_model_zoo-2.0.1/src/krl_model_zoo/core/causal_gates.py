# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Causal Recurrence Gates for GRU Networks - Professional Tier

PROPRIETARY: This module contains algorithms for enforcing causal constraints
in recurrent neural networks using domain knowledge from directed acyclic graphs.

Patent-Safe Strategy: Novel application of causal graph structure to RNN gates,
domain-specific to multi-domain causal analysis (not general-purpose masking).
"""

import torch
import torch.nn as nn
from typing import Optional, Dict
import numpy as np

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None


class CausalRecurrenceGates(nn.Module):
    """
    Causal recurrence gate mechanism for GRU networks.
    
    This implementation enforces causal constraints derived from domain knowledge
    (DAGs) within the GRU gate mechanism, preventing future information leakage
    while allowing historical causal dependencies.
    
    Key Innovation: Unlike standard attention masks that operate on timesteps,
    this mechanism operates on feature dimensions, masking interactions between
    variables that violate causal ordering.
    
    Parameters
    ----------
    hidden_size : int
        Dimension of GRU hidden state
    n_variables : int
        Number of input variables (features)
    causal_dag : networkx.DiGraph, optional
        Directed acyclic graph encoding causal relationships.
        Edge u -> v means "u causally influences v".
        If None, all variables can influence all others.
    
    Notes
    -----
    Patent-Safe Strategy:
    - Domain-specific application to multi-domain causal graphs (33 KRL domains)
    - Novel gate masking mechanism distinct from standard attention
    - Unique transitive closure computation for indirect causal paths
    """
    
    def __init__(
        self,
        hidden_size: int,
        n_variables: int,
        causal_dag: Optional['nx.DiGraph'] = None
    ):
        super(CausalRecurrenceGates, self).__init__()
        
        if not HAS_NETWORKX and causal_dag is not None:
            raise ImportError(
                "networkx is required for causal gates. "
                "Install with: pip install networkx"
            )
        
        self.hidden_size = hidden_size
        self.n_variables = n_variables
        
        # Compute causal mask from DAG
        if causal_dag is not None:
            self.register_buffer(
                'causal_mask',
                self._compute_causal_mask(causal_dag)
            )
        else:
            # Default: all variables can influence all others
            self.register_buffer(
                'causal_mask',
                torch.ones(n_variables, n_variables)
            )
    
    def _compute_causal_mask(self, dag: 'nx.DiGraph') -> torch.Tensor:
        """
        Compute causal mask from directed acyclic graph.
        
        For each pair (i, j), check if path exists from i to j using
        transitive closure to capture indirect causal relationships.
        """
        n = len(dag.nodes())
        mask = torch.zeros(n, n)
        
        # Self-influence: each variable influences itself
        for i in range(n):
            mask[i, i] = 1.0
        
        # Transitive closure for indirect causal paths
        # If i -> ... -> j in DAG, then i can influence j
        node_list = list(dag.nodes())
        for i, source in enumerate(node_list):
            for j, target in enumerate(node_list):
                if nx.has_path(dag, source, target):
                    mask[i, j] = 1.0
        
        return mask
    
    def apply_causal_mask(
        self,
        gate_inputs: torch.Tensor,
        variable_idx: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Apply causal mask to gate inputs.
        
        This method masks gate inputs to prevent non-causal information flow.
        Only variables with causal relationships in the DAG can influence
        each other's gate activations.
        
        Parameters
        ----------
        gate_inputs : torch.Tensor of shape (batch, seq_len, n_variables)
            Inputs to GRU gates (concatenation of h_{t-1} and x_t)
        variable_idx : torch.Tensor, optional
            Indices mapping features to DAG variables
        
        Returns
        -------
        masked_inputs : torch.Tensor
            Gate inputs with non-causal connections masked to zero
        """
        # Broadcast mask to match batch dimensions
        mask_expanded = self.causal_mask.unsqueeze(0)
        
        # Apply mask: zero out non-causal connections
        masked = gate_inputs.unsqueeze(-1) * mask_expanded
        
        # Sum over source variables
        masked_inputs = masked.sum(dim=-2)
        
        return masked_inputs
