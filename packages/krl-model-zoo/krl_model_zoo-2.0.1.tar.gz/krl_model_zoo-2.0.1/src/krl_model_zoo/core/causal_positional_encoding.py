# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Causal Positional Encoding for Transformer Networks - Professional Tier

PROPRIETARY: This module contains algorithms for encoding causal structure
into transformer positional embeddings using domain knowledge from directed
acyclic graphs.

Patent-Safe Strategy: Novel encoding method specific to multi-domain causal
analysis (33 KRL domains), distinct from standard sinusoidal encodings.
"""

import torch
import torch.nn as nn
import math
from typing import Optional, Dict, List
import numpy as np

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None


class CausalPositionalEncoding(nn.Module):
    """
    Causal positional encoding for Transformer networks.
    
    This implementation replaces standard sinusoidal positional encoding with
    a causal structure-aware encoding that incorporates domain knowledge from
    directed acyclic graphs (DAGs).
    
    Key Innovation: Instead of encoding only temporal position, we encode
    CAUSAL position - a variable's location in the causal graph, including
    its ancestors (causes) and descendants (effects).
    
    Algorithm:
    ----------
    For each variable v in DAG G = (V, E):
    
    1. Ancestor Path Encoding (sin components):
       PE_anc(v, 2i) = sin(depth_ancestors(v) / 10000^(2i/d_model))
       
    2. Descendant Path Encoding (cos components):
       PE_desc(v, 2i+1) = cos(depth_descendants(v) / 10000^(2i/d_model))
       
    3. Hub Penalty:
       PE_final(v) = PE(v) / (1 + hub_penalty_coef × out_degree(v))
       Prevents over-reliance on hub variables with high out-degree
    
    Parameters
    ----------
    d_model : int
        Dimension of the model (must be even)
    causal_dag : networkx.DiGraph, optional
        Directed acyclic graph encoding causal relationships
    variable_names : List[str], optional
        Ordered list of variable names matching DAG nodes
    max_len : int, default=5000
        Maximum sequence length for fallback temporal encoding
    dropout : float, default=0.1
        Dropout probability
    hub_penalty_coef : float, default=0.1
        Hub penalty coefficient for high out-degree nodes
    
    Notes
    -----
    Patent-Safe Strategy:
    - Domain-specific to multi-domain causal graphs (33 KRL domains)
    - Novel bidirectional encoding (ancestors/descendants)
    - Unique hub penalty mechanism
    - Optimized for causal discovery and econometric applications
    """
    
    def __init__(
        self,
        d_model: int,
        causal_dag: Optional['nx.DiGraph'] = None,
        variable_names: Optional[List[str]] = None,
        max_len: int = 5000,
        dropout: float = 0.1,
        hub_penalty_coef: float = 0.1
    ):
        super(CausalPositionalEncoding, self).__init__()
        
        if d_model % 2 != 0:
            raise ValueError(f"d_model must be even, got {d_model}")
        
        if not HAS_NETWORKX and causal_dag is not None:
            raise ImportError(
                "networkx is required for causal positional encoding. "
                "Install with: pip install networkx"
            )
        
        self.d_model = d_model
        self.dropout = nn.Dropout(p=dropout)
        self.hub_penalty_coef = hub_penalty_coef
        
        # If DAG provided, compute causal positional encoding
        if causal_dag is not None and variable_names is not None:
            self.use_causal = True
            self.variable_names = variable_names
            pe_causal = self._compute_causal_encoding(causal_dag)
            self.register_buffer('pe_causal', pe_causal)
        else:
            self.use_causal = False
            # Fallback to standard positional encoding
            pe_standard = self._compute_standard_encoding(max_len, d_model)
            self.register_buffer('pe_standard', pe_standard)
    
    def _compute_causal_encoding(self, dag: 'nx.DiGraph') -> torch.Tensor:
        """
        Compute causal positional encoding from DAG.
        
        Encodes each variable's causal position using:
        - Ancestor depth (sin components) - how far back causally
        - Descendant depth (cos components) - how far forward causally
        - Hub penalty - reduces weight for high out-degree nodes
        """
        n_vars = len(dag.nodes())
        pe = torch.zeros(n_vars, self.d_model)
        
        # Temperature scaling (standard transformer)
        div_term = torch.exp(
            torch.arange(0, self.d_model, 2).float() * 
            (-math.log(10000.0) / self.d_model)
        )
        
        for i, node in enumerate(self.variable_names):
            if node not in dag.nodes():
                # Variable not in DAG - use neutral encoding (all zeros)
                continue
            
            # Compute ancestor depth (causes)
            ancestors = list(nx.ancestors(dag, node))
            if ancestors:
                # Average depth of all ancestor paths
                anc_depths = [
                    nx.shortest_path_length(dag, ancestor, node)
                    for ancestor in ancestors
                ]
                anc_depth = float(np.mean(anc_depths))
            else:
                anc_depth = 0.0  # Root node (no causes)
            
            # Compute descendant depth (effects)
            descendants = list(nx.descendants(dag, node))
            if descendants:
                # Average depth of all descendant paths
                desc_depths = [
                    nx.shortest_path_length(dag, node, descendant)
                    for descendant in descendants
                ]
                desc_depth = float(np.mean(desc_depths))
            else:
                desc_depth = 0.0  # Leaf node (no effects)
            
            # Bidirectional encoding
            # Sin for ancestors (causes), cos for descendants (effects)
            pe[i, 0::2] = torch.sin(
                torch.tensor(anc_depth) * div_term
            )
            pe[i, 1::2] = torch.cos(
                torch.tensor(desc_depth) * div_term
            )
            
            # Hub penalty: prevent over-reliance on high out-degree variables
            out_degree = dag.out_degree(node)
            hub_penalty = 1.0 + self.hub_penalty_coef * out_degree
            pe[i, :] = pe[i, :] / hub_penalty
        
        # Add batch dimension: (n_vars, d_model) -> (1, n_vars, d_model)
        return pe.unsqueeze(0)
    
    def _compute_standard_encoding(self, max_len: int, d_model: int) -> torch.Tensor:
        """
        Fallback: Standard sinusoidal positional encoding (Vaswani et al. 2017).
        Used when no causal DAG is provided.
        """
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * 
            (-math.log(10000.0) / d_model)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        return pe.unsqueeze(0)  # Add batch dimension
    
    def forward(
        self,
        x: torch.Tensor,
        variable_idx: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Add causal positional encoding to input.
        
        Parameters
        ----------
        x : torch.Tensor of shape (batch_size, seq_len, d_model)
            Input tensor (after input projection)
        variable_idx : torch.Tensor, optional
            Indices mapping sequence positions to variables in DAG.
            Shape: (seq_len,) with values in [0, n_vars).
            If None and use_causal=True, assumes identity mapping.
        
        Returns
        -------
        torch.Tensor of shape (batch_size, seq_len, d_model)
            Input with causal positional encoding added
        """
        if self.use_causal:
            # Apply causal positional encoding
            seq_len = x.size(1)
            
            if variable_idx is not None:
                # Map variables to their causal positions
                pe = self.pe_causal[:, variable_idx, :]
            else:
                # Assume sequence corresponds to variable order
                if seq_len <= self.pe_causal.size(1):
                    pe = self.pe_causal[:, :seq_len, :]
                else:
                    # Pad with last encoding if sequence is longer
                    n_vars = self.pe_causal.size(1)
                    n_repeat = seq_len - n_vars
                    pe_last = self.pe_causal[:, -1:, :].repeat(1, n_repeat, 1)
                    pe = torch.cat([self.pe_causal, pe_last], dim=1)
            
            x = x + pe
        else:
            # Standard temporal positional encoding
            x = x + self.pe_standard[:, :x.size(1), :]
        
        return self.dropout(x)
    
    def get_causal_structure_info(self) -> Dict:
        """
        Get information about the encoded causal structure.
        
        Returns
        -------
        info : dict
            Causal structure metadata (for debugging/validation)
        """
        if not self.use_causal:
            return {'use_causal': False}
        
        return {
            'use_causal': True,
            'n_variables': len(self.variable_names),
            'variable_names': self.variable_names,
            'd_model': self.d_model,
            'hub_penalty_coef': self.hub_penalty_coef,
            'encoding_shape': tuple(self.pe_causal.shape)
        }
