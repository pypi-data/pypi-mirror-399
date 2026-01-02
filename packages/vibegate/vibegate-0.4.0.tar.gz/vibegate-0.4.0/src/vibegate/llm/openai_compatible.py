"""OpenAI-compatible API provider for local model servers (vLLM, SGLang, LM Studio, etc.)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from vibegate.findings import Finding
from vibegate.llm.cache import LLMCache
from vibegate.llm.prompts import build_combined_prompt_json
from vibegate.llm.providers import CodeContext, LLMResponse

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """OpenAI-compatible API provider for local model inference.

    Works with local servers that implement the OpenAI chat completions API:
    - vLLM (https://docs.vllm.ai/en/latest/)
    - SGLang (https://sgl-project.github.io/)
    - LM Studio (https://lmstudio.ai/)
    - text-generation-webui with OpenAI extension
    - Any other local server implementing /v1/chat/completions
    """

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:8000/v1",
        cache_dir: str | None = None,
        temperature: float = 0.3,
        timeout_sec: int = 60,
        extra_headers: dict[str, str] | None = None,
    ):
        """Initialize OpenAI-compatible provider.

        Args:
            model: Model name to use (e.g., "Qwen/Qwen2.5-Coder-7B-Instruct")
            base_url: Base URL of the local server (default: http://localhost:8000/v1)
            cache_dir: Directory for caching LLM responses (default: .vibegate/llm_cache)
            temperature: Sampling temperature (lower = more deterministic)
            timeout_sec: Request timeout in seconds
            extra_headers: Optional additional HTTP headers
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.timeout_sec = timeout_sec
        self.extra_headers = extra_headers or {}
        self.cache = LLMCache(cache_dir) if cache_dir else None

    def is_available(self) -> bool:
        """Check if the local server is available.

        Returns:
            True if server is running and responding
        """
        try:
            # Try to get model list
            models_url = f"{self.base_url}/models"
            req = urllib.request.Request(
                models_url,
                headers={"Content-Type": "application/json", **self.extra_headers},
            )

            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    # Check if our model is in the list (if API returns models)
                    if "data" in data:
                        model_ids = [m.get("id", "") for m in data.get("data", [])]
                        if model_ids and self.model not in model_ids:
                            logger.warning(
                                f"Model {self.model} not found in server. Available: {model_ids}"
                            )
                    return True
                return False

        except Exception as e:
            logger.debug(f"OpenAI-compatible server not available: {e}")
            return False

    def get_model_info(self) -> dict[str, str]:
        """Get information about the current model.

        Returns:
            Dictionary with model metadata
        """
        return {
            "name": self.model,
            "provider": "openai_compatible",
            "base_url": self.base_url,
        }

    def _call_chat_completion(
        self, messages: list[dict[str, str]], request_json: bool = False
    ) -> str:
        """Call the OpenAI-compatible chat completions endpoint.

        Args:
            messages: List of message dicts with "role" and "content"
            request_json: Whether to request JSON output format

        Returns:
            Response text from the model

        Raises:
            Exception: If the API call fails
        """
        url = f"{self.base_url}/chat/completions"

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        # Request JSON output if supported (helps with structured outputs)
        if request_json:
            payload["response_format"] = {"type": "json_object"}

        data = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            **self.extra_headers,
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as response:
                response_data = json.loads(response.read().decode("utf-8"))

                # Extract content from OpenAI-format response
                choices = response_data.get("choices", [])
                if not choices:
                    raise ValueError("No choices in response")

                message = choices[0].get("message", {})
                content = message.get("content", "")

                return content.strip()

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            logger.error(f"HTTP error {e.code}: {error_body}")
            raise Exception(
                f"API call failed with status {e.code}: {error_body}"
            ) from e

        except urllib.error.URLError as e:
            logger.error(f"URL error: {e.reason}")
            raise Exception(f"Failed to connect to server: {e.reason}") from e

    def explain_finding(self, finding: Finding) -> str:
        """Generate a user-friendly explanation of a finding.

        Args:
            finding: The finding to explain

        Returns:
            Plain-English explanation
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get_explanation(finding.fingerprint, self.model)
            if cached:
                return cached

        # Build prompt
        from vibegate.llm.prompts import build_explanation_prompt

        prompt = build_explanation_prompt(finding)

        try:
            messages = [{"role": "user", "content": prompt}]
            explanation = self._call_chat_completion(messages)

            # Cache the result
            if self.cache:
                self.cache.save_explanation(
                    finding.fingerprint, self.model, explanation
                )

            return explanation

        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"Error generating explanation: {str(e)}"

    def generate_fix_prompt(self, finding: Finding, context: CodeContext) -> str:
        """Generate a detailed fix prompt for AI coding assistants.

        Args:
            finding: The finding to fix
            context: Code context

        Returns:
            Detailed fix prompt
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get_fix_prompt(finding.fingerprint, self.model)
            if cached:
                return cached

        # Build prompt
        from vibegate.llm.prompts import build_fix_prompt

        prompt = build_fix_prompt(finding, context)

        try:
            messages = [{"role": "user", "content": prompt}]
            fix_prompt = self._call_chat_completion(messages)

            # Cache the result
            if self.cache:
                self.cache.save_fix_prompt(finding.fingerprint, self.model, fix_prompt)

            return fix_prompt

        except Exception as e:
            logger.error(f"Failed to generate fix prompt: {e}")
            return f"Error generating fix prompt: {str(e)}"

    def process_finding(
        self, finding: Finding, context: CodeContext | None = None
    ) -> LLMResponse:
        """Process a finding and generate both explanation and fix prompt.

        This is more efficient than calling explain_finding and generate_fix_prompt
        separately, as it makes a single LLM call.

        Args:
            finding: The finding to process
            context: Optional code context

        Returns:
            LLMResponse with both explanation and fix prompt
        """
        # Check cache first
        if self.cache:
            cached_response = self.cache.get_combined(finding.fingerprint, self.model)
            if cached_response:
                return LLMResponse(
                    explanation=cached_response["explanation"],
                    fix_prompt=cached_response["fix_prompt"],
                    model_used=self.model,
                    cached=True,
                )

        # Build combined prompt requesting JSON output
        prompt = build_combined_prompt_json(finding, context)

        try:
            messages = [{"role": "user", "content": prompt}]
            # Request JSON format for structured output
            content = self._call_chat_completion(messages, request_json=True)

            # Try to parse as JSON first
            explanation, fix_prompt = self._parse_response(content)

            # Cache the result
            if self.cache:
                self.cache.save_combined(
                    finding.fingerprint, self.model, explanation, fix_prompt
                )

            return LLMResponse(
                explanation=explanation,
                fix_prompt=fix_prompt,
                model_used=self.model,
                cached=False,
            )

        except Exception as e:
            logger.error(f"Failed to process finding: {e}")
            return LLMResponse(
                explanation=f"Error: {str(e)}",
                fix_prompt=f"Error: {str(e)}",
                model_used=self.model,
                cached=False,
            )

    def _parse_response(self, content: str) -> tuple[str, str]:
        """Parse LLM response into explanation and fix prompt.

        Tries JSON parsing first, falls back to section-based parsing.

        Args:
            content: Raw LLM response

        Returns:
            Tuple of (explanation, fix_prompt)
        """
        # Try JSON parsing first (structured output)
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                # Check for standard field names
                explanation = (
                    data.get("explanation_simple")
                    or data.get("explanation")
                    or data.get("EXPLANATION")
                    or ""
                )
                fix_prompt = (
                    data.get("fix_prompt")
                    or data.get("FIX_PROMPT")
                    or data.get("fix")
                    or ""
                )

                if explanation or fix_prompt:
                    return explanation.strip(), fix_prompt.strip()

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # Not JSON, fall back to text parsing
            logger.debug(f"Response not JSON, using text parsing: {e}")

        # Fallback: parse text with section headers (same as Ollama)
        explanation = ""
        fix_prompt = ""

        if "## EXPLANATION" in content and "## FIX PROMPT" in content:
            parts = content.split("## FIX PROMPT")
            explanation = parts[0].replace("## EXPLANATION", "").strip()
            fix_prompt = parts[1].strip()
        elif "EXPLANATION:" in content and "FIX PROMPT:" in content:
            parts = content.split("FIX PROMPT:")
            explanation = parts[0].replace("EXPLANATION:", "").strip()
            fix_prompt = parts[1].strip()
        else:
            # Last resort: treat entire response as explanation
            explanation = content
            fix_prompt = "See explanation above for guidance on fixing this issue."

        return explanation, fix_prompt

    def process_cluster(self, cluster_description: str) -> str:
        """Process a tuning cluster and generate an explanation.

        Args:
            cluster_description: Description of the cluster pattern

        Returns:
            LLM-generated explanation of the pattern
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful coding assistant explaining patterns in code quality issues.",
                },
                {
                    "role": "user",
                    "content": f"Explain this pattern of false positives in a friendly way:\n\n{cluster_description}",
                },
            ]

            return self._call_chat_completion(messages)

        except Exception as e:
            logger.error(f"Failed to process cluster: {e}")
            return f"Error: {str(e)}"

    def process_finding_combined(
        self, finding: Finding, context: CodeContext | None = None
    ) -> LLMResponse:
        """Alias for process_finding for compatibility.

        Args:
            finding: The finding to process
            context: Optional code context

        Returns:
            LLMResponse with both explanation and fix prompt
        """
        return self.process_finding(finding, context)
