"""
Model Router and Infrastructure Package
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer
"""

from .registry_manager import (
    ModelRegistryManager,
    RegistryValidationError,
    ModelNotFoundError,
    VersionRollbackError,
)
from .provenance import (
    ProvenanceVerifier,
    TamperedModelWeightError,
)
from .fallback_policy import (
    FallbackPolicy,
    FallbackPolicyEngine,
    FallbackEvent,
    FallbackExhaustedError,
)
from .cascade import (
    ModelCascader,
    CascadeResult,
)
from .adapters import (
    BaseModelAdapter,
    ModelResponse,
    ToolCallRequest,
    TokenUsage,
    HealthStatus,
    ModelInferenceError,
    OutOfMemoryError,
    ModelUnavailableError,
    VLLMAdapter,
    OllamaAdapter,
    LlamaCppAdapter,
    MockAdapter,
    create_adapter,
)

__all__ = [
    "ModelRegistryManager",
    "RegistryValidationError",
    "ModelNotFoundError",
    "VersionRollbackError",
    "ProvenanceVerifier",
    "TamperedModelWeightError",
    "FallbackPolicy",
    "FallbackPolicyEngine",
    "FallbackEvent",
    "FallbackExhaustedError",
    "ModelCascader",
    "CascadeResult",
    "BaseModelAdapter",
    "ModelResponse",
    "ToolCallRequest",
    "TokenUsage",
    "HealthStatus",
    "ModelInferenceError",
    "OutOfMemoryError",
    "ModelUnavailableError",
    "VLLMAdapter",
    "OllamaAdapter",
    "LlamaCppAdapter",
    "MockAdapter",
    "create_adapter",
]
