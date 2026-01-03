"""Tests for multi-agent patterns."""

import uuid

import pytest

from miu_core.models import Response, TextContent
from miu_core.patterns import (
    Orchestrator,
    OrchestratorConfig,
    Pipeline,
    PipelineConfig,
    Router,
    RouterConfig,
)


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, response_text: str = "mock response") -> None:
        self.response_text = response_text
        self.run_count = 0
        self.last_query: str | None = None

    async def run(self, query: str) -> Response:
        """Mock run method."""
        self.run_count += 1
        self.last_query = query
        return Response(
            id=str(uuid.uuid4()),
            content=[TextContent(type="text", text=f"{self.response_text}: {query[:50]}")],
        )


class FailingAgent:
    """Agent that raises exceptions."""

    async def run(self, query: str) -> Response:
        """Always fails."""
        raise RuntimeError("Agent failed")


# =============================================================================
# Orchestrator Tests
# =============================================================================


class TestOrchestrator:
    """Tests for Orchestrator pattern."""

    @pytest.fixture
    def orchestrator(self) -> Orchestrator:
        """Create orchestrator instance."""
        return Orchestrator()

    async def test_single_task(self, orchestrator: Orchestrator) -> None:
        """Test single task execution."""
        agent = MockAgent("result")
        orchestrator.add_agent("test", agent)
        orchestrator.add_task("task1", "test", "do something")

        results = await orchestrator.run()

        assert "task1" in results
        assert results["task1"].success
        assert agent.run_count == 1
        assert "do something" in agent.last_query  # type: ignore

    async def test_task_with_dependencies(self, orchestrator: Orchestrator) -> None:
        """Test tasks with dependencies execute in order."""
        agent1 = MockAgent("first")
        agent2 = MockAgent("second")

        orchestrator.add_agent("agent1", agent1)
        orchestrator.add_agent("agent2", agent2)

        orchestrator.add_task("task1", "agent1", "first task")
        orchestrator.add_task(
            "task2",
            "agent2",
            lambda ctx: f"second task using {ctx['task1'].response.get_text()[:10]}",
            depends_on=["task1"],
        )

        results = await orchestrator.run()

        assert results["task1"].success
        assert results["task2"].success
        assert agent1.run_count == 1
        assert agent2.run_count == 1
        # Verify task2 received context from task1
        assert "first" in agent2.last_query  # type: ignore

    async def test_fail_fast(self) -> None:
        """Test fail_fast stops on error."""
        orchestrator = Orchestrator(OrchestratorConfig(fail_fast=True))

        orchestrator.add_agent("failing", FailingAgent())
        orchestrator.add_agent("second", MockAgent())

        orchestrator.add_task("task1", "failing", "will fail")
        orchestrator.add_task("task2", "second", "should not run", depends_on=["task1"])

        results = await orchestrator.run()

        assert not results["task1"].success
        assert "Agent failed" in (results["task1"].error or "")
        # Task2 should not exist or show dependency failure
        assert "task2" not in results or not results["task2"].success

    async def test_unregistered_agent_raises(self, orchestrator: Orchestrator) -> None:
        """Test adding task with unregistered agent."""
        with pytest.raises(ValueError, match="not registered"):
            orchestrator.add_task("task", "unknown_agent", "query")

    async def test_circular_dependency_detection(self, orchestrator: Orchestrator) -> None:
        """Test circular dependencies are detected."""
        agent = MockAgent()
        orchestrator.add_agent("a", agent)

        orchestrator.add_task("task1", "a", "q1", depends_on=["task2"])
        orchestrator.add_task("task2", "a", "q2", depends_on=["task1"])

        with pytest.raises(ValueError, match="Circular dependency"):
            await orchestrator.run()

    async def test_clear(self, orchestrator: Orchestrator) -> None:
        """Test clearing orchestrator."""
        orchestrator.add_agent("test", MockAgent())
        orchestrator.add_task("task", "test", "query")
        orchestrator.clear()

        results = await orchestrator.run()
        assert len(results) == 0


# =============================================================================
# Pipeline Tests
# =============================================================================


