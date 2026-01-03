# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Tier Guard - Access Control for KRL Model Zoo

Provides tier-based access control for model loading:
- Community Tier: 20 open-source base models (FREE)
- Professional Tier: Core neural enhancements (API key)
- Enterprise Tier: Full stack + causal analysis (License)
"""

from enum import Enum
from typing import Optional
import os


class ModelTier(Enum):
    """Model access tier levels."""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TierAccessDeniedError(Exception):
    """Raised when access to a tier-protected resource is denied."""
    
    def __init__(
        self,
        required_tier: ModelTier,
        current_tier: Optional[ModelTier] = None,
        message: Optional[str] = None,
    ):
        self.required_tier = required_tier
        self.current_tier = current_tier or ModelTier.COMMUNITY
        
        if message is None:
            message = (
                f"Access denied. Required tier: {required_tier.value}, "
                f"current tier: {self.current_tier.value}. "
                f"Upgrade your subscription to access this feature."
            )
        super().__init__(message)


class TierGuard:
    """
    Tier-based access control guard.
    
    Usage:
        guard = TierGuard()
        guard.require_tier(ModelTier.PROFESSIONAL)  # Raises if not authorized
        
        # Or check without raising:
        if guard.has_tier(ModelTier.ENTERPRISE):
            # Use enterprise features
            pass
    """
    
    # Tier hierarchy (higher index = more access)
    _TIER_HIERARCHY = [ModelTier.COMMUNITY, ModelTier.PROFESSIONAL, ModelTier.ENTERPRISE]
    
    def __init__(self, api_key: Optional[str] = None, license_key: Optional[str] = None):
        """
        Initialize tier guard.
        
        Args:
            api_key: Professional tier API key (or from KRL_API_KEY env var)
            license_key: Enterprise tier license (or from KRL_LICENSE_KEY env var)
        """
        self._api_key = api_key or os.environ.get("KRL_API_KEY")
        self._license_key = license_key or os.environ.get("KRL_LICENSE_KEY")
        self._validated_tier: Optional[ModelTier] = None
    
    @property
    def current_tier(self) -> ModelTier:
        """Get the current validated tier level."""
        if self._validated_tier is not None:
            return self._validated_tier
        
        # Validate and cache tier
        self._validated_tier = self._resolve_tier()
        return self._validated_tier
    
    def _resolve_tier(self) -> ModelTier:
        """Resolve the current tier based on credentials."""
        if self._license_key and self._validate_license(self._license_key):
            return ModelTier.ENTERPRISE
        elif self._api_key and self._validate_api_key(self._api_key):
            return ModelTier.PROFESSIONAL
        else:
            return ModelTier.COMMUNITY
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate a Professional tier API key.
        
        In production, this would call the KRL license server.
        For now, we accept any non-empty key with proper format.
        """
        if not api_key or len(api_key) < 16:
            return False
        # Format: krl_pro_<32hex>
        if api_key.startswith("krl_pro_") and len(api_key) >= 40:
            return True
        # Also accept legacy format
        return len(api_key) >= 32
    
    def _validate_license(self, license_key: str) -> bool:
        """
        Validate an Enterprise tier license key.
        
        In production, this would call the KRL license server.
        For now, we accept any non-empty key with proper format.
        """
        if not license_key or len(license_key) < 32:
            return False
        # Format: krl_ent_<64hex>
        if license_key.startswith("krl_ent_") and len(license_key) >= 72:
            return True
        # Also accept legacy format
        return len(license_key) >= 64
    
    def has_tier(self, tier: ModelTier) -> bool:
        """
        Check if current access level meets or exceeds the required tier.
        
        Args:
            tier: Required tier level
            
        Returns:
            True if access is granted
        """
        current_idx = self._TIER_HIERARCHY.index(self.current_tier)
        required_idx = self._TIER_HIERARCHY.index(tier)
        return current_idx >= required_idx
    
    def require_tier(self, tier: ModelTier) -> None:
        """
        Require a specific tier level, raising if not authorized.
        
        Args:
            tier: Required tier level
            
        Raises:
            TierAccessDeniedError: If current tier is insufficient
        """
        if not self.has_tier(tier):
            raise TierAccessDeniedError(
                required_tier=tier,
                current_tier=self.current_tier,
            )
    
    def refresh(self) -> ModelTier:
        """
        Re-validate tier credentials (e.g., if env vars changed).
        
        Returns:
            The newly validated tier level
        """
        self._api_key = os.environ.get("KRL_API_KEY")
        self._license_key = os.environ.get("KRL_LICENSE_KEY")
        self._validated_tier = None
        return self.current_tier


# Global singleton for convenience
_default_guard: Optional[TierGuard] = None


def get_tier_guard() -> TierGuard:
    """Get the default global TierGuard instance."""
    global _default_guard
    if _default_guard is None:
        _default_guard = TierGuard()
    return _default_guard


def require_tier(tier: ModelTier) -> None:
    """Convenience function to require a tier using the default guard."""
    get_tier_guard().require_tier(tier)


def get_current_tier() -> ModelTier:
    """Convenience function to get current tier using the default guard."""
    return get_tier_guard().current_tier


__all__ = [
    "ModelTier",
    "TierGuard",
    "TierAccessDeniedError",
    "get_tier_guard",
    "require_tier",
    "get_current_tier",
]
