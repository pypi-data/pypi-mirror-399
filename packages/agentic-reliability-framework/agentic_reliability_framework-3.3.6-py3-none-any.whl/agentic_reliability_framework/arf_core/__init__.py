"""
ARF Core Module - OSS Edition
Production-grade multi-agent AI for reliability monitoring
OSS Edition: Advisory mode only, Apache 2.0 Licensed

IMPORTANT: This module ONLY exports OSS components - no circular imports
"""

__version__ = "3.3.5"  # Updated to match package version
__all__ = [
    "HealingIntent",
    "HealingIntentSerializer",
    "create_rollback_intent",
    "create_restart_intent",
    "create_scale_out_intent",
    "OSSMCPClient",
    "create_mcp_client",
    "OSS_EDITION",
    "OSS_LICENSE",
    "EXECUTION_ALLOWED",
    "MCP_MODES_ALLOWED",
    "OSSBoundaryError",
]

# ============================================================================
# DIRECT IMPORTS - RESOLVE CIRCULAR DEPENDENCIES
# ============================================================================

# Import from absolute paths to avoid circular imports
from agentic_reliability_framework.arf_core.models.healing_intent import (
    HealingIntent,
    HealingIntentSerializer,
    create_rollback_intent,
    create_restart_intent,
    create_scale_out_intent,
)

from agentic_reliability_framework.arf_core.constants import (
    OSS_EDITION,
    OSS_LICENSE,
    EXECUTION_ALLOWED,
    MCP_MODES_ALLOWED,
    OSSBoundaryError,
)

# Lazy load OSSMCPClient to avoid circular dependencies
_oss_mcp_client_class = None

def _get_oss_mcp_client_class():
    """Dynamically import OSSMCPClient on first use with proper fallback"""
    global _oss_mcp_client_class
    if _oss_mcp_client_class is not None:
        return _oss_mcp_client_class
    
    try:
        # Try simple_mcp_client first (avoids circular imports)
        from agentic_reliability_framework.arf_core.engine.simple_mcp_client import OSSMCPClient
        _oss_mcp_client_class = OSSMCPClient
    except ImportError as e1:
        try:
            # Fall back to full oss_mcp_client
            from agentic_reliability_framework.arf_core.engine.oss_mcp_client import OSSMCPClient
            _oss_mcp_client_class = OSSMCPClient
        except ImportError as e2:
            # Create minimal fallback class (instead of None)
            class MinimalOSSMCPClient:
                def __init__(self, config=None):
                    self.mode = "advisory"
                    self.config = config or {}
                
                async def execute_tool(self, request_dict):
                    return {
                        "request_id": request_dict.get("request_id", "oss-request"),
                        "status": "advisory",
                        "message": f"Advisory analysis for {request_dict.get('tool', 'unknown')}",
                        "executed": False,
                        "result": {
                            "mode": "advisory",
                            "requires_enterprise": True,
                            "upgrade_url": "https://arf.dev/enterprise"
                        }
                    }
                
                def get_client_stats(self):
                    return {
                        "mode": "advisory",
                        "oss_edition": True,
                        "can_execute": False,
                        "can_advise": True,
                        "enterprise_upgrade_available": True
                    }
            
            _oss_mcp_client_class = MinimalOSSMCPClient
    
    return _oss_mcp_client_class

def __getattr__(name):
    """Lazy loading for OSSMCPClient"""
    if name == "OSSMCPClient":
        return _get_oss_mcp_client_class()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def create_mcp_client(config=None):
    """Factory function for OSSMCPClient"""
    OSSMCPClientClass = _get_oss_mcp_client_class()
    return OSSMCPClientClass(config=config)

# Export OSSMCPClient for static analysis (with fallback)
try:
    OSSMCPClient = _get_oss_mcp_client_class()
except Exception:
    # This should never happen due to the fallback above
    OSSMCPClient = None

# ============================================================================
# MODULE METADATA
# ============================================================================

ENTERPRISE_UPGRADE_URL = "https://arf.dev/enterprise"
