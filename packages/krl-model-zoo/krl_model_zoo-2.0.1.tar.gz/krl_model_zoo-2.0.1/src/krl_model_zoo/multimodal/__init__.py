# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Multimodal Models - Community Tier

1 essential multimodal model:
- CLIP (ViT-B/32): Vision-language understanding
"""

def load_multimodal_model(model_name: str, **kwargs):
    """
    Load a multimodal model from Community tier.
    
    Args:
        model_name: Currently only: clip_vit_b32
        **kwargs: Model-specific configuration
            
    Returns:
        Model instance and processor
    """
    if model_name == "clip_vit_b32":
        return load_clip_vit_b32(**kwargs)
    else:
        raise ValueError(f"Unknown multimodal model: {model_name}")

def load_clip_vit_b32(**kwargs):
    """
    Load CLIP (ViT-B/32) for vision-language understanding.
    
    CLIP can perform:
    - Zero-shot image classification
    - Image-text similarity
    - Text-to-image retrieval
    - Image-to-text retrieval
    
    Returns:
        Dict with 'model' and 'processor' keys
    """
    try:
        from transformers import CLIPModel, CLIPProcessor
    except ImportError:
        raise ImportError("Please install transformers: pip install transformers")
    
    model_name = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    return {"model": model, "processor": processor}

__all__ = [
    "load_multimodal_model",
    "load_clip_vit_b32"
]
