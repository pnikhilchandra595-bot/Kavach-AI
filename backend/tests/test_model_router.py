"""
Unit tests for Model Registry and Model Router.
"""

import pytest
import os
from model_router.registry import ModelRegistry, ModelMetadata
from model_router.router import ModelRouter, RoutingDecision
from model_router.adapters.base import MockLocalAdapter


@pytest.fixture
def registry():
    return ModelRegistry()


@pytest.fixture
def router(registry):
    return ModelRouter(registry=registry)


def test_registry_loading(registry):
    assert len(registry.models) > 0
    assert "qwen2.5-72b-instruct" in registry.models
    assert "qwen2.5-coder-32b" in registry.models or any("coder" in m for m in registry.models)
    assert "qwen2.5-vl-7b" in registry.models or "qwen2.5-vl-7b-instruct" in registry.models

    coding_models = registry.get_models_by_capability("code")
    assert len(coding_models) >= 2
    # Check priority ordering
    assert coding_models[0].priority <= coding_models[1].priority


def test_router_code_classification(router):
    prompt = "Write a python script to parse pump vibration telemetry data and check thresholds."
    decision = router.route(prompt)
    assert decision.task_type == "code"
    assert "coder" in decision.selected_model_id or "code" in decision.rationale.lower()
    assert decision.confidence >= 0.70


def test_router_vision_classification(router):
    prompt = "Analyze this P&ID diagram and identify the bypass valve on line 12."
    decision = router.route(prompt)
    assert decision.task_type == "vision"
    assert "vl" in decision.selected_model_id or "vision" in decision.selected_model_id
    assert decision.confidence >= 0.75


def test_router_attached_file_detection(router):
    prompt = "Inspect this attached document."
    decision = router.route(prompt, attached_files=["/data/scanned_report.png"])
    assert decision.task_type == "vision"
    assert decision.confidence >= 0.90


def test_router_confidence_thresholding(router):
    # Very vague query
    prompt = "Hello"
    decision = router.route(prompt)
    # When vague or low confidence, should fall back safely to reasoning
    assert decision.selected_model_id in ("qwen2.5-72b-instruct", "mock-universal-agent")
