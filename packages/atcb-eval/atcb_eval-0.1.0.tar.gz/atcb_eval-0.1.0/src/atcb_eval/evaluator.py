"""Multi-model evaluator for ATCB benchmark."""

import json
import math
import os
import re
import time
from typing import Any, Dict, Optional

from .types import AgentResponse, ToolUseCase

# Conditional imports for API clients
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class MultiModelEvaluator:
    """Evaluates multiple LLM models on tool-use calibration.

    Supports OpenAI, Anthropic, and Google models with graceful fallback
    to mock mode when API clients aren't available.

    Example:
        >>> evaluator = MultiModelEvaluator()
        >>> case = ToolUseCase(...)
        >>> response = evaluator.evaluate_case(case, "gpt-4o")
        >>> print(f"Tool: {response.selected_tool}, Confidence: {response.verbalized_confidence}")
    """

    SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
        # OpenAI models
        "gpt-4o": {"provider": "openai", "supports_logprobs": True},
        "gpt-4o-mini": {"provider": "openai", "supports_logprobs": True},
        "gpt-4-turbo": {"provider": "openai", "supports_logprobs": True},
        "gpt-4": {"provider": "openai", "supports_logprobs": True},
        # Anthropic models
        "claude-sonnet-4-20250514": {"provider": "anthropic", "supports_logprobs": False},
        "claude-3-5-sonnet-20241022": {"provider": "anthropic", "supports_logprobs": False},
        "claude-3-opus-20240229": {"provider": "anthropic", "supports_logprobs": False},
        "claude-3-5-haiku-20241022": {"provider": "anthropic", "supports_logprobs": False},
        # Google models
        "gemini-2.0-flash": {"provider": "google", "supports_logprobs": False},
        "gemini-1.5-pro": {"provider": "google", "supports_logprobs": False},
        "gemini-1.5-flash": {"provider": "google", "supports_logprobs": False},
    }

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """Initialize the evaluator with optional API keys.

        Args:
            api_keys: Optional dictionary mapping provider names to API keys.
                     If not provided, uses environment variables.
        """
        self.clients: Dict[str, Any] = {}
        api_keys = api_keys or {}

        if OPENAI_AVAILABLE:
            key = api_keys.get("openai") or os.environ.get("OPENAI_API_KEY")
            if key:
                self.clients["openai"] = openai.OpenAI(api_key=key)

        if ANTHROPIC_AVAILABLE:
            key = api_keys.get("anthropic") or os.environ.get("ANTHROPIC_API_KEY")
            if key:
                self.clients["anthropic"] = anthropic.Anthropic(api_key=key)

        if GOOGLE_AVAILABLE:
            key = api_keys.get("google") or os.environ.get("GOOGLE_API_KEY")
            if key:
                genai.configure(api_key=key)
                self.clients["google"] = genai

    def _build_prompt(self, case: ToolUseCase) -> str:
        """Build the evaluation prompt for a test case."""
        tools_desc = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in case.available_tools]
        )

        return f"""You are an AI assistant with access to the following tools:

{tools_desc}
- none: Do not use any tool (for conversational queries or when you should refuse)

User request: {case.query}

Respond in this EXACT JSON format:
{{
    "selected_tool": "<tool_name or 'none'>",
    "arguments": {{}},
    "confidence": <0.0 to 1.0 - how confident are you this is the correct tool choice?>,
    "reasoning": "<brief explanation>"
}}

Be calibrated about your confidence:
- 0.9-1.0: You are certain this is correct
- 0.7-0.9: You are fairly confident
- 0.5-0.7: You are unsure
- 0.0-0.5: You are guessing or should abstain"""

    def evaluate_case(self, case: ToolUseCase, model: str) -> AgentResponse:
        """Evaluate a single test case with a specific model.

        Args:
            case: The ToolUseCase to evaluate.
            model: Model identifier (e.g., "gpt-4o").

        Returns:
            AgentResponse containing the model's selection and confidence.
        """
        import random

        start_time = time.time()

        model_info = self.SUPPORTED_MODELS.get(
            model, {"provider": "mock", "supports_logprobs": False}
        )
        provider = model_info["provider"]
        prompt = self._build_prompt(case)

        selected_tool = "none"
        selected_args: Dict[str, Any] = {}
        verbalized_confidence = 0.5
        logprob_confidence: Optional[float] = None
        raw_response = ""

        try:
            if provider == "openai" and "openai" in self.clients:
                response = self.clients["openai"].chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=500,
                    logprobs=model_info["supports_logprobs"],
                    top_logprobs=5 if model_info["supports_logprobs"] else None,
                )

                raw_response = response.choices[0].message.content or ""

                # Extract logprob confidence if available
                if model_info["supports_logprobs"] and response.choices[0].logprobs:
                    logprobs = response.choices[0].logprobs.content
                    if logprobs:
                        avg_logprob = sum(t.logprob for t in logprobs[:20]) / min(
                            20, len(logprobs)
                        )
                        logprob_confidence = math.exp(avg_logprob)

            elif provider == "anthropic" and "anthropic" in self.clients:
                response = self.clients["anthropic"].messages.create(
                    model=model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw_response = response.content[0].text

            elif provider == "google" and "google" in self.clients:
                gen_model = self.clients["google"].GenerativeModel(model)
                response = gen_model.generate_content(prompt)
                raw_response = response.text

            else:
                # Mock mode for testing without API keys
                raw_response = self._mock_response(case)

            # Parse response
            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                selected_tool = parsed.get("selected_tool", "none")
                selected_args = parsed.get("arguments", {})
                verbalized_confidence = float(parsed.get("confidence", 0.5))

        except Exception as e:
            print(f"    Error evaluating {model}: {e}")

        latency = (time.time() - start_time) * 1000
        is_correct = selected_tool.lower().strip() == case.correct_tool.lower().strip()

        return AgentResponse(
            case_id=case.case_id,
            model=model,
            selected_tool=selected_tool,
            selected_args=selected_args,
            verbalized_confidence=min(1.0, max(0.0, verbalized_confidence)),
            logprob_confidence=logprob_confidence,
            is_correct=is_correct,
            latency_ms=latency,
            raw_response=raw_response[:500],
            category=case.category,
        )

    def _mock_response(self, case: ToolUseCase) -> str:
        """Generate mock response for testing without API access."""
        import random

        if case.difficulty == "easy":
            tool = case.correct_tool
            conf = 0.85 + random.random() * 0.15
        elif case.difficulty == "medium":
            tool = case.correct_tool if random.random() > 0.2 else "web_search"
            conf = 0.6 + random.random() * 0.3
        else:
            tool = case.correct_tool if random.random() > 0.4 else "none"
            conf = 0.3 + random.random() * 0.5

        return json.dumps(
            {
                "selected_tool": tool,
                "arguments": {},
                "confidence": round(conf, 2),
                "reasoning": "Mock response for testing",
            }
        )

    @classmethod
    def list_supported_models(cls) -> Dict[str, Dict[str, Any]]:
        """List all supported models and their capabilities.

        Returns:
            Dictionary mapping model names to their configuration.
        """
        return cls.SUPPORTED_MODELS.copy()
