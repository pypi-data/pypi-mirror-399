"""LangChain integration for Sentrial observability."""

from typing import Any, Dict, List, Optional
from uuid import UUID

try:
    from langchain_core.callbacks.base import BaseCallbackHandler
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.outputs import LLMResult
except ImportError:
    raise ImportError(
        "LangChain is required for this integration. "
        "Install it with: pip install langchain-core"
    )

from .client import SentrialClient


class SentrialCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler for Sentrial performance monitoring.
    
    Automatically tracks:
    - Agent reasoning (Chain of Thought)
    - Tool executions (with inputs/outputs)
    - Tool errors
    - LLM calls (optional)
    
    Usage:
        from sentrial import SentrialClient
        from sentrial.langchain import SentrialCallbackHandler
        
        client = SentrialClient(api_url="...", project_id="...")
        session_id = client.create_session(name="My Agent Run", agent_name="my_agent")
        handler = SentrialCallbackHandler(client, session_id)
        
        # Pass to LangChain agent
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            callbacks=[handler],
            verbose=True
        )
    """
    
    def __init__(
        self, 
        client: SentrialClient, 
        session_id: str,
        track_llm_calls: bool = False,
        verbose: bool = False
    ):
        """
        Initialize Sentrial callback handler.
        
        Args:
            client: SentrialClient instance
            session_id: Active session ID
            track_llm_calls: Whether to track individual LLM API calls (default: False)
            verbose: Print tracking info (default: False)
        """
        super().__init__()
        self.client = client
        self.session_id = session_id
        self.track_llm_calls = track_llm_calls
        self.verbose = verbose
        
        # Track tool runs in flight (run_id -> tool data)
        self.tool_runs: Dict[str, Dict[str, Any]] = {}
        
        # Track pending agent actions (for correlating with tool outputs)
        self.pending_actions: Dict[str, Dict[str, Any]] = {}
        
        # Track agent steps
        self.step_count = 0
        
        # Track last LLM output for reasoning
        self.last_llm_reasoning: Optional[str] = None
    
    def _log(self, message: str):
        """Log if verbose mode is enabled."""
        if self.verbose:
            print(f"[Sentrial] {message}")
    
    # ===== Agent Reasoning (Chain of Thought) =====
    
    def on_agent_action(
        self, 
        action: AgentAction, 
        *, 
        run_id: UUID, 
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """
        Capture agent reasoning and tool calls.
        """
        self.step_count += 1
        reasoning = action.log if action.log else f"Action: {action.tool}"
        tool_name = action.tool
        tool_input = action.tool_input
        
        self._log(f"Step {self.step_count}: Agent action - {tool_name}")
        
        # Store the pending action for correlation with tool output
        self.pending_actions[str(run_id)] = {
            "tool": tool_name,
            "input": tool_input,
            "reasoning": reasoning,
            "tracked": False,
            "step_number": self.step_count
        }
        
        # Track as tool_call with the available info
        input_dict = tool_input if isinstance(tool_input, dict) else {"input": str(tool_input) if tool_input else ""}
        
        self.client.track_tool_call(
            session_id=self.session_id,
            tool_name=tool_name,
            tool_input=input_dict,
            tool_output={"status": "executed"},
            reasoning=reasoning
        )
        
        # Mark as tracked
        self.pending_actions[str(run_id)]["tracked"] = True
    
    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """Track agent completion."""
        self._log("Agent finished")
        
        self.client.track_decision(
            session_id=self.session_id,
            reasoning=f"Agent completed: {finish.return_values.get('output', 'No output')}",
            confidence=1.0
        )
    
    # ===== Tool Execution =====
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """Buffer tool inputs for correlation with outputs."""
        tool_name = serialized.get("name", "unknown_tool")
        
        self._log(f"Tool started: {tool_name}")
        
        # Check if we have a pending action for this tool
        parent_id = str(parent_run_id) if parent_run_id else None
        pending = None
        if parent_id and parent_id in self.pending_actions:
            pending = self.pending_actions.get(parent_id)
        
        self.tool_runs[str(run_id)] = {
            "name": tool_name,
            "input": input_str,
            "pending_action": pending,
            "parent_run_id": parent_id
        }
    
    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """Track successful tool execution with full input/output."""
        run_data = self.tool_runs.pop(str(run_id), None)
        
        # Check if this was already tracked from on_agent_action
        parent_id = str(parent_run_id) if parent_run_id else None
        if parent_id and parent_id in self.pending_actions:
            pending = self.pending_actions[parent_id]
            if pending.get("tracked"):
                # Already tracked, just log
                self._log(f"Tool completed: {pending['tool']}")
                return
        
        # If we get here, it means on_agent_action didn't fire (common in new LangChain)
        # In this case, we should track it here with the last captured reasoning
        if run_data:
            tool_name = run_data["name"]
            tool_input = run_data["input"]
            
            self._log(f"Tool completed (no agent_action): {tool_name}")
            
            # Safely serialize output (might be ToolMessage or other object)
            if isinstance(output, str):
                output_value = output
            elif hasattr(output, 'content'):
                # ToolMessage object
                output_value = str(output.content)
            elif hasattr(output, '__dict__'):
                # Try to get a reasonable string representation
                output_value = str(output)
            else:
                output_value = str(output)
            
            # Parse input/output
            input_dict = {"input": tool_input} if isinstance(tool_input, str) else tool_input
            output_dict = {"output": output_value}
            
            # Use the last captured reasoning from LLM
            reasoning = self.last_llm_reasoning
            self.last_llm_reasoning = None  # Clear it after use
            
            self.client.track_tool_call(
                session_id=self.session_id,
                tool_name=tool_name,
                tool_input=input_dict,
                tool_output=output_dict,
                reasoning=reasoning,
            )
    
    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """Track tool errors."""
        run_data = self.tool_runs.pop(str(run_id), None)
        
        if run_data:
            tool_name = run_data["name"]
            tool_input = run_data["input"]
            
            self._log(f"Tool error: {tool_name} - {error}")
            
            input_dict = {"input": tool_input} if isinstance(tool_input, str) else tool_input
            
            self.client.track_tool_call(
                session_id=self.session_id,
                tool_name=tool_name,
                tool_input=input_dict,
                tool_output={"error": str(error), "error_type": type(error).__name__},
            )
    
    # ===== LLM Calls (Optional) =====
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """Track LLM calls if enabled."""
        if self.track_llm_calls:
            self._log(f"LLM call started: {len(prompts)} prompts")
    
    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """Track LLM responses and extract reasoning."""
        # Extract reasoning from the LLM output for the next tool call
        if response.generations and len(response.generations) > 0:
            generation = response.generations[0][0]
            if hasattr(generation, 'text'):
                text = generation.text
                # Try to extract "Thought:" from the output
                if 'Thought:' in text:
                    # Extract everything after "Thought:" and before "Action:"
                    thought_start = text.find('Thought:') + len('Thought:')
                    thought_end = text.find('Action:', thought_start)
                    if thought_end == -1:
                        thought_end = text.find('Final Answer:', thought_start)
                    if thought_end == -1:
                        thought_end = len(text)
                    reasoning = text[thought_start:thought_end].strip()
                    self.last_llm_reasoning = reasoning
                    self._log(f"Captured reasoning: {reasoning[:50]}...")
        
        if self.track_llm_calls:
            self._log(f"LLM call completed: {len(response.generations)} generations")
    
    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> None:
        """Track LLM errors if enabled."""
        if self.track_llm_calls:
            self._log(f"LLM error: {error}")
