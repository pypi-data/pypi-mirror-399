"""Orchestrator pattern for coordinating multiple agents."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from miu_core.agents.base import Agent
from miu_core.models import Response


class OrchestratorConfig(BaseModel):
    """Configuration for orchestrator."""

    max_parallel: int = 5
    fail_fast: bool = True
    timeout: float | None = None


@dataclass
class TaskResult:
    """Result from an orchestrated task."""

    agent_name: str
    success: bool
    response: Response | None = None
    error: str | None = None


@dataclass
class Task:
    """A task to be executed by an agent."""

    name: str
    agent: Agent
    query: str | Callable[[dict[str, Any]], str]
    depends_on: list[str] = field(default_factory=list)


class Orchestrator:
    """Coordinates multiple agents to complete complex tasks.

    The orchestrator manages agent dependencies and execution order,
    allowing for both sequential and parallel execution patterns.

    Example:
        orchestrator = Orchestrator()
        orchestrator.add_agent("researcher", research_agent)
        orchestrator.add_agent("writer", writer_agent)

        orchestrator.add_task("research", "researcher", "Research AI agents")
        orchestrator.add_task(
            "write",
            "writer",
            lambda ctx: f"Write about: {ctx['research'].response.get_text()}",
            depends_on=["research"],
        )

        results = await orchestrator.run()
    """

    def __init__(self, config: OrchestratorConfig | None = None) -> None:
        self.config = config or OrchestratorConfig()
        self._agents: dict[str, Agent] = {}
        self._tasks: list[Task] = []

    def add_agent(self, name: str, agent: Agent) -> None:
        """Register an agent with a name."""
        self._agents[name] = agent

    def add_task(
        self,
        name: str,
        agent_name: str,
        query: str | Callable[[dict[str, Any]], str],
        depends_on: list[str] | None = None,
    ) -> None:
        """Add a task to be executed.

        Args:
            name: Unique task identifier
            agent_name: Name of the agent to execute this task
            query: Either a static query string or a callable that receives
                   the context dict and returns a query string
            depends_on: List of task names that must complete before this task
        """
        if agent_name not in self._agents:
            raise ValueError(f"Agent '{agent_name}' not registered")

        self._tasks.append(
            Task(
                name=name,
                agent=self._agents[agent_name],
                query=query,
                depends_on=depends_on or [],
            )
        )

    async def run(self) -> dict[str, TaskResult]:
        """Execute all tasks respecting dependencies.

        Returns:
            Dictionary mapping task names to their results
        """
        results: dict[str, TaskResult] = {}
        completed: set[str] = set()
        context: dict[str, Any] = {}

        # Build dependency graph
        task_map = {task.name: task for task in self._tasks}

        # Topological sort for execution order
        execution_order = self._topological_sort(task_map)

        for task_name in execution_order:
            task = task_map[task_name]

            # Check dependencies are satisfied
            for dep in task.depends_on:
                if dep not in completed:
                    raise RuntimeError(f"Dependency '{dep}' not satisfied for '{task_name}'")
                if self.config.fail_fast and not results[dep].success:
                    results[task_name] = TaskResult(
                        agent_name=task_name,
                        success=False,
                        error=f"Dependency '{dep}' failed",
                    )
                    continue

            # Build query from context if callable
            query = task.query(context) if callable(task.query) else task.query

            # Execute task
            try:
                response = await task.agent.run(query)
                result = TaskResult(
                    agent_name=task_name,
                    success=True,
                    response=response,
                )
            except Exception as e:
                result = TaskResult(
                    agent_name=task_name,
                    success=False,
                    error=str(e),
                )
                if self.config.fail_fast:
                    results[task_name] = result
                    break

            results[task_name] = result
            context[task_name] = result
            completed.add(task_name)

        return results

    def _topological_sort(self, task_map: dict[str, Task]) -> list[str]:
        """Sort tasks by dependencies (Kahn's algorithm)."""
        in_degree: dict[str, int] = {name: 0 for name in task_map}
        graph: dict[str, list[str]] = {name: [] for name in task_map}

        for name, task in task_map.items():
            for dep in task.depends_on:
                if dep in graph:
                    graph[dep].append(name)
                    in_degree[name] += 1

        # Start with tasks that have no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result: list[str] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(task_map):
            raise ValueError("Circular dependency detected in tasks")

        return result

    def clear(self) -> None:
        """Clear all agents and tasks."""
        self._agents.clear()
        self._tasks.clear()
