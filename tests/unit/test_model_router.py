"""Unit tests for model router."""
import pytest
from src.llm.model_router import ModelRouter, TaskComplexity


@pytest.fixture
def router():
    """Create a model router instance."""
    return ModelRouter()


@pytest.mark.unit
def test_select_model_simple_task(router):
    """Test model selection for simple tasks."""
    model = router.select_model(task_complexity=TaskComplexity.SIMPLE)
    assert model in router.model_metrics
    # Simple tasks should select cheaper models
    assert router.model_metrics[model]["cost"] <= 0.005


@pytest.mark.unit
def test_select_model_complex_task(router):
    """Test model selection for complex tasks."""
    model = router.select_model(task_complexity=TaskComplexity.COMPLEX)
    assert model in router.model_metrics
    # Complex tasks should select higher quality models
    assert router.model_metrics[model]["quality"] >= 9.0


@pytest.mark.unit
def test_select_model_with_cost_constraint(router):
    """Test model selection with cost constraint."""
    model = router.select_model(max_cost=0.002)
    assert router.model_metrics[model]["cost"] <= 0.002


@pytest.mark.unit
def test_select_model_with_latency_constraint(router):
    """Test model selection with latency constraint."""
    model = router.select_model(max_latency=2.0)
    assert router.model_metrics[model]["latency"] <= 2.0


@pytest.mark.unit
def test_mark_unavailable(router):
    """Test marking model as unavailable."""
    model = "gpt-4-turbo"
    router.mark_unavailable(model)
    assert router.model_availability[model] is False


@pytest.mark.unit
def test_mark_available(router):
    """Test marking model as available."""
    model = "gpt-4-turbo"
    router.mark_unavailable(model)
    router.mark_available(model)
    assert router.model_availability[model] is True


@pytest.mark.unit
def test_get_fallback_models(router):
    """Test getting fallback models."""
    fallbacks = router.get_fallback_models("gemini-pro")
    assert isinstance(fallbacks, list)
    assert len(fallbacks) > 0
    assert all(router.model_availability.get(m, False) for m in fallbacks)


@pytest.mark.unit
def test_optimize_for_cost(router):
    """Test cost optimization."""
    model = router.optimize_for_cost()
    assert model in router.model_metrics
    # Should select the cheapest model
    assert router.model_metrics[model]["cost"] == min(
        m["cost"] for m in router.model_metrics.values()
    )


@pytest.mark.unit
def test_optimize_for_latency(router):
    """Test latency optimization."""
    model = router.optimize_for_latency()
    assert model in router.model_metrics
    # Should select the fastest model
    assert router.model_metrics[model]["latency"] == min(
        m["latency"] for m in router.model_metrics.values()
    )


@pytest.mark.unit
def test_optimize_for_quality(router):
    """Test quality optimization."""
    model = router.optimize_for_quality()
    assert model in router.model_metrics
    # Should select the highest quality model
    assert router.model_metrics[model]["quality"] == max(
        m["quality"] for m in router.model_metrics.values()
    )