class TestPipeline:
    """Tests for Pipeline pattern."""

    @pytest.fixture
    def pipeline(self) -> Pipeline:
        """Create pipeline instance."""
        return Pipeline()

    async def test_single_stage(self, pipeline: Pipeline) -> None:
        """Test single stage pipeline."""
        agent = MockAgent("stage1")
        pipeline.add_stage("stage1", agent)

        result = await pipeline.run("initial query")

        assert result.success
        assert result.stages_completed == 1
        assert result.final_response is not None
        assert "stage1" in result.final_response.get_text()

    async def test_multiple_stages(self, pipeline: Pipeline) -> None:
        """Test pipeline with multiple stages."""
        agent1 = MockAgent("first")
        agent2 = MockAgent("second")

        pipeline.add_stage("s1", agent1).add_stage("s2", agent2)

        result = await pipeline.run("start")

        assert result.success
        assert result.stages_completed == 2
        assert len(result.stage_responses) == 2
        assert "s1" in result.stage_responses
        assert "s2" in result.stage_responses

    async def test_transform_function(self, pipeline: Pipeline) -> None:
        """Test transform between stages."""
        agent1 = MockAgent("data")
        agent2 = MockAgent("processed")

        pipeline.add_stage("extract", agent1)
        pipeline.add_stage(
            "transform",
            agent2,
            transform=lambda q, r: f"TRANSFORM: {r.get_text()}",
        )

        result = await pipeline.run("input")

        assert result.success
        assert agent2.last_query is not None
        assert "TRANSFORM" in agent2.last_query

    async def test_stop_on_error(self) -> None:
        """Test pipeline stops on error when configured."""
        pipeline = Pipeline(PipelineConfig(stop_on_error=True))

        pipeline.add_stage("s1", MockAgent("ok"))
        pipeline.add_stage("s2", FailingAgent())
        pipeline.add_stage("s3", MockAgent("never"))

        result = await pipeline.run("start")

        assert not result.success
        assert result.stages_completed == 1
        assert result.failed_stage == "s2"
        assert "Agent failed" in (result.error or "")

    async def test_continue_on_error(self) -> None:
        """Test pipeline continues on error when configured."""
        pipeline = Pipeline(PipelineConfig(stop_on_error=False))

        agent1 = MockAgent("first")
        agent3 = MockAgent("third")

        pipeline.add_stage("s1", agent1)
        pipeline.add_stage("s2", FailingAgent())
        pipeline.add_stage("s3", agent3)

        result = await pipeline.run("start")

        # Should complete despite error (2 successful stages)
        assert result.success
        assert result.stages_completed == 3

    async def test_stages_property(self, pipeline: Pipeline) -> None:
        """Test stages property returns names."""
        pipeline.add_stage("a", MockAgent())
        pipeline.add_stage("b", MockAgent())
        pipeline.add_stage("c", MockAgent())

        assert pipeline.stages == ["a", "b", "c"]
        assert len(pipeline) == 3


# =============================================================================
# Router Tests
# =============================================================================


class TestRouter:
    """Tests for Router pattern."""

    @pytest.fixture
    def router(self) -> Router:
        """Create router instance."""
        return Router()

    async def test_keyword_routing(self, router: Router) -> None:
        """Test routing by keywords."""
        code_agent = MockAgent("code response")
        write_agent = MockAgent("write response")

        router.add_route("code", code_agent, keywords=["python", "code", "debug"])
        router.add_route("writing", write_agent, keywords=["write", "essay"])

        result = await router.route("help me debug python code")

        assert result.agent_name == "code"
        assert "code response" in result.response.get_text()

    async def test_pattern_routing(self, router: Router) -> None:
        """Test routing by regex pattern."""
        math_agent = MockAgent("math")

        router.add_route("math", math_agent, pattern=r"\d+\s*[\+\-\*\/]\s*\d+")

        result = await router.route("calculate 5 + 3")

        assert result.agent_name == "math"

    async def test_condition_routing(self, router: Router) -> None:
        """Test routing by custom condition."""
        long_agent = MockAgent("long handler")

        router.add_route("long", long_agent, condition=lambda q: len(q) > 50)

        result = await router.route("a" * 60)

        assert result.agent_name == "long"

    async def test_priority_ordering(self, router: Router) -> None:
        """Test routes are checked by priority."""
        specific = MockAgent("specific")
        general = MockAgent("general")

        router.add_route("general", general, condition=lambda q: True, priority=0)
        router.add_route(
            "specific",
            specific,
            keywords=["special"],
            priority=10,  # Higher priority
        )

        result = await router.route("special request")

        assert result.agent_name == "specific"

    async def test_default_agent(self) -> None:
        """Test default agent fallback."""
        router = Router(RouterConfig(default_agent="fallback"))
        fallback = MockAgent("fallback")

        router.add_route("fallback", fallback, condition=lambda q: False)  # Never matches

        result = await router.route("any query")

        assert result.agent_name == "fallback"

    async def test_no_match_raises(self, router: Router) -> None:
        """Test unmatched query raises error."""
        router.add_route("specific", MockAgent(), keywords=["specific"])

        with pytest.raises(ValueError, match="Unable to route"):
            await router.route("unmatched query")

    def test_get_route_without_execution(self, router: Router) -> None:
        """Test get_route returns name without running agent."""
        agent = MockAgent()
        router.add_route("test", agent, keywords=["test"])

        route = router.get_route("test query")

        assert route == "test"
        assert agent.run_count == 0  # Agent not called

    def test_routes_property(self, router: Router) -> None:
        """Test routes property returns names."""
        router.add_route("a", MockAgent(), keywords=["a"])
        router.add_route("b", MockAgent(), keywords=["b"])

        # Routes sorted by priority (same priority = insertion order)
        assert set(router.routes) == {"a", "b"}

    def test_must_provide_routing_rule(self, router: Router) -> None:
        """Test that at least one routing rule is required."""
        with pytest.raises(ValueError, match="Must provide"):
            router.add_route("invalid", MockAgent())
