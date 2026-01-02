"""Sentrial Client - Main SDK interface"""

import os
import requests
from typing import Any, Optional, Dict
from .types import EventType


class SentrialClient:
    """
    Sentrial Client for tracking agent events.

    Usage:
        client = SentrialClient(
            api_url="http://localhost:3001",
            project_id="your-project-id"
        )

        # Create a session
        session_id = client.create_session(name="My Agent Run")

        # Track events
        client.track_tool_call(
            session_id=session_id,
            tool_name="search",
            tool_input={"query": "test"},
            tool_output={"result": "success"}
        )

        # Close session
        client.close_session(session_id)
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        project_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Sentrial client.

        Args:
            api_url: URL of the Sentrial API server (defaults to SENTRIAL_API_URL env var or production)
            project_id: Project ID (defaults to SENTRIAL_PROJECT_ID env var or demo project)
            api_key: API key for authentication (defaults to SENTRIAL_API_KEY env var)
        """
        self.api_url = (api_url or os.environ.get("SENTRIAL_API_URL", "https://api.sentrial.com")).rstrip("/")
        self.project_id = project_id or os.environ.get("SENTRIAL_PROJECT_ID", "00000000-0000-0000-0000-000000000000")
        self.api_key = api_key or os.environ.get("SENTRIAL_API_KEY")
        self.session = requests.Session()
        self.current_state: dict[str, Any] = {}

        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def create_session(
        self,
        name: str,
        agent_name: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Create a new session.

        Args:
            name: Name of the session
            agent_name: Required identifier for the agent type (used for grouping)
            metadata: Optional metadata

        Returns:
            Session ID
        """
        payload = {
            "projectId": self.project_id,
            "name": name,
            "agentName": agent_name,
            "metadata": metadata,
        }
            
        response = self.session.post(
            f"{self.api_url}/api/sdk/sessions",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["id"]

    def track_tool_call(
        self,
        session_id: str,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_output: dict[str, Any],
        reasoning: Optional[str] = None,
        estimated_cost: float = 0.0,
    ) -> dict[str, Any]:
        """
        Track a tool call event.

        Args:
            session_id: Session ID
            tool_name: Name of the tool
            tool_input: Tool input data
            tool_output: Tool output data
            reasoning: Optional reasoning
            estimated_cost: Estimated cost in USD for this tool call

        Returns:
            Event data
        """
        state_before = self.current_state.copy()

        # Update current state (simplified)
        self.current_state[f"{tool_name}_result"] = tool_output

        response = self.session.post(
            f"{self.api_url}/api/sdk/events",
            json={
                "sessionId": session_id,
                "eventType": EventType.TOOL_CALL.value,
                "toolName": tool_name,
                "toolInput": tool_input,
                "toolOutput": tool_output,
                "reasoning": reasoning,
                "stateBefore": state_before,
                "stateAfter": self.current_state.copy(),
                "estimatedCost": estimated_cost,
            },
        )
        response.raise_for_status()
        return response.json()

    def track_decision(
        self,
        session_id: str,
        reasoning: str,
        alternatives: Optional[list[str]] = None,
        confidence: Optional[float] = None,
        branch_name: str = "main",
    ) -> dict[str, Any]:
        """
        Track an LLM decision event.

        Args:
            session_id: Session ID
            reasoning: Decision reasoning
            alternatives: Alternative options considered
            confidence: Confidence score (0.0 to 1.0)
            branch_name: Branch name (default: "main")

        Returns:
            Event data
        """
        state_before = self.current_state.copy()

        response = self.session.post(
            f"{self.api_url}/api/sdk/events",
            json={
                "sessionId": session_id,
                "eventType": EventType.LLM_DECISION.value,
                "reasoning": reasoning,
                "alternativesConsidered": alternatives,
                "confidence": confidence,
                "stateBefore": state_before,
                "stateAfter": self.current_state.copy(),
                "branchName": branch_name,
            },
        )
        response.raise_for_status()
        return response.json()

    def update_state(self, key: str, value: Any):
        """Update the current state."""
        self.current_state[key] = value

    def complete_session(
        self,
        session_id: str,
        success: bool = True,
        failure_reason: Optional[str] = None,
        estimated_cost: Optional[float] = None,
        custom_metrics: Optional[Dict[str, float]] = None,
        duration_ms: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Complete a session with performance metrics.

        This is the recommended way to close sessions for performance monitoring.

        Args:
            session_id: Session ID
            success: Whether the session successfully completed its goal (default: True)
            failure_reason: If success=False, why did it fail?
            estimated_cost: Total estimated cost in USD for this session
            custom_metrics: Custom KPI metrics (e.g., {"customer_satisfaction": 4.5, "order_value": 129.99})
            duration_ms: Duration in milliseconds (auto-calculated if not provided)

        Returns:
            Updated session data

        Example:
            >>> client.complete_session(
            ...     session_id=session_id,
            ...     success=True,
            ...     estimated_cost=0.023,
            ...     custom_metrics={
            ...         "customer_satisfaction": 4.5,
            ...         "order_value": 129.99,
            ...         "items_processed": 7
            ...     }
            ... )
        """
        payload = {
            "status": "completed" if success else "failed",
            "success": success,
        }

        if failure_reason is not None:
            payload["failureReason"] = failure_reason
        if estimated_cost is not None:
            payload["estimatedCost"] = estimated_cost
        if custom_metrics is not None:
            payload["customMetrics"] = custom_metrics
        if duration_ms is not None:
            payload["durationMs"] = duration_ms

        response = self.session.patch(
            f"{self.api_url}/api/sdk/sessions/{session_id}",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def close_session(
        self,
        session_id: str,
        duration_ms: Optional[int] = None,
        success: Optional[bool] = None,
        failure_reason: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Mark a session as completed (legacy method).

        Note: Use complete_session() for better performance monitoring with custom metrics.

        Args:
            session_id: Session ID
            duration_ms: Duration in milliseconds
            success: Whether the session successfully completed its goal
            failure_reason: If success=False, why did it fail?

        Returns:
            Updated session data
        """
        return self.complete_session(
            session_id=session_id,
            success=success if success is not None else True,
            failure_reason=failure_reason,
            duration_ms=duration_ms,
        )

    def get_policies(self) -> list[dict[str, Any]]:
        """
        Fetch policy rules for the current project.

        Returns:
            List of policy rules
        """
        response = self.session.get(
            f"{self.api_url}/api/sdk/policies",
            params={"projectId": self.project_id},
        )
        response.raise_for_status()
        return response.json().get("rules", [])

    def get_session_overrides(self, session_id: str) -> list[dict[str, Any]]:
        """
        Fetch overrides for a specific session (edits made in the UI).

        Args:
            session_id: Session ID to get overrides for

        Returns:
            List of session overrides ordered by step number
        """
        response = self.session.get(
            f"{self.api_url}/api/sdk/sessions/{session_id}/overrides",
        )
        response.raise_for_status()
        return response.json().get("overrides", [])

    def get_promoted_overrides(self, agent_name: str) -> list[dict[str, Any]]:
        """
        Fetch promoted overrides for an agent (apply to all future runs).

        Args:
            agent_name: Agent name to get promoted overrides for

        Returns:
            List of promoted overrides ordered by step number
        """
        response = self.session.get(
            f"{self.api_url}/api/sdk/promoted-overrides",
            params={
                "projectId": self.project_id,
                "agentName": agent_name,
            },
        )
        response.raise_for_status()
        return response.json().get("overrides", [])

    def get_current_workflow_version(self, agent_name: str) -> Optional[dict[str, Any]]:
        """
        Get the current (latest) workflow version for an agent.

        Args:
            agent_name: Agent name

        Returns:
            Current workflow version info or None if no versions exist
        """
        response = self.session.get(
            f"{self.api_url}/api/sdk/workflow-version",
            params={
                "projectId": self.project_id,
                "agentName": agent_name,
            },
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json().get("version")

    # Cost calculation helpers
    @staticmethod
    def calculate_openai_cost(
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate cost for OpenAI API calls.

        Args:
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD

        Example:
            >>> cost = SentrialClient.calculate_openai_cost(
            ...     model="gpt-4",
            ...     input_tokens=1000,
            ...     output_tokens=500
            ... )
            >>> print(f"Cost: ${cost:.4f}")
        """
        # Pricing as of 2025 (per 1M tokens)
        pricing = {
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4o": {"input": 2.5, "output": 10.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "o1-preview": {"input": 15.0, "output": 60.0},
            "o1-mini": {"input": 3.0, "output": 12.0},
        }

        # Find matching model (handle versioned models like gpt-4-0613)
        model_key = None
        for key in pricing.keys():
            if model.startswith(key):
                model_key = key
                break

        if not model_key:
            # Default to gpt-4 pricing if unknown
            model_key = "gpt-4"

        rates = pricing[model_key]
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]

        return input_cost + output_cost

    @staticmethod
    def calculate_anthropic_cost(
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate cost for Anthropic API calls.

        Args:
            model: Model name (e.g., "claude-3-opus", "claude-3-sonnet")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pricing = {
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
        }

        model_key = None
        for key in pricing.keys():
            if model.startswith(key):
                model_key = key
                break

        if not model_key:
            model_key = "claude-3-sonnet"

        rates = pricing[model_key]
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]

        return input_cost + output_cost

