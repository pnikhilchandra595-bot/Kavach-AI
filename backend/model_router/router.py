"""
Task Intent Classifier and Model Router.
Inspects incoming task requirements, context size, and modalities to select the best local model.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import re
import os
from model_router.registry import ModelRegistry, ModelMetadata
from model_router.fallback_policy import FallbackPolicy, FallbackEvent
from model_router.adapters.base import ModelResponse, GenerationConfig


class RoutingDecision(BaseModel):
    selected_model_id: str
    task_type: str
    confidence: float
    rationale: str
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    fallback_chain: List[str] = Field(default_factory=list)


class ModelRouter:
    """
    Classifies task intent (code, vision, OCR, planning/reasoning, summarization)
    and routes to the optimal local model from the registry.
    """

    # Keyword taxonomies for zero-overhead local intent classification
    CODE_KEYWORDS = {
        "python", "script", "def ", "class ", "import ", "function", "docker", 
        "sandbox", "code", "bug", "algorithm", "sql", "syntax", "compile", 
        "traceback", "exception", "json", "yaml", "regex", "pandas", "numpy"
    }
    
    VISION_KEYWORDS = {
        "p&id", "pid", "diagram", "schematic", "drawing", "blueprint", "photo", 
        "image", "flowsheet", "piping", "valve", "instrumentation", "isometrics",
        ".png", ".jpg", ".jpeg", ".bmp", ".svg"
    }

    OCR_KEYWORDS = {
        "ocr", "scanned", "handwritten", "handwriting", "tesseract", "paddleocr",
        "extract text", "receipt", "log sheet", "inspection sheet", "scanned pdf"
    }

    SUMMARIZATION_KEYWORDS = {
        "summarize", "summary", "brief", "digest", "tldr", "abstract", "condense", 
        "overview", "executive summary"
    }

    def __init__(self, registry: Optional[ModelRegistry] = None, fallback_policy: Optional[FallbackPolicy] = None):
        self.registry = registry or ModelRegistry()
        self.fallback_policy = fallback_policy or FallbackPolicy(self.registry)
        self.confidence_threshold = self.registry.default_confidence_threshold

    def classify_task(self, prompt: str, attached_files: Optional[List[str]] = None) -> tuple[str, float, str]:
        """
        Classifies task into (task_type, confidence, rationale).
        Task types: 'code', 'vision', 'ocr', 'summarization', 'reasoning'
        """
        prompt_lower = prompt.lower()
        attached_files = attached_files or []

        # 1. Inspect attached file extensions
        for f in attached_files:
            ext = os.path.splitext(f)[1].lower()
            if ext in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
                return "vision", 0.95, f"Attached image file '{os.path.basename(f)}' requires vision model."
            if ext in {".py", ".sh", ".sql", ".js", ".ts", ".json", ".c", ".cpp"}:
                return "code", 0.92, f"Attached source code file '{os.path.basename(f)}' requires coding model."

        # 2. Score keyword matching
        words = set(re.findall(r"\b[a-z0-9_#&.-]+\b", prompt_lower))
        
        vision_matches = words.intersection(self.VISION_KEYWORDS)
        code_matches = words.intersection(self.CODE_KEYWORDS)
        ocr_matches = words.intersection(self.OCR_KEYWORDS)
        sum_matches = words.intersection(self.SUMMARIZATION_KEYWORDS)

        scores = {
            "vision": len(vision_matches) * 1.5,
            "code": len(code_matches) * 1.4,
            "ocr": len(ocr_matches) * 1.3,
            "summarization": len(sum_matches) * 1.2,
        }

        # Check explicit code blocks or function syntax
        if "```" in prompt or "def " in prompt_lower or "import " in prompt_lower:
            scores["code"] += 3.0

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        if best_score >= 2.5:
            confidence = min(0.95, 0.60 + (best_score * 0.10))
            rationale = f"High keyword alignment for {best_type} (matches: {eval(f'{best_type}_matches') if best_type in ['vision', 'code', 'ocr', 'summarization'] else ''})"
            return best_type, confidence, rationale

        if best_score > 0:
            confidence = min(0.75, 0.50 + (best_score * 0.10))
            rationale = f"Moderate keyword match for {best_type}."
            return best_type, confidence, rationale

        # Default fallback to reasoning
        return "reasoning", 0.70, "Defaulting to general reasoning/planning model for complex multi-step reasoning."

    def route(self, prompt: str, attached_files: Optional[List[str]] = None) -> RoutingDecision:
        """
        Determines the optimal model and fallback chain for the given task.
        """
        task_type, confidence, rationale = self.classify_task(prompt, attached_files)

        # Handle low confidence below threshold
        requires_clarification = False
        clarification_question = None

        if confidence < self.confidence_threshold:
            requires_clarification = True
            clarification_question = (
                f"Task intent is ambiguous (confidence: {confidence:.2f}). "
                "Should this be routed to the Coding Model or the General Reasoning Model?"
            )
            # Safe default fallback to highest-capability reasoning model
            target_capability = "reasoning"
            rationale += f" [Confidence {confidence:.2f} < {self.confidence_threshold:.2f}; routed safely to reasoning]"
        else:
            capability_map = {
                "code": "code",
                "vision": "vision",
                "ocr": "ocr",
                "summarization": "summarization",
                "reasoning": "reasoning"
            }
            target_capability = capability_map.get(task_type, "reasoning")

        # Select candidate model from registry
        candidates = self.registry.get_models_by_capability(target_capability)
        if not candidates:
            # Fallback to general reasoning if specific capability not found
            candidates = self.registry.get_models_by_capability("reasoning")

        if not candidates:
            # Fallback to mock universal model if everything else fails
            selected_model = self.registry.get_model("mock-universal-agent")
        else:
            selected_model = candidates[0]

        fallback_chain = self.fallback_policy.get_fallback_chain(selected_model.id)

        return RoutingDecision(
            selected_model_id=selected_model.id,
            task_type=task_type,
            confidence=confidence,
            rationale=rationale,
            requires_clarification=requires_clarification,
            clarification_question=clarification_question,
            fallback_chain=fallback_chain
        )

    def dispatch(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        attached_files: Optional[List[str]] = None,
        config: Optional[GenerationConfig] = None
    ) -> tuple[ModelResponse, RoutingDecision]:
        """
        Routes the task and executes with fallback protection.
        """
        decision = self.route(prompt, attached_files)
        response = self.fallback_policy.execute_with_fallback(
            preferred_model_id=decision.selected_model_id,
            prompt=prompt,
            system_prompt=system_prompt,
            config=config
        )
        return response, decision
