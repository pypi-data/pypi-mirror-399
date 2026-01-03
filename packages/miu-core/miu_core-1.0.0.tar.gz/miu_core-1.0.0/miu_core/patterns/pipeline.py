"""Pipeline pattern for sequential agent processing."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from miu_core.agents.base import Agent
from miu_core.models import Response


class PipelineConfig(BaseModel):
    """Configuration for pipeline."""

    stop_on_error: bool = True


@dataclass
class PipelineStage:
    """A stage in the pipeline."""

    name: str
    agent: Agent
    transform: Callable[[str, Response], str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Result from pipeline execution."""

    success: bool
    stages_completed: int
    final_response: Response | None
    stage_responses: dict[str, Response]
    error: str | None = None
    failed_stage: str | None = None


class Pipeline:
    """Sequential agent chain where each stage's output feeds to the next.

    Pipelines are useful for tasks that require multiple processing steps,
    such as research -> summarize -> write -> edit.

    Example:
        pipeline = Pipeline()
        pipeline.add_stage("research", research_agent)
        pipeline.add_stage(
            "summarize",
            summarizer_agent,
            transform=lambda query, resp: f"Summarize: {resp.get_text()}"
        )
        pipeline.add_stage(
            "edit",
            editor_agent,
            transform=lambda query, resp: f"Edit this: {resp.get_text()}"
        )

        result = await pipeline.run("Research quantum computing")
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self._stages: list[PipelineStage] = []

    def add_stage(
        self,
        name: str,
        agent: Agent,
        transform: Callable[[str, Response], str] | None = None,
        **metadata: Any,
    ) -> "Pipeline":
        """Add a stage to the pipeline.

        Args:
            name: Stage identifier
            agent: Agent to execute at this stage
            transform: Optional function to transform previous response into
                       the next query. Receives (original_query, previous_response)
                       and returns the new query string.
            **metadata: Additional metadata for the stage

        Returns:
            Self for method chaining
        """
        self._stages.append(
            PipelineStage(
                name=name,
                agent=agent,
                transform=transform,
                metadata=dict(metadata),
            )
        )
        return self

    async def run(self, initial_query: str) -> PipelineResult:
        """Execute the pipeline sequentially.

        Args:
            initial_query: The query to start the pipeline with

        Returns:
            PipelineResult with all stage outputs
        """
        stage_responses: dict[str, Response] = {}
        current_query = initial_query
        last_response: Response | None = None

        for i, stage in enumerate(self._stages):
            # Transform query if transformer provided and not first stage
            if stage.transform and last_response:
                current_query = stage.transform(initial_query, last_response)

            try:
                response = await stage.agent.run(current_query)
                stage_responses[stage.name] = response
                last_response = response
                current_query = response.get_text()
            except Exception as e:
                if self.config.stop_on_error:
                    return PipelineResult(
                        success=False,
                        stages_completed=i,
                        final_response=last_response,
                        stage_responses=stage_responses,
                        error=str(e),
                        failed_stage=stage.name,
                    )
                # Continue without this stage's response
                continue

        return PipelineResult(
            success=True,
            stages_completed=len(self._stages),
            final_response=last_response,
            stage_responses=stage_responses,
        )

    def __len__(self) -> int:
        """Return number of stages."""
        return len(self._stages)

    @property
    def stages(self) -> list[str]:
        """Return list of stage names."""
        return [stage.name for stage in self._stages]
