# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Audio & Speech Models - Community Tier

2 essential audio models:
- Wav2Vec2-base: Speech recognition foundation model
- SpeechBrain-ASR: End-to-end speech-to-text
"""

def load_audio_model(model_name: str, **kwargs):
    """
    Load an audio model from Community tier.
    
    Args:
        model_name: One of: wav2vec2_base, speechbrain_asr
        **kwargs: Model-specific configuration
            
    Returns:
        Model instance or pipeline
    """
    if model_name == "wav2vec2_base":
        return load_wav2vec2_base(**kwargs)
    elif model_name == "speechbrain_asr":
        return load_speechbrain_asr(**kwargs)
    else:
        raise ValueError(f"Unknown audio model: {model_name}")

def load_wav2vec2_base(**kwargs):
    """Load Wav2Vec2-base for speech recognition."""
    try:
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
    except ImportError:
        raise ImportError("Please install transformers: pip install transformers")
    
    model_name = "facebook/wav2vec2-base-960h"
    processor = Wav2Vec2Processor.from_pretrained(model_name)
    model = Wav2Vec2ForCTC.from_pretrained(model_name)
    
    return {"model": model, "processor": processor}

def load_speechbrain_asr(**kwargs):
    """
    Load SpeechBrain ASR for speech-to-text.
    
    Note: This requires the speechbrain library.
    Install with: pip install speechbrain
    """
    try:
        from speechbrain.pretrained import EncoderDecoderASR
    except ImportError:
        raise ImportError(
            "Please install speechbrain: pip install speechbrain\n"
            "Or use wav2vec2_base for speech recognition"
        )
    
    # Load pre-trained model
    asr_model = EncoderDecoderASR.from_hparams(
        source="speechbrain/asr-crdnn-rnnlm-librispeech",
        savedir="pretrained_models/asr-crdnn-rnnlm-librispeech"
    )
    
    return asr_model

__all__ = [
    "load_audio_model",
    "load_wav2vec2_base",
    "load_speechbrain_asr"
]
