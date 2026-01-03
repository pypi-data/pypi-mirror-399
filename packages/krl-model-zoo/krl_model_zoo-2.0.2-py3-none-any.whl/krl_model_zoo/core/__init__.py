# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Core neural network enhancements - Professional Tier

Proprietary enhancements for LSTM, GRU, and Transformer models:
- Equity-Weighted Attention: Fair predictions across demographics
- Causal Recurrence Gates: DAG-constrained recurrent gates
- Causal Positional Encoding: Graph-aware transformer encodings
"""

from krl_model_zoo.core.equity_attention import EquityWeightedAttention
from krl_model_zoo.core.causal_gates import CausalRecurrenceGates
from krl_model_zoo.core.causal_positional_encoding import CausalPositionalEncoding

__all__ = [
    'EquityWeightedAttention',
    'CausalRecurrenceGates',
    'CausalPositionalEncoding',
]
