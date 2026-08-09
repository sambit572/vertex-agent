import time
from openai import OpenAI, RateLimitError, APIError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

import config

groq_client = OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)
openrouter_client = OpenAI(api_key=config.OPENROUTER_API_KEY, base_url=config.OPENROUTER_BASE_URL)

# Circuit breaker state
_circuit_tripped_until = 0


def _circuit_is_open():
    return time.time() < _circuit_tripped_until


def _trip_circuit():
    global _circuit_tripped_until
    _circuit_tripped_until = time.time() + config.CIRCUIT_COOLDOWN_SECONDS
    print(f"[circuit-breaker] Groq tripped. Cooling down for {config.CIRCUIT_COOLDOWN_SECONDS}s.")


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=20),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(RateLimitError),
)
def _call_groq(messages, tools=None):
    return groq_client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=messages,
        tools=tools,
    )


def _call_openrouter(messages, tools=None):
    return openrouter_client.chat.completions.create(
        model=config.OPENROUTER_MODEL,
        messages=messages,
        tools=tools,
    )


def call_llm(messages, tools=None):
    """
    Circuit-breaker routed LLM call.
    Tries Groq first (fast). Falls back to OpenRouter if Groq
    is rate-limited repeatedly, cooling down before retrying Groq.
    """
    if not _circuit_is_open():
        try:
            return _call_groq(messages, tools)
        except RateLimitError:
            _trip_circuit()
        except APIError as e:
            print(f"[groq] API error, falling back: {e}")

    # Circuit open or Groq failed — use OpenRouter
    try:
        return _call_openrouter(messages, tools)
    except APIError as e:
        print(f"[openrouter] API error: {e}")
        raise