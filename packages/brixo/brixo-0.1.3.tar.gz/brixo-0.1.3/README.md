# Brixo Python SDK

The **Brixo Python SDK** lets you instrument AI agents and capture high-quality interaction traces for analysis in the Brixo platform. It is designed to be lightweight, explicit, and easy to integrate into existing agent code.

---

## Compatibility

- Python 3.10+

---

## Installation

Install the SDK from PyPI:

```bash
pip install brixo
```

---

## Authentication

### Create an API key

1. Create a Brixo account @ https://app.brixo.com/sign_up
2. Once logged in, generate a new API key from the instructions page
3. Export it as an environment variable:

```bash
export BRIXO_API_KEY=<your_api_key>
```

The Brixo SDK will automatically read this value at runtime.

---

## Quickstart (copy/paste)

Create a minimal file that instruments a single interaction:

```bash
export BRIXO_API_KEY=<your_api_key>
cat > main.py <<'PY'
from brixo import Brixo

Brixo.init(
    app_name="my-app",
    environment="development",
)

@Brixo.interaction("Hello World Interaction")
def handle_user_input(user_input: str):
    Brixo.begin_context(
        user={"id": "1", "name": "Jane Doe"},
        input=user_input,
    )
    response = f"You said: {user_input}"
    Brixo.end_context(output=response)
    print(response)

def main():
    while True:
        user_input = input("User: ")
        handle_user_input(user_input)

if __name__ == "__main__":
    main()
PY
python main.py
```

What you should see:

- Your console echoes responses like `You said: <input>`
- A new trace appears in Brixo Live View shortly after each interaction: https://app.brixo.com/traces/live

---

## Instrumentation Quickstart

The typical flow is:

1. Initialize Brixo once at application startup
2. Wrap each *user interaction* with `@Brixo.interaction`
3. Attach context (user, customer, session, input, output)
4. Let the interaction finish so traces can be flushed

---

## Example

Below is a minimal but complete example that instruments a single agent interaction loop.

Create a file called `main.py`:

```python
# --- Brixo SDK import ---
# Import the Brixo SDK so we can instrument and send interaction traces to Brixo.
from brixo import Brixo
from my_agent import agent

# --- Brixo interaction boundary ---
# Mark ONE bounded user interaction (one request -> one response) so Brixo can group
# spans/attributes into a single trace and flush it when this function returns.

@Brixo.interaction("Main Agent Execution")
def handle_user_input(user_input: str):

    # --- Brixo context start ---
    # Attach contextual metadata to the current trace
    Brixo.begin_context(
        account={"id": "1", "name": "ACME, Inc."},
        user={"id": "1", "name": "John Doe"},
        session_id="session-123",
        metadata={"foo": "bar"},
        input=user_input,
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )

    handle_agent_response(response)


def handle_agent_response(response):
    """Extracts the final agent output and updates the trace."""

    final_text = response["messages"][-1].content

    # --- Brixo context update ---
    # Add/update attributes after the agent has produced output.
    Brixo.end_context(output=final_text)

def main():
    # --- Brixo SDK initialization ---
    # Initialize once at startup, before any instrumented code runs.
    Brixo.init(
        app_name="my-app",
        environment="production",
    )

    while True:
        user_input = input("User: ")
        handle_user_input(user_input)

if __name__ == "__main__":
    main()
```

Run the example:

```bash
python main.py
```

---

## Key Concepts

### Concepts at a glance

- **Interaction boundary**: one user request -> one response
- **Context lifecycle**: `begin_context` early, `update_context` for mid-flight, `end_context` to close
- **Flush timing**: traces are exported when the interaction function returns

### `Brixo.init(...)`

Initializes the SDK. Call **once** at application startup.

Arguments and value formats:

- `app_name`: `str` logical name for your application or agent; cannot be `None`
- `environment`: `str` such as `development`, `staging`, `production`; cannot be `None`
- `api_key`: `str` or `None`; defaults to `BRIXO_API_KEY`
- `filter_openinference_spans`: `bool` or `None` to drop OpenInference spans on export
- `filter_traceloop_spans`: `bool` or `None` to drop Traceloop spans on export

Usage:

```python
Brixo.init(
    app_name="my-app",
    environment="production",
    api_key="brx_123456",
    filter_openinference_spans=True,
    filter_traceloop_spans=True,
)
```

---

### `@Brixo.interaction(name)`

Marks a single, bounded **user interaction**.

Arguments and value formats:

- `name`: `str` or `None` descriptive interaction name

Usage:

```python
@Brixo.interaction("Main Agent Execution")
def handle_user_input(user_input: str):
    ...
```

Guidelines:

- Use one interaction per user request
- The function must terminate (no infinite loops)
- Choose descriptive names - they improve trace readability

---

### `Brixo.begin_context(...)`

Attaches structured metadata to the current interaction trace.

Arguments and value formats:

- `account`: `dict` or `None` with any of: `id`, `name`, `logo_url`, `website_url` (all `str`)
- `user`: `dict` or `None` with any of: `id`, `name`, `email` (all `str`)
- `session_id`: `str` or `None` logical session identifier
- `metadata`: `dict` or `None` of arbitrary key/value data
- `input`: `str` or `None` raw user input
- `output`: `str` or `None` output if available at start

Usage:

```python
Brixo.begin_context(
    account={
        "id": "acct_123",
        "name": "ACME, Inc.",
        "logo_url": "https://example.com/logo.png",
        "website_url": "https://acme.com",
    },
    user={
        "id": "user_456",
        "name": "Jane Doe",
        "email": "jane@example.com",
    },
    session_id="session-123",
    metadata={"plan": "pro", "feature": "search"},
    input="Find me the latest quarterly report.",
    output="",
)
```

---

### `Brixo.update_context(...)`

Adds or updates attributes **after** the interaction has started and leaves the interaction context open.

Arguments and value formats:

- `account`: `dict` or `None` with any of: `id`, `name`, `logo_url`, `website_url` (all `str`)
- `user`: `dict` or `None` with any of: `id`, `name`, `email` (all `str`)
- `session_id`: `str` or `None` logical session identifier
- `metadata`: `dict` or `None` of arbitrary key/value data
- `input`: `str` or `None` raw user input
- `output`: `str` or `None` output or intermediate result

Usage:

```python
Brixo.update_context(
    account={
        "id": "acct_123",
        "name": "ACME, Inc.",
        "logo_url": "https://example.com/logo.png",
        "website_url": "https://acme.com",
    },
    user={
        "id": "user_456",
        "name": "Jane Doe",
        "email": "jane@example.com",
    },
    session_id="session-123",
    metadata={"latency_ms": 1200, "tool": "search"},
    input="Find me the latest quarterly report.",
    output="Intermediate tool summary...",
)
```

Typical use cases:

- Derived metrics
- Tool results or summaries

---

### `Brixo.end_context(...)`

Adds or updates attributes **after** the interaction has started and then explicitly closes the interaction context.

Arguments and value formats:

- `account`: `dict` or `None` with any of: `id`, `name`, `logo_url`, `website_url` (all `str`)
- `user`: `dict` or `None` with any of: `id`, `name`, `email` (all `str`)
- `session_id`: `str` or `None` logical session identifier
- `metadata`: `dict` or `None` of arbitrary key/value data
- `input`: `str` or `None` raw user input
- `output`: `str` or `None` final agent output

Usage:

```python
Brixo.end_context(
    account={
        "id": "acct_123",
        "name": "ACME, Inc.",
        "logo_url": "https://example.com/logo.png",
        "website_url": "https://acme.com",
    },
    user={
        "id": "user_456",
        "name": "Jane Doe",
        "email": "jane@example.com",
    },
    session_id="session-123",
    metadata={"feedback_score": 5},
    input="Find me the latest quarterly report.",
    output="Here is the latest quarterly report summary...",
)
```

Typical use cases:

- Final agent output

---

## Best Practices

- **One interaction = one user request**
- Keep interaction functions short and bounded
- Use descriptive interaction names
- Attach inputs early and outputs late
- Initialize Brixo early at startup; if you rely on auto-instrumentation, import those
  libraries after `Brixo.init(...)`

---

## Troubleshooting

- **Missing traces**: Confirm `BRIXO_API_KEY` is set and that `Brixo.init(...)` runs before instrumented code.
- **Nothing in Live View**: Check https://app.brixo.com/traces/live and allow a few seconds after each interaction.
- **No internet or proxy issues**: Ensure your runtime can reach `app.brixo.com`.

---

## Support

If you have questions or run into issues:

- Check the Brixo [Live View](https://app.brixo.com/traces/live) for trace visibility
- Reach out to the Brixo team at support@brixo.com

Happy instrumenting 🚀
