# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Natural Language Processing Models - Community Tier

6 essential NLP models:
- BERT-base: Text encoding foundation model
- DistilBERT: Efficient BERT variant
- GPT-2 (small): Text generation
- Word2Vec: Word embeddings
- TextCNN: Text classification
- Sentiment-RoBERTa: Sentiment analysis
"""

from typing import Optional, List
import torch
import torch.nn as nn

def load_nlp_model(model_name: str, **kwargs):
    """
    Load an NLP model from Community tier.
    
    Args:
        model_name: One of: bert_base, distilbert, gpt2_small, word2vec,
                    textcnn, sentiment_roberta
        **kwargs: Model-specific configuration
            
    Returns:
        Model instance or transformers model
    """
    if model_name == "bert_base":
        return load_bert_base(**kwargs)
    elif model_name == "distilbert":
        return load_distilbert(**kwargs)
    elif model_name == "gpt2_small":
        return load_gpt2_small(**kwargs)
    elif model_name == "word2vec":
        return load_word2vec(**kwargs)
    elif model_name == "textcnn":
        return load_textcnn(**kwargs)
    elif model_name == "sentiment_roberta":
        return load_sentiment_roberta(**kwargs)
    else:
        raise ValueError(f"Unknown NLP model: {model_name}")

def load_bert_base(**kwargs):
    """Load BERT-base for text encoding."""
    try:
        from transformers import BertModel, BertTokenizer
    except ImportError:
        raise ImportError("Please install transformers: pip install transformers")
    
    model_name = "bert-base-uncased"
    model = BertModel.from_pretrained(model_name)
    tokenizer = BertTokenizer.from_pretrained(model_name)
    
    return {"model": model, "tokenizer": tokenizer}

def load_distilbert(**kwargs):
    """Load DistilBERT for efficient text encoding."""
    try:
        from transformers import DistilBertModel, DistilBertTokenizer
    except ImportError:
        raise ImportError("Please install transformers: pip install transformers")
    
    model_name = "distilbert-base-uncased"
    model = DistilBertModel.from_pretrained(model_name)
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    
    return {"model": model, "tokenizer": tokenizer}

def load_gpt2_small(**kwargs):
    """Load GPT-2 (small) for text generation."""
    try:
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
    except ImportError:
        raise ImportError("Please install transformers: pip install transformers")
    
    model_name = "gpt2"  # small variant
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    return {"model": model, "tokenizer": tokenizer}

def load_word2vec(vector_size: int = 100, window: int = 5, min_count: int = 1, **kwargs):
    """
    Load Word2Vec for word embeddings.
    
    Note: This returns an untrained model. Train with:
        model.build_vocab(sentences)
        model.train(sentences, total_examples=len(sentences), epochs=10)
    """
    try:
        from gensim.models import Word2Vec
    except ImportError:
        raise ImportError("Please install gensim: pip install gensim")
    
    model = Word2Vec(
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=4,
        **kwargs
    )
    
    return model

def load_textcnn(
    vocab_size: int = 10000,
    embed_dim: int = 300,
    num_classes: int = 2,
    kernel_sizes: List[int] = [3, 4, 5],
    num_filters: int = 100,
    dropout: float = 0.5,
    **kwargs
):
    """Load TextCNN for text classification."""
    
    class TextCNN(nn.Module):
        def __init__(self, vocab_size, embed_dim, num_classes, kernel_sizes, num_filters, dropout):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, embed_dim)
            
            # Multiple convolutional layers with different kernel sizes
            self.convs = nn.ModuleList([
                nn.Conv2d(1, num_filters, (k, embed_dim)) 
                for k in kernel_sizes
            ])
            
            self.dropout = nn.Dropout(dropout)
            self.fc = nn.Linear(len(kernel_sizes) * num_filters, num_classes)
        
        def forward(self, x):
            # x: (batch_size, seq_len)
            x = self.embedding(x)  # (batch_size, seq_len, embed_dim)
            x = x.unsqueeze(1)  # (batch_size, 1, seq_len, embed_dim)
            
            # Apply convolutions and max pooling
            conv_outputs = []
            for conv in self.convs:
                conv_out = torch.relu(conv(x).squeeze(3))  # (batch_size, num_filters, seq_len - k + 1)
                pooled = torch.max_pool1d(conv_out, conv_out.size(2)).squeeze(2)  # (batch_size, num_filters)
                conv_outputs.append(pooled)
            
            # Concatenate outputs from all conv layers
            x = torch.cat(conv_outputs, 1)  # (batch_size, len(kernel_sizes) * num_filters)
            x = self.dropout(x)
            logits = self.fc(x)  # (batch_size, num_classes)
            
            return logits
    
    model = TextCNN(vocab_size, embed_dim, num_classes, kernel_sizes, num_filters, dropout)
    return model

def load_sentiment_roberta(**kwargs):
    """Load Sentiment-RoBERTa for sentiment analysis."""
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError:
        raise ImportError("Please install transformers: pip install transformers")
    
    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    return {"model": model, "tokenizer": tokenizer}

__all__ = [
    "load_nlp_model",
    "load_bert_base",
    "load_distilbert",
    "load_gpt2_small",
    "load_word2vec",
    "load_textcnn",
    "load_sentiment_roberta"
]
