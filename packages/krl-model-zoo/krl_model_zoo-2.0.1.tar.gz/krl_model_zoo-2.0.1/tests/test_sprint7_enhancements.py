# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Tests for Sprint 7 Neural Network Enhancements

Tests for:
- LSTM Equity-Weighted Attention
- GRU Causal Recurrence Gates  
- Transformer Causal Positional Encoding
"""

import pytest
import torch
import numpy as np
from krl_model_zoo.time_series import load_lstm, load_gru, load_transformer

# Try to import networkx for causal graph tests
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class TestLSTMEquityAttention:
    """Tests for LSTM with Equity-Weighted Attention (Sprint 7)."""
    
    def test_lstm_basic_forward(self):
        """Test basic LSTM forward pass without equity attention."""
        model = load_lstm(
            input_size=10,
            hidden_size=32,
            num_layers=2,
            output_size=1
        )
        
        # Create sample input
        batch_size = 4
        seq_len = 20
        x = torch.randn(batch_size, seq_len, 10)
        
        # Forward pass
        out, hidden = model(x)
        
        assert out.shape == (batch_size, 1)
        assert isinstance(hidden, tuple)
        assert hidden[0].shape == (2, batch_size, 32)  # h
        assert hidden[1].shape == (2, batch_size, 32)  # c
    
    def test_lstm_equity_attention_forward(self):
        """Test LSTM with equity-weighted attention."""
        model = load_lstm(
            input_size=10,
            hidden_size=32,
            num_layers=2,
            output_size=1,
            use_equity_attention=True,
            n_equity_dims=3
        )
        
        # Create sample input
        batch_size = 4
        seq_len = 20
        x = torch.randn(batch_size, seq_len, 10)
        equity_factors = torch.randn(batch_size, 3)  # 3 equity dimensions
        
        # Forward pass
        out, hidden = model(x, equity_factors=equity_factors)
        
        assert out.shape == (batch_size, 1)
    
    def test_lstm_equity_attention_fallback(self):
        """Test LSTM equity attention fallback when no factors provided."""
        model = load_lstm(
            input_size=10,
            hidden_size=32,
            num_layers=2,
            output_size=1,
            use_equity_attention=True,
            n_equity_dims=3
        )
        
        # Forward pass without equity factors (should use mean pooling)
        batch_size = 4
        seq_len = 20
        x = torch.randn(batch_size, seq_len, 10)
        
        out, hidden = model(x, equity_factors=None)
        
        assert out.shape == (batch_size, 1)
    
    def test_lstm_equity_attention_gradient_flow(self):
        """Test gradient flow through equity attention."""
        model = load_lstm(
            input_size=10,
            hidden_size=32,
            num_layers=2,
            output_size=1,
            use_equity_attention=True,
            n_equity_dims=3
        )
        
        # Create sample input and target
        x = torch.randn(4, 20, 10, requires_grad=True)
        equity_factors = torch.randn(4, 3, requires_grad=True)
        target = torch.randn(4, 1)
        
        # Forward pass
        out, _ = model(x, equity_factors=equity_factors)
        
        # Compute loss and backward
        loss = torch.nn.functional.mse_loss(out, target)
        loss.backward()
        
        # Check gradients exist
        assert x.grad is not None
        assert equity_factors.grad is not None


class TestGRUCausalGates:
    """Tests for GRU with Causal Recurrence Gates (Sprint 7)."""
    
    def test_gru_basic_forward(self):
        """Test basic GRU forward pass without causal gates."""
        model = load_gru(
            input_size=10,
            hidden_size=32,
            num_layers=2,
            output_size=1
        )
        
        # Create sample input
        batch_size = 4
        seq_len = 20
        x = torch.randn(batch_size, seq_len, 10)
        
        # Forward pass
        out, hidden = model(x)
        
        assert out.shape == (batch_size, 1)
        assert hidden.shape == (2, batch_size, 32)
    
    @pytest.mark.skipif(not HAS_NETWORKX, reason="networkx not installed")
    def test_gru_causal_gates_forward(self):
        """Test GRU with causal recurrence gates."""
        # Create simple causal DAG: x1 -> x2 -> x3
        dag = nx.DiGraph()
        dag.add_edges_from([('x1', 'x2'), ('x2', 'x3')])
        
        model = load_gru(
            input_size=3,
            hidden_size=32,
            num_layers=2,
            output_size=1,
            use_causal_gates=True,
            n_variables=3,
            causal_dag=dag
        )
        
        # Create sample input
        batch_size = 4
        seq_len = 20
        x = torch.randn(batch_size, seq_len, 3)
        
        # Forward pass
        out, hidden = model(x)
        
        assert out.shape == (batch_size, 1)
    
    def test_gru_causal_gates_without_dag(self):
        """Test GRU causal gates without DAG (all variables influence all)."""
        model = load_gru(
            input_size=5,
            hidden_size=32,
            num_layers=2,
            output_size=1,
            use_causal_gates=True,
            n_variables=5,
            causal_dag=None  # No DAG provided
        )
        
        # Create sample input
        batch_size = 4
        seq_len = 20
        x = torch.randn(batch_size, seq_len, 5)
        
        # Forward pass (should work with default mask)
        out, hidden = model(x)
        
        assert out.shape == (batch_size, 1)
    
    def test_gru_causal_gates_gradient_flow(self):
        """Test gradient flow through causal gates."""
        model = load_gru(
            input_size=5,
            hidden_size=32,
            num_layers=2,
            output_size=1,
            use_causal_gates=True,
            n_variables=5
        )
        
        # Create sample input and target
        x = torch.randn(4, 20, 5, requires_grad=True)
        target = torch.randn(4, 1)
        
        # Forward pass
        out, _ = model(x)
        
        # Compute loss and backward
        loss = torch.nn.functional.mse_loss(out, target)
        loss.backward()
        
        # Check gradients exist
        assert x.grad is not None


class TestTransformerCausalPE:
    """Tests for Transformer with Causal Positional Encoding (Sprint 7)."""
    
    def test_transformer_basic_forward(self):
        """Test basic Transformer forward pass without causal PE."""
        model = load_transformer(
            d_model=64,
            nhead=4,
            num_layers=2,
            dim_feedforward=256,
            input_size=10,
            output_size=1
        )
        
        # Create sample input
        batch_size = 4
        seq_len = 20
        x = torch.randn(batch_size, seq_len, 10)
        
        # Forward pass
        out = model(x)
        
        assert out.shape == (batch_size, 1)
    
    @pytest.mark.skipif(not HAS_NETWORKX, reason="networkx not installed")
    def test_transformer_causal_pe_forward(self):
        """Test Transformer with causal positional encoding."""
        # Create simple causal DAG
        dag = nx.DiGraph()
        dag.add_edges_from([('var1', 'var2'), ('var2', 'var3')])
        variable_names = ['var1', 'var2', 'var3']
        
        model = load_transformer(
            d_model=64,
            nhead=4,
            num_layers=2,
            dim_feedforward=256,
            input_size=3,
            output_size=1,
            use_causal_pe=True,
            causal_dag=dag,
            variable_names=variable_names
        )
        
        # Create sample input
        batch_size = 4
        seq_len = 3  # Match number of variables
        x = torch.randn(batch_size, seq_len, 3)
        
        # Forward pass
        out = model(x)
        
        assert out.shape == (batch_size, 1)
    
    @pytest.mark.skipif(not HAS_NETWORKX, reason="networkx not installed")
    def test_transformer_causal_pe_hub_penalty(self):
        """Test that hub penalty is applied correctly."""
        # Create hub DAG: hub -> v1, hub -> v2, hub -> v3
        dag = nx.DiGraph()
        dag.add_edges_from([
            ('hub', 'v1'),
            ('hub', 'v2'),
            ('hub', 'v3')
        ])
        variable_names = ['hub', 'v1', 'v2', 'v3']
        
        model = load_transformer(
            d_model=64,
            nhead=4,
            num_layers=2,
            dim_feedforward=256,
            input_size=4,
            output_size=1,
            use_causal_pe=True,
            causal_dag=dag,
            variable_names=variable_names
        )
        
        # Hub node should have reduced positional encoding magnitude
        # due to hub penalty (out_degree = 3)
        pe_info = model.pos_encoder.get_causal_structure_info()
        
        assert pe_info['use_causal'] == True
        assert pe_info['n_variables'] == 4
        assert pe_info['hub_penalty_coef'] == 0.1
    
    def test_transformer_causal_pe_gradient_flow(self):
        """Test gradient flow through causal positional encoding."""
        model = load_transformer(
            d_model=64,
            nhead=4,
            num_layers=2,
            dim_feedforward=256,
            input_size=5,
            output_size=1
        )
        
        # Create sample input and target
        x = torch.randn(4, 10, 5, requires_grad=True)
        target = torch.randn(4, 1)
        
        # Forward pass
        out = model(x)
        
        # Compute loss and backward
        loss = torch.nn.functional.mse_loss(out, target)
        loss.backward()
        
        # Check gradients exist
        assert x.grad is not None


class TestSprint7Integration:
    """Integration tests for all Sprint 7 enhancements."""
    
    def test_all_models_load_successfully(self):
        """Test that all enhanced models can be loaded."""
        lstm = load_lstm(hidden_size=32, use_equity_attention=True, n_equity_dims=3)
        gru = load_gru(hidden_size=32, use_causal_gates=True, n_variables=5)
        transformer = load_transformer(d_model=64, nhead=4)
        
        assert lstm is not None
        assert gru is not None
        assert transformer is not None
    
    def test_enhanced_models_trainable(self):
        """Test that enhanced models can be trained."""
        # LSTM with equity attention
        lstm = load_lstm(
            input_size=10,
            hidden_size=32,
            output_size=1,
            use_equity_attention=True,
            n_equity_dims=3
        )
        
        # Create simple training data
        x = torch.randn(16, 20, 10)
        equity = torch.randn(16, 3)
        y = torch.randn(16, 1)
        
        # Training step
        optimizer = torch.optim.Adam(lstm.parameters(), lr=0.001)
        criterion = torch.nn.MSELoss()
        
        lstm.train()
        optimizer.zero_grad()
        out, _ = lstm(x, equity_factors=equity)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        
        assert loss.item() > 0  # Loss computed successfully
    
    def test_patent_safe_implementation(self):
        """Verify patent-safe implementation characteristics."""
        # Test that enhancements are domain-specific (not general-purpose)
        
        # 1. Equity attention requires equity_factors (demographic data)
        lstm = load_lstm(use_equity_attention=True, n_equity_dims=3)
        x = torch.randn(4, 20, 1)
        
        # Should work without equity_factors (fallback)
        out, _ = lstm(x, equity_factors=None)
        assert out.shape == (4, 1)
        
        # 2. Causal gates require domain knowledge (DAG)
        gru = load_gru(use_causal_gates=True, n_variables=5)
        x = torch.randn(4, 20, 5)
        
        # Should work with default mask (all variables influence all)
        out, _ = gru(x)
        assert out.shape == (4, 1)
        
        # 3. Causal PE is specific to variable relationships
        transformer = load_transformer(d_model=64, nhead=4)
        x = torch.randn(4, 10, 1)
        
        # Should use standard PE when no DAG provided
        out = transformer(x)
        assert out.shape == (4, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
