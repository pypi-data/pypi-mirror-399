import base64
import json
import logging
import re
from abc import abstractmethod

import requests
from dojo_sdk_core.settings import settings

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BasicCUA(BaseAgent):
    """Base class for Computer Use Agents with common functionality."""

    def __init__(
        self,
        image_context_length: int = 10,
        max_tokens: int = 4096,
        system_prompt_suffix: str = "",
        screen_size: tuple[int, int] = (1280, 800),
        verbose: bool = False,
    ):
        self.image_context_length = image_context_length
        self.max_tokens = max_tokens
        self.system_prompt_suffix = system_prompt_suffix
        self.screen_size = screen_size
        self.verbose = verbose

        # Image cache to eliminate redundant downloads
        self._image_cache = {}  # path -> base64_string
        self._cache_size_mb = 0.0
        self._max_cache_size_mb = 100.0

    @abstractmethod
    def history_to_messages(self, history: list):
        """Convert history steps to model-specific message format."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, task_instruction: str, obs: dict = None, messages: list = None):
        """Make a prediction using the model. Returns (reasoning, actions, raw_response)."""
        raise NotImplementedError

    def _trim_history_to_context_window(self, history: list) -> list:
        """Trim history to keep first step + last N steps within context window."""
        if len(history) <= self.image_context_length:
            return history
        return [history[0]] + history[-self.image_context_length :]

    def _get_cached_image(self, screenshot_path: str) -> str:
        """Get base64-encoded image from cache or download and cache it."""
        if screenshot_path in self._image_cache:
            return self._image_cache[screenshot_path]

        try:
            response = requests.get(f"{settings.dojo_http_endpoint}/image?path={screenshot_path}")
            screenshot_base64 = base64.b64encode(response.content).decode("utf-8")

            # Update cache
            self._image_cache[screenshot_path] = screenshot_base64
            self._cache_size_mb += len(screenshot_base64) / (1024 * 1024)

            # Prune if needed
            if self._cache_size_mb > self._max_cache_size_mb:
                self._prune_cache_to_context_window()

            return screenshot_base64

        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return ""

    def _prune_cache_to_context_window(self):
        """Remove old images from cache, keeping first + recent images."""
        if len(self._image_cache) <= self.image_context_length + 1:
            return

        # Cache keys are already in chronological order due to history trimming
        paths = list(self._image_cache.keys())

        # Keep first + last N
        paths_to_keep = [paths[0]] + paths[-(self.image_context_length) :]

        # Remove others and update size tracking
        for path in paths:
            if path not in paths_to_keep:
                image_data = self._image_cache[path]
                self._cache_size_mb -= len(image_data) / (1024 * 1024)
                del self._image_cache[path]

        logger.debug(f"Pruned images from cache, new cache size: ({self._cache_size_mb:.2f}MB)")

    def _repair_tool_arguments(self, args_str: str) -> dict | None:
        """Attempt to repair malformed JSON from tool call arguments.

        Handles common issues like:
        - Empty string arguments: "" -> None
        - Missing comma in coordinate arrays: [360 227] -> [360, 227]
        - Trailing garbage characters: }}] -> }
        """

        # Handle empty string
        if not args_str or args_str.strip() == "":
            logger.warning("Empty tool arguments, returning None")
            return None

        try:
            # Fix missing comma in coordinate arrays like [360 227] -> [360, 227]
            fixed = re.sub(r"\[(\d+)\s+(\d+)\]", r"[\1, \2]", args_str)

            # Find the first complete JSON object by tracking braces
            brace_count = 0
            end_idx = 0
            for i, char in enumerate(fixed):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            if end_idx > 0:
                fixed = fixed[:end_idx]

            return json.loads(fixed)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"JSON repair failed: {e}")
            return None

    def _manual_parse_tool_arguments(self, args_str: str) -> dict | None:
        """Attempt manual parsing of tool arguments for common patterns.

        This is a fallback when JSON parsing fails. It looks for patterns like:
        - action: click, coordinate: [100, 200]
        - action="click" coordinate="[100,200]"
        - {action:click,coordinate:[100,200]} (missing quotes)

        Returns:
            dict or None if parsing fails
        """
        if not args_str or not args_str.strip():
            return None

        try:
            result = {}

            # Try to extract action field
            action_patterns = [
                r'"action"\s*:\s*"([^"]+)"',  # "action": "click"
                r"'action'\s*:\s*'([^']+)'",  # 'action': 'click'
                r"action\s*:\s*([a-zA-Z_]+)",  # action: click (no quotes)
                r"action\s*=\s*['\"]([^'\"]+)['\"]",  # action="click"
            ]

            for pattern in action_patterns:
                match = re.search(pattern, args_str)
                if match:
                    result["action"] = match.group(1)
                    break

            if not result.get("action"):
                return None

            # Try to extract coordinate field
            coord_patterns = [
                r'"coordinate"\s*:\s*\[([^\]]+)\]',  # "coordinate": [100, 200]
                r"'coordinate'\s*:\s*\[([^\]]+)\]",  # 'coordinate': [100, 200]
                r"coordinate\s*:\s*\[([^\]]+)\]",  # coordinate: [100, 200]
            ]

            for pattern in coord_patterns:
                match = re.search(pattern, args_str)
                if match:
                    coord_str = match.group(1)
                    coords = [int(float(x.strip())) for x in coord_str.split(",")]
                    if len(coords) == 2:
                        result["coordinate"] = coords
                    break

            # Try to extract text field
            text_patterns = [
                r'"text"\s*:\s*"([^"]*)"',  # "text": "hello"
                r"'text'\s*:\s*'([^']*)'",  # 'text': 'hello'
                r"text\s*:\s*([^,}\s]+)",  # text: hello (no quotes, simple case)
            ]

            for pattern in text_patterns:
                match = re.search(pattern, args_str)
                if match:
                    result["text"] = match.group(1)
                    break

            # Try to extract scroll_amount
            scroll_patterns = [
                r'"scroll_amount"\s*:\s*(\d+)',
                r"'scroll_amount'\s*:\s*(\d+)",
                r"scroll_amount\s*:\s*(\d+)",
            ]

            for pattern in scroll_patterns:
                match = re.search(pattern, args_str)
                if match:
                    result["scroll_amount"] = int(match.group(1))
                    break

            # Only return if we at least got an action
            return result if result.get("action") else None

        except Exception as e:
            logger.debug(f"Manual parsing failed: {e}")
            return None
