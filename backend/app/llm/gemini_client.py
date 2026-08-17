import os

from dotenv import load_dotenv
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    ThinkingConfig,
)


# ==========================================
# Environment
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found."
    )


# ==========================================
# Gemini Client
# ==========================================

client = genai.Client(
    api_key=API_KEY
)


class GeminiClient:

    def __init__(
        self,
        model: str = "gemini-3.6-flash"
    ):

        self.model = model

    # ======================================
    # Normal generation
    # ======================================

    def generate(
        self,
        prompt: str
    ) -> str:

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=GenerateContentConfig(

                max_output_tokens=3000,

                thinking_config=ThinkingConfig(
                    thinking_level="low"
                ),
            )
        )

        self._log_response_metadata(
            response
        )

        return (
            response.text or ""
        ).strip()

    # ======================================
    # Streaming generation
    # ======================================

    def generate_stream(
        self,
        prompt: str
    ):

        response_stream = (
            client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=GenerateContentConfig(

                    max_output_tokens=3000,

                    thinking_config=ThinkingConfig(
                        thinking_level="low"
                    ),
                )
            )
        )

        last_finish_reason = None
        last_usage = None

        for chunk in response_stream:

            # ----------------------------------
            # Capture candidate metadata
            # ----------------------------------

            candidates = getattr(
                chunk,
                "candidates",
                None
            )

            if candidates:

                candidate = candidates[0]

                finish_reason = getattr(
                    candidate,
                    "finish_reason",
                    None
                )

                if finish_reason is not None:

                    last_finish_reason = (
                        str(finish_reason)
                    )

            # ----------------------------------
            # Capture usage metadata
            # ----------------------------------

            usage = getattr(
                chunk,
                "usage_metadata",
                None
            )

            if usage:
                last_usage = usage

            # ----------------------------------
            # Stream text
            # ----------------------------------

            text = getattr(
                chunk,
                "text",
                None
            )

            if text:
                yield text

        # ======================================
        # Stream finished
        # ======================================

        print(
            "\n[LLM] Stream finished"
        )

        print(
            "[LLM] Finish reason:",
            last_finish_reason
        )

        if last_usage:

            print(
                "[LLM] Prompt tokens:",
                getattr(
                    last_usage,
                    "prompt_token_count",
                    None
                )
            )

            print(
                "[LLM] Output tokens:",
                getattr(
                    last_usage,
                    "candidates_token_count",
                    None
                )
            )

            print(
                "[LLM] Thinking tokens:",
                getattr(
                    last_usage,
                    "thoughts_token_count",
                    None
                )
            )

            print(
                "[LLM] Total tokens:",
                getattr(
                    last_usage,
                    "total_token_count",
                    None
                )
            )

    # ======================================
    # Response metadata
    # ======================================

    def _log_response_metadata(
        self,
        response
    ):

        print(
            "\n[LLM] Generation finished"
        )

        candidates = getattr(
            response,
            "candidates",
            None
        )

        if candidates:

            candidate = candidates[0]

            print(
                "[LLM] Finish reason:",
                getattr(
                    candidate,
                    "finish_reason",
                    None
                )
            )

        usage = getattr(
            response,
            "usage_metadata",
            None
        )

        if usage:

            print(
                "[LLM] Prompt tokens:",
                getattr(
                    usage,
                    "prompt_token_count",
                    None
                )
            )

            print(
                "[LLM] Output tokens:",
                getattr(
                    usage,
                    "candidates_token_count",
                    None
                )
            )

            print(
                "[LLM] Thinking tokens:",
                getattr(
                    usage,
                    "thoughts_token_count",
                    None
                )
            )

            print(
                "[LLM] Total tokens:",
                getattr(
                    usage,
                    "total_token_count",
                    None
                )
            )
            

# ==========================================
# Local test
# ==========================================

if __name__ == "__main__":

    gemini = GeminiClient()

    print(
        "Streaming test:\n"
    )

    for chunk in gemini.generate_stream(
        "Explain Nietzsche's idea "
        "of eternal recurrence."
    ):

        print(
            chunk,
            end="",
            flush=True
        )

    print()
            