import json
from llm_client import call_llm
from tools import TOOL_SCHEMAS, TOOL_REGISTRY

SYSTEM_PROMPT = (
    "You are Vertex, a helpful personal AI agent for Sambit. "
    "You can call tools to open apps, search the web, and open/view URLs. "
    "If the user asks to 'open', 'see', 'show', or 'view' a GitHub PR, use open_browser "
    "with the URL format: https://github.com/<username>/<repo>/pull/<number>. "
    "Sambit's GitHub username is sambit572."
)


def run():
    print("Vertex is online. Type a command (or 'exit' to quit).")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Vertex: Shutting down.")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        response = call_llm(messages, tools=TOOL_SCHEMAS)
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"[tool] Calling {name}({args})")

                func = TOOL_REGISTRY.get(name)
                result = func(**args) if func else f"Unknown tool: {name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

            # Get final response after tool execution — no tools here, force a text summary
            followup = call_llm(messages, tools=None)
            reply = followup.choices[0].message.content

            if not reply:
                reply = "I got the tool results but had trouble summarizing them. Try rephrasing?"

            print(f"Vertex: {reply}")
            messages.append({"role": "assistant", "content": reply})
        else:
            reply = msg.content
            print(f"Vertex: {reply}")
            messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    run()