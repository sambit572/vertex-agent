from llm_client import call_llm

SYSTEM_PROMPT = (
    "You are Vertex, a helpful personal AI agent for Sambit. "
    "Respond concisely and clearly."
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

        response = call_llm(messages)
        reply = response.choices[0].message.content
        print(f"Vertex: {reply}")

        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    run()