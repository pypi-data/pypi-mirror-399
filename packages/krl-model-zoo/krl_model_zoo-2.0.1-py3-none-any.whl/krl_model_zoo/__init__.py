"""
KRL Model Zoo v2.0 - Community Tier

Open-source deep learning models for vision, NLP, time series, audio, and multimodal tasks.

Community Tier includes 20 essential models:
- 8 Computer Vision models
- 6 NLP models
- 3 Time Series models
- 2 Audio models
- 1 Multimodal model

For more models, upgrade to:
- Professional Tier: 65 models ($49/month)
- Enterprise Tier: 105 models ($299/month)

© 2025 KR-Labs. All rights reserved.
"""

__version__ = "2.0.1"
__author__ = "KR-Labs Team"
__email__ = "info@krlabs.dev"
__license__ = "Apache-2.0"

# Community Tier Model Registry
COMMUNITY_MODELS = {
    "vision": [
        "resnet50",
        "mobilenetv2", 
        "efficientnet_b0",
        "yolov5s",
        "faster_rcnn",
        "unet",
        "deeplabv3",
        "openpose"
    ],
    "nlp": [
        "bert_base",
        "distilbert",
        "gpt2_small",
        "word2vec",
        "textcnn",
        "sentiment_roberta"
    ],
    "time_series": [
        "lstm",
        "gru", 
        "tabnet"
    ],
    "audio": [
        "wav2vec2_base",
        "speechbrain_asr"
    ],
    "multimodal": [
        "clip_vit_b32"
    ]
}

def get_available_models():
    """Get list of all available models in Community tier."""
    all_models = []
    for category, models in COMMUNITY_MODELS.items():
        all_models.extend([f"{category}.{model}" for model in models])
    return sorted(all_models)

def load_model(model_name: str, **kwargs):
    """
    Load a model from the Community tier.
    
    Args:
        model_name: Model name in format "category.model" (e.g., "vision.resnet50")
        **kwargs: Model-specific configuration
        
    Returns:
        Loaded model instance
        
    Examples:
        >>> from krl_model_zoo import load_model
        >>> model = load_model("vision.resnet50", pretrained=True)
        >>> model = load_model("nlp.bert_base", num_classes=3)
        >>> model = load_model("multimodal.clip_vit_b32")
    """
    if "." not in model_name:
        raise ValueError(
            f"Model name must be in format 'category.model', got: {model_name}\n"
            f"Available models: {get_available_models()}"
        )
    
    category, model = model_name.split(".", 1)
    
    if category not in COMMUNITY_MODELS:
        raise ValueError(
            f"Unknown category: {category}\n"
            f"Available categories: {list(COMMUNITY_MODELS.keys())}"
        )
    
    if model not in COMMUNITY_MODELS[category]:
        raise ValueError(
            f"Unknown model '{model}' in category '{category}'\n"
            f"Available models in {category}: {COMMUNITY_MODELS[category]}"
        )
    
    # Import and return model
    if category == "vision":
        from .vision import load_vision_model
        return load_vision_model(model, **kwargs)
    elif category == "nlp":
        from .nlp import load_nlp_model
        return load_nlp_model(model, **kwargs)
    elif category == "time_series":
        from .time_series import load_time_series_model
        return load_time_series_model(model, **kwargs)
    elif category == "audio":
        from .audio import load_audio_model
        return load_audio_model(model, **kwargs)
    elif category == "multimodal":
        from .multimodal import load_multimodal_model
        return load_multimodal_model(model, **kwargs)
    else:
        raise ValueError(f"Category not implemented: {category}")

__all__ = [
    "__version__",
    "COMMUNITY_MODELS",
    "get_available_models",
    "load_model",
]

# Environment checker utility (for diagnostics)
# Users can run: python -m krl_model_zoo.env_check
