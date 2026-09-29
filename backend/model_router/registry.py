"""
Model Registry management for Sovereign Workbench.
Loads, validates, and manages pluggable local models.
"""

from typing import Dict, List, Optional
import os
import yaml
from pydantic import BaseModel, Field
from model_router.adapters.base import ModelAdapter, MockLocalAdapter


class ModelMetadata(BaseModel):
    id: str
    name: str
    capabilities: List[str]
    context_window: int = 16384
    adapter_type: str = "vllm"
    quantization: str = "none"
    priority: int = 1
    vram_required_gb: int = 0
    status: str = "active"
    fallback_targets: List[str] = Field(default_factory=list)


class ModelRegistry:
    """Manages models, dynamic capability queries, and runtime adapter instances."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default to model_registry.yaml in same directory
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(cur_dir, "model_registry.yaml")

        self.config_path = config_path
        self.version: str = "2.0"
        self.default_confidence_threshold: float = 0.65
        self.models: Dict[str, ModelMetadata] = {}
        self._adapters: Dict[str, ModelAdapter] = {}
        self.load()

    def load(self):
        """Loads and parses model_registry.yaml."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Model registry file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.version = data.get("version", "2.0")
        self.default_confidence_threshold = float(data.get("default_router_confidence_threshold", 0.65))

        self.models.clear()
        raw_models = data.get("models", {})
        if isinstance(raw_models, dict):
            for mid, mdata in raw_models.items():
                capabilities = mdata.get("strengths", mdata.get("capabilities", []))
                # Map coding / sop_qa to code / reasoning
                if "coding" in capabilities and "code" not in capabilities:
                    capabilities.append("code")
                if "sop_qa" in capabilities and "reasoning" not in capabilities:
                    capabilities.append("reasoning")
                if "vision_ocr" in capabilities and "vision" not in capabilities:
                    capabilities.append("vision")
                
                model_meta = ModelMetadata(
                    id=mid,
                    name=mdata.get("served_model_name", mid),
                    capabilities=capabilities,
                    context_window=mdata.get("context_window", 16384),
                    adapter_type=mdata.get("adapter", mdata.get("adapter_type", "vllm")),
                    quantization=mdata.get("quantization", "none"),
                    priority=1 if mdata.get("tier") == "stretch" else 2 if mdata.get("tier") == "recommended" else 3,
                    vram_required_gb=mdata.get("vram_required_mb", 0) // 1024,
                    status="active",
                    fallback_targets=mdata.get("fallback_targets", [])
                )
                self.models[mid] = model_meta
        elif isinstance(raw_models, list):
            for item in raw_models:
                model_meta = ModelMetadata(**item)
                self.models[model_meta.id] = model_meta

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        return self.models.get(model_id)

    def get_models_by_capability(self, capability: str) -> List[ModelMetadata]:
        """Finds all active models supporting a capability, sorted by priority (1 is highest)."""
        matching = [
            m for m in self.models.values()
            if capability.lower() in [c.lower() for c in m.capabilities] and m.status == "active"
        ]
        return sorted(matching, key=lambda m: m.priority)

    def register_adapter(self, model_id: str, adapter: ModelAdapter):
        """Allows runtime registration of an adapter instance (e.g. from P2)."""
        self._adapters[model_id] = adapter

    def get_adapter(self, model_id: str) -> ModelAdapter:
        """Retrieves or creates a default adapter for the model."""
        if model_id in self._adapters:
            return self._adapters[model_id]

        model_meta = self.get_model(model_id)
        if not model_meta:
            raise ValueError(f"Unknown model_id: {model_id}")

        # In absence of a live backend process, provide MockLocalAdapter as safe fallback
        adapter = MockLocalAdapter(model_id=model_id, config={"quantization": model_meta.quantization})
        self._adapters[model_id] = adapter
        return adapter

    def list_models(self) -> List[ModelMetadata]:
        return list(self.models.values())
