"""
Model Registry Manager with Versioning and Rollback
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer

Maintains pluggable model configurations, detects hardware capacity constraints,
and enforces rollback-capable versioning for mission-critical refinery operations.
"""

import os
import json
import shutil
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from .adapters import BaseModelAdapter, create_adapter


class RegistryValidationError(Exception):
    """Raised when registry schema or model definition is invalid."""
    pass


class ModelNotFoundError(Exception):
    """Raised when a requested model is not present in the active registry."""
    pass


class VersionRollbackError(Exception):
    """Raised when a requested rollback version is invalid or unreachable."""
    pass


class ModelRegistryManager:
    """Manages versioned model registry, hardware tier detection, and adapter lifecycle."""

    def __init__(self, registry_path: Optional[str] = None, history_dir: Optional[str] = None):
        base_dir = Path(__file__).parent
        self.registry_path = Path(registry_path or (base_dir / "model_registry.yaml"))
        self.history_dir = Path(history_dir or (base_dir / "registry_history"))
        self.history_dir.mkdir(parents=True, exist_ok=True)

        self._raw_config: Dict[str, Any] = {}
        self._active_adapters: Dict[str, BaseModelAdapter] = {}
        self.system_vram_mb: int = 4096  # Default detected or fallback
        self.system_ram_mb: int = 16384
        self.reduced_capacity_mode: bool = False

        self._detect_hardware()
        self.load_registry()

    def _detect_hardware(self):
        """Detect local host VRAM and system memory to determine hardware tier."""
        # Check environment override first (e.g. for testing)
        vram_env = os.environ.get("SOVEREIGN_VRAM_MB")
        if vram_env:
            try:
                self.system_vram_mb = int(vram_env)
            except ValueError:
                pass
        else:
            # Probe Windows CIM / nvidia-smi if available
            try:
                import subprocess
                res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if res.returncode == 0 and res.stdout.strip():
                    self.system_vram_mb = int(res.stdout.strip().split("\n")[0])
            except Exception:
                # Fallback to 4096 MB (RTX 3050 Laptop tier)
                self.system_vram_mb = 4096

        # Check for degraded / reduced-capacity mode
        # If available VRAM is < 8192 MB, trigger Tier 1 "reduced-capacity mode"
        if self.system_vram_mb < 8192:
            self.reduced_capacity_mode = True
        else:
            self.reduced_capacity_mode = False

    def load_registry(self) -> Dict[str, Any]:
        """Load and validate the active model registry file."""
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry file not found at {self.registry_path}")

        content = self.registry_path.read_text(encoding="utf-8")
        if HAS_YAML:
            self._raw_config = yaml.safe_load(content) or {}
        else:
            # Standard json fallback or simplified parser
            self._raw_config = json.loads(content)

        self._validate_schema(self._raw_config)
        return self._raw_config

    def _validate_schema(self, config: Dict[str, Any]):
        """Ensure all required fields exist and constraints are satisfied."""
        required_roots = ["schema_version", "registry_version", "models"]
        for r in required_roots:
            if r not in config:
                raise RegistryValidationError(f"Missing required registry root key: '{r}'")

        models = config.get("models", {})
        if not isinstance(models, dict) or not models:
            raise RegistryValidationError("Registry must define at least one model in 'models'")

        for model_id, mcfg in models.items():
            for req in ["family", "adapter", "quantization", "vram_required_mb", "strengths"]:
                if req not in mcfg:
                    raise RegistryValidationError(f"Model '{model_id}' is missing required field '{req}'")

    def get_hardware_tier(self) -> str:
        """Return the current operating hardware tier."""
        if self.system_vram_mb < 8192:
            return "degraded"
        elif self.system_vram_mb < 16384:
            return "minimum"
        elif self.system_vram_mb < 40960:
            return "recommended"
        return "stretch"

    def get_registry_version(self) -> str:
        return self._raw_config.get("registry_version", "1.0.0")

    def list_models(self) -> List[Dict[str, Any]]:
        """List all models registered in the system with their metadata."""
        out = []
        for mid, mcfg in self._raw_config.get("models", {}).items():
            entry = dict(mcfg)
            entry["model_id"] = mid
            entry["fits_current_hardware"] = (mcfg.get("vram_required_mb", 0) <= self.system_vram_mb)
            out.append(entry)
        return out

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Fetch config for a specific model ID."""
        models = self._raw_config.get("models", {})
        if model_id not in models:
            raise ModelNotFoundError(f"Model '{model_id}' not found in registry (available: {list(models.keys())})")
        cfg = dict(models[model_id])
        cfg["model_id"] = model_id
        return cfg

    def get_models_for_task(self, task_type: str, strict_hardware: bool = True) -> List[Dict[str, Any]]:
        """Return matching models sorted by fitness and hardware compatibility."""
        matches = []
        for mid, mcfg in self._raw_config.get("models", {}).items():
            strengths = mcfg.get("strengths", [])
            if task_type in strengths:
                fits = (mcfg.get("vram_required_mb", 0) <= self.system_vram_mb)
                if strict_hardware and not fits:
                    continue
                entry = dict(mcfg)
                entry["model_id"] = mid
                matches.append(entry)

        # Sort: preferential to models matching current tier, then lower vram
        matches.sort(key=lambda m: (m.get("vram_required_mb", 0)), reverse=not strict_hardware)
        return matches

    def get_adapter(self, model_id: str) -> BaseModelAdapter:
        """Get or instantiate the inference adapter for the given model ID."""
        if model_id in self._active_adapters:
            return self._active_adapters[model_id]

        mcfg = self.get_model(model_id)
        adapter = create_adapter(model_id, mcfg)
        self._active_adapters[model_id] = adapter
        return adapter

    def create_snapshot(self, reason: str = "Config update", author: str = "engineer") -> str:
        """Snapshot the current registry state into version history."""
        current_version = self.get_registry_version()
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snapshot_filename = f"registry_v{current_version}_{timestamp}.yaml"
        snapshot_path = self.history_dir / snapshot_filename

        # Write snapshot
        shutil.copy2(self.registry_path, snapshot_path)

        # Update metadata ledger
        ledger_path = self.history_dir / "version_ledger.json"
        ledger = []
        if ledger_path.exists():
            try:
                ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            except Exception:
                ledger = []

        ledger.append({
            "version": current_version,
            "filename": snapshot_filename,
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "author": author,
        })
        ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        return snapshot_filename

    def list_version_history(self) -> List[Dict[str, Any]]:
        """Return history of all version snapshots."""
        ledger_path = self.history_dir / "version_ledger.json"
        if not ledger_path.exists():
            return []
        try:
            return json.loads(ledger_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def rollback_to_version(self, target_version: str, author: str = "supervisor") -> Dict[str, Any]:
        """Roll back registry to a specific previous version from the snapshot history."""
        history = self.list_version_history()
        target_entry = None
        for entry in reversed(history):
            if entry.get("version") == target_version:
                target_entry = entry
                break

        if not target_entry:
            # Check by filename directly
            candidate = self.history_dir / target_version
            if candidate.exists():
                target_entry = {"filename": candidate.name, "version": "custom"}
            else:
                available = [e.get("version") for e in history]
                raise VersionRollbackError(
                    f"Version '{target_version}' not found in history. Available versions: {available}"
                )

        snapshot_file = self.history_dir / target_entry["filename"]
        if not snapshot_file.exists():
            raise VersionRollbackError(f"Snapshot file '{snapshot_file}' is missing from disk")

        # Snapshot current state before rolling back
        current_v = self.get_registry_version()
        self.create_snapshot(reason=f"Pre-rollback backup before restoring v{target_version}", author=author)

        # Restore
        shutil.copy2(snapshot_file, self.registry_path)

        # Invalidate active adapters cache
        self._active_adapters.clear()

        # Reload and revalidate
        self.load_registry()

        return {
            "status": "ROLLBACK_SUCCESSFUL",
            "restored_version": target_version,
            "previous_version": current_v,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "operator": author,
        }

    def update_model_param(self, model_id: str, updates: Dict[str, Any], author: str = "engineer", reason: str = "Param tune") -> str:
        """Update a model parameter with automatic version bump and snapshot."""
        if model_id not in self._raw_config.get("models", {}):
            raise ModelNotFoundError(f"Cannot update unknown model '{model_id}'")

        # Create pre-update snapshot
        self.create_snapshot(reason=f"Prior to updating {model_id}: {reason}", author=author)

        # Apply updates
        self._raw_config["models"][model_id].update(updates)

        # Increment patch version
        curr_ver = self._raw_config.get("registry_version", "1.0.0")
        parts = curr_ver.split(".")
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
            new_ver = ".".join(parts)
        else:
            new_ver = f"{curr_ver}.1"

        self._raw_config["registry_version"] = new_ver
        self._raw_config["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"

        # Save to disk
        if HAS_YAML:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                yaml.dump(self._raw_config, f, sort_keys=False)
        else:
            self.registry_path.write_text(json.dumps(self._raw_config, indent=2), encoding="utf-8")

        self._active_adapters.pop(model_id, None)
        return new_ver
