"""Router pattern for directing requests to appropriate agents."""

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from miu_core.agents.base import Agent
from miu_core.models import Response


class RouterConfig(BaseModel):
    """Configuration for router."""

    default_agent: str | None = None
    fallback_message: str = "Unable to route request to an appropriate agent."


@dataclass
class RoutingRule:
    """A rule for routing requests."""

    name: str
    agent: Agent
    condition: Callable[[str], bool]
    priority: int = 0
    metadata: dict[str, Any] | None = None


@dataclass
class RouteResult:
    """Result from routing a request."""

    agent_name: str
    response: Response
    matched_rule: str | None = None


class Router:
    """Routes requests to appropriate agents based on rules.

    The router evaluates rules in priority order and directs the request
    to the first matching agent. Rules can be keyword-based, regex-based,
    or use custom condition functions.

    Example:
        router = Router()

        # Add agents with keyword-based routing
        router.add_route(
            "code",
            code_agent,
            keywords=["code", "programming", "debug"]
        )
        router.add_route(
            "writing",
            writing_agent,
            keywords=["write", "essay", "article"]
        )
        router.add_route(
            "general",
            general_agent,
            condition=lambda q: True,  # Catch-all
            priority=-1
        )

        result = await router.route("Help me debug this Python code")
        # Routes to code_agent
    """

    def __init__(self, config: RouterConfig | None = None) -> None:
        self.config = config or RouterConfig()
        self._routes: list[RoutingRule] = []
        self._agents: dict[str, Agent] = {}

    def add_route(
        self,
        name: str,
        agent: Agent,
        *,
        keywords: list[str] | None = None,
        pattern: str | None = None,
        condition: Callable[[str], bool] | None = None,
        priority: int = 0,
        **metadata: Any,
    ) -> "Router":
        """Add a routing rule.

        Args:
            name: Route identifier
            agent: Agent to route to when rule matches
            keywords: List of keywords to match (case-insensitive)
            pattern: Regex pattern to match
            condition: Custom condition function receiving the query
            priority: Higher priority rules are checked first (default 0)
            **metadata: Additional metadata for the route

        Returns:
            Self for method chaining
        """
        self._agents[name] = agent

        # Build condition from keywords, pattern, or custom
        if condition:
            rule_condition = condition
        elif pattern:
            rule_condition = self._make_pattern_condition(pattern)
        elif keywords:
            rule_condition = self._make_keyword_condition(keywords)
        else:
            raise ValueError("Must provide keywords, pattern, or condition")

        self._routes.append(
            RoutingRule(
                name=name,
                agent=agent,
                condition=rule_condition,
                priority=priority,
                metadata=dict(metadata) if metadata else None,
            )
        )

        # Sort by priority (highest first)
        self._routes.sort(key=lambda r: -r.priority)
        return self

    async def route(self, query: str) -> RouteResult:
        """Route a query to the appropriate agent.

        Args:
            query: The user query to route

        Returns:
            RouteResult with the agent's response
        """
        # Check rules in priority order
        for rule in self._routes:
            if rule.condition(query):
                response = await rule.agent.run(query)
                return RouteResult(
                    agent_name=rule.name,
                    response=response,
                    matched_rule=rule.name,
                )

        # Fall back to default agent
        if self.config.default_agent and self.config.default_agent in self._agents:
            response = await self._agents[self.config.default_agent].run(query)
            return RouteResult(
                agent_name=self.config.default_agent,
                response=response,
                matched_rule=None,
            )

        raise ValueError(self.config.fallback_message)

    def get_route(self, query: str) -> str | None:
        """Get the route name without executing the agent.

        Args:
            query: The query to check routing for

        Returns:
            Name of the matched route or None
        """
        for rule in self._routes:
            if rule.condition(query):
                return rule.name

        return self.config.default_agent

    @property
    def routes(self) -> list[str]:
        """Return list of route names."""
        return [route.name for route in self._routes]

    @staticmethod
    def _make_pattern_condition(pattern: str) -> Callable[[str], bool]:
        """Create a regex-based condition."""
        compiled = re.compile(pattern, re.IGNORECASE)

        def condition(query: str) -> bool:
            return bool(compiled.search(query))

        return condition

    @staticmethod
    def _make_keyword_condition(keywords: list[str]) -> Callable[[str], bool]:
        """Create a keyword-based condition."""
        kw_lower = [k.lower() for k in keywords]

        def condition(query: str) -> bool:
            query_lower = query.lower()
            return any(k in query_lower for k in kw_lower)

        return condition
