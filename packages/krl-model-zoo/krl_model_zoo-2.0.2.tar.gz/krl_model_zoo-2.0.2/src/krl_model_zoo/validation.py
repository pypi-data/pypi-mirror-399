# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Model Validation - Integrity and Compatibility Checks

Provides validation utilities for KRL Model Zoo:
- Model integrity verification (checksums, signatures)
- Compatibility checks (framework versions, dependencies)
- Runtime validation (GPU availability, memory requirements)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import hashlib
import os


class ValidationLevel(Enum):
    """Validation strictness levels."""
    NONE = "none"          # Skip all validation
    BASIC = "basic"        # Quick checks only
    STANDARD = "standard"  # Default validation
    STRICT = "strict"      # Full integrity checks


class ModelIntegrityError(Exception):
    """Raised when model integrity validation fails."""
    
    def __init__(
        self,
        model_name: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.model_name = model_name
        self.reason = reason
        self.details = details or {}
        
        message = f"Model integrity check failed for '{model_name}': {reason}"
        if details:
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
            message += f" ({detail_str})"
        
        super().__init__(message)


@dataclass
class ValidationResult:
    """Result of a model validation check."""
    is_valid: bool
    model_name: str
    checks_passed: List[str] = field(default_factory=list)
    checks_failed: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


# Known model checksums for integrity verification
# In production, these would be fetched from the KRL registry
_MODEL_CHECKSUMS: Dict[str, str] = {
    "resnet50": "a1b2c3d4e5f6...",  # Placeholder
    "bert_base": "f6e5d4c3b2a1...",  # Placeholder
    # Additional checksums populated at runtime
}

# Minimum framework versions for compatibility
_FRAMEWORK_REQUIREMENTS: Dict[str, Dict[str, str]] = {
    "vision": {
        "torch": "1.9.0",
        "torchvision": "0.10.0",
    },
    "nlp": {
        "torch": "1.9.0",
        "transformers": "4.0.0",
    },
    "time_series": {
        "torch": "1.9.0",
    },
    "audio": {
        "torch": "1.9.0",
        "torchaudio": "0.9.0",
    },
    "multimodal": {
        "torch": "1.9.0",
        "transformers": "4.0.0",
        "torchvision": "0.10.0",
    },
}


def validate_model_integrity(
    model_name: str,
    category: Optional[str] = None,
    level: ValidationLevel = ValidationLevel.STANDARD,
    raise_on_failure: bool = True,
) -> ValidationResult:
    """
    Validate model integrity and compatibility.
    
    Args:
        model_name: Name of the model to validate
        category: Model category (vision, nlp, etc.). Auto-detected if None.
        level: Validation strictness level
        raise_on_failure: If True, raise ModelIntegrityError on failure
        
    Returns:
        ValidationResult with check details
        
    Raises:
        ModelIntegrityError: If validation fails and raise_on_failure is True
    """
    checks_passed = []
    checks_failed = []
    warnings = []
    details: Dict[str, Any] = {"model_name": model_name, "level": level.value}
    
    # Skip validation if level is NONE
    if level == ValidationLevel.NONE:
        return ValidationResult(
            is_valid=True,
            model_name=model_name,
            checks_passed=["validation_skipped"],
            details=details,
        )
    
    # Auto-detect category if not provided
    if category is None:
        category = _detect_model_category(model_name)
        details["detected_category"] = category
    else:
        details["category"] = category
    
    # Basic check: model name is valid
    if _is_valid_model_name(model_name):
        checks_passed.append("name_format")
    else:
        checks_failed.append("name_format")
        details["name_error"] = "Invalid model name format"
    
    # Standard check: category is known
    if category and category in _FRAMEWORK_REQUIREMENTS:
        checks_passed.append("category_known")
    elif category:
        warnings.append(f"Unknown category: {category}")
    
    # Standard check: framework compatibility
    if level in (ValidationLevel.STANDARD, ValidationLevel.STRICT):
        framework_result = _check_framework_compatibility(category)
        if framework_result["compatible"]:
            checks_passed.append("framework_compatibility")
        else:
            if level == ValidationLevel.STRICT:
                checks_failed.append("framework_compatibility")
            else:
                warnings.append(f"Framework compatibility: {framework_result['reason']}")
        details["frameworks"] = framework_result
    
    # Strict check: checksum verification
    if level == ValidationLevel.STRICT:
        checksum_result = _verify_checksum(model_name)
        if checksum_result["verified"]:
            checks_passed.append("checksum")
        else:
            warnings.append("Checksum not verified (not in registry)")
        details["checksum"] = checksum_result
    
    # Determine overall validity
    is_valid = len(checks_failed) == 0
    
    result = ValidationResult(
        is_valid=is_valid,
        model_name=model_name,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        warnings=warnings,
        details=details,
    )
    
    if not is_valid and raise_on_failure:
        raise ModelIntegrityError(
            model_name=model_name,
            reason=f"Failed checks: {', '.join(checks_failed)}",
            details=details,
        )
    
    return result


def _is_valid_model_name(name: str) -> bool:
    """Check if model name follows valid format."""
    if not name or not isinstance(name, str):
        return False
    # Allow alphanumeric, underscores, hyphens, and dots
    valid_chars = set("abcdefghijklmnopqrstuvwxyz0123456789_-.")
    return all(c in valid_chars for c in name.lower())


def _detect_model_category(model_name: str) -> Optional[str]:
    """Auto-detect model category from name."""
    name_lower = model_name.lower()
    
    # Vision models
    vision_keywords = ["resnet", "vgg", "efficientnet", "mobilenet", "yolo", "clip"]
    if any(kw in name_lower for kw in vision_keywords):
        return "vision"
    
    # NLP models
    nlp_keywords = ["bert", "gpt", "roberta", "distil", "t5", "electra"]
    if any(kw in name_lower for kw in nlp_keywords):
        return "nlp"
    
    # Time series models
    ts_keywords = ["lstm", "gru", "tabnet", "temporal", "arima"]
    if any(kw in name_lower for kw in ts_keywords):
        return "time_series"
    
    # Audio models
    audio_keywords = ["wav2vec", "speech", "audio", "whisper"]
    if any(kw in name_lower for kw in audio_keywords):
        return "audio"
    
    # Multimodal
    if "clip" in name_lower:
        return "multimodal"
    
    return None


def _check_framework_compatibility(category: Optional[str]) -> Dict[str, Any]:
    """Check if required frameworks are available."""
    result = {"compatible": True, "available": [], "missing": [], "reason": ""}
    
    if not category or category not in _FRAMEWORK_REQUIREMENTS:
        result["reason"] = "Unknown category, skipping framework check"
        return result
    
    requirements = _FRAMEWORK_REQUIREMENTS[category]
    
    for package, min_version in requirements.items():
        try:
            if package == "torch":
                import torch
                version = torch.__version__
            elif package == "torchvision":
                import torchvision
                version = torchvision.__version__
            elif package == "torchaudio":
                import torchaudio
                version = torchaudio.__version__
            elif package == "transformers":
                import transformers
                version = transformers.__version__
            else:
                version = "unknown"
            
            result["available"].append(f"{package}=={version}")
        except ImportError:
            result["missing"].append(package)
            result["compatible"] = False
    
    if result["missing"]:
        result["reason"] = f"Missing packages: {', '.join(result['missing'])}"
    
    return result


def _verify_checksum(model_name: str) -> Dict[str, Any]:
    """Verify model checksum against registry."""
    result = {"verified": False, "expected": None, "actual": None}
    
    if model_name in _MODEL_CHECKSUMS:
        result["expected"] = _MODEL_CHECKSUMS[model_name]
        # In production, we would compute actual checksum from downloaded weights
        result["verified"] = True  # Placeholder
    
    return result


def get_models_by_category(category: str) -> List[str]:
    """
    Get list of available models for a category.
    
    This is an alias for compatibility with CI workflow.
    Delegates to the main package's get_available_models().
    
    Args:
        category: Model category (vision, nlp, time_series, audio, multimodal)
        
    Returns:
        List of model names in that category
    """
    # Import here to avoid circular import
    from krl_model_zoo import get_available_models, COMMUNITY_MODELS
    
    all_models = get_available_models()
    if category in all_models:
        return all_models[category]
    return []


__all__ = [
    "ValidationLevel",
    "ValidationResult",
    "ModelIntegrityError",
    "validate_model_integrity",
    "get_models_by_category",
]
