"""Data types for ATCB benchmark."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolUseCase:
    """A single tool use test case.

    Attributes:
        case_id: Unique identifier for this test case.
        query: The user query/request.
        available_tools: List of tool definitions available to the agent.
        correct_tool: The name of the correct tool to use (or "none").
        correct_args: The correct arguments for the tool call.
        difficulty: Difficulty level ("easy", "medium", "hard").
        category: Task category for analysis.

    Example:
        >>> case = ToolUseCase(
        ...     case_id="case_001",
        ...     query="What is 25 * 47?",
        ...     available_tools=[{"name": "calculator", "description": "..."}],
        ...     correct_tool="calculator",
        ...     correct_args={"expression": "25 * 47"},
        ...     difficulty="easy",
        ...     category="clear_match"
        ... )
    """

    case_id: str
    query: str
    available_tools: List[Dict[str, Any]]
    correct_tool: str
    correct_args: Dict[str, Any]
    difficulty: str
    category: str


@dataclass
class AgentResponse:
    """Agent's response to a tool use case.

    Attributes:
        case_id: Reference to the test case.
        model: Model identifier that generated this response.
        selected_tool: The tool the agent selected.
        selected_args: Arguments the agent provided.
        verbalized_confidence: Agent's self-reported confidence (0-1).
        logprob_confidence: Confidence from token log-probabilities (if available).
        is_correct: Whether the tool selection was correct.
        latency_ms: Response time in milliseconds.
        raw_response: The raw text response from the model.
        category: Category of the original test case.
    """

    case_id: str
    model: str
    selected_tool: str
    selected_args: Dict[str, Any]
    verbalized_confidence: float
    logprob_confidence: Optional[float]
    is_correct: bool
    latency_ms: float
    raw_response: str = ""
    category: str = ""


@dataclass
class ToolDefinition:
    """Definition of a tool available to the agent.

    Attributes:
        name: Tool name.
        description: Human-readable description.
        parameters: Dictionary of parameter names to types.
    """

    name: str
    description: str
    parameters: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API calls."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


# Standard tool definitions
STANDARD_TOOLS = [
    ToolDefinition(
        name="calculator",
        description="Perform mathematical calculations. Input: expression (string)",
        parameters={"expression": "string"},
    ),
    ToolDefinition(
        name="web_search",
        description="Search the web for current information",
        parameters={"query": "string"},
    ),
    ToolDefinition(
        name="get_weather",
        description="Get current weather for a location",
        parameters={"location": "string"},
    ),
    ToolDefinition(
        name="send_email",
        description="Send an email to a recipient",
        parameters={"to": "string", "subject": "string", "body": "string"},
    ),
    ToolDefinition(
        name="get_stock_price",
        description="Get current stock price for a ticker symbol",
        parameters={"symbol": "string"},
    ),
    ToolDefinition(
        name="translate",
        description="Translate text to target language",
        parameters={"text": "string", "target_language": "string"},
    ),
    ToolDefinition(
        name="create_calendar_event",
        description="Create a calendar event",
        parameters={"title": "string", "date": "string", "time": "string"},
    ),
    ToolDefinition(
        name="set_reminder",
        description="Set a reminder for a specific time",
        parameters={"message": "string", "time": "string"},
    ),
    ToolDefinition(
        name="get_news",
        description="Get latest news headlines",
        parameters={"topic": "string"},
    ),
    ToolDefinition(
        name="convert_currency",
        description="Convert amount between currencies",
        parameters={"amount": "number", "from": "string", "to": "string"},
    ),
]
