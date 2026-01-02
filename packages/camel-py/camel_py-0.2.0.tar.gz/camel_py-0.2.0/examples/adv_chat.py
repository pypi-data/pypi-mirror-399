"""
Advanced Example: CamelClient with context persistence

- Saves conversation context to disk (JSON file).
- Reloads context in a new client.
- Demonstrates model listing and switching.
"""

import json
from pathlib import Path
from camel import CamelClient

CONTEXT_FILE = Path("chat_context.json")


def save_context_to_file(ctx: list[int]):
    with open(CONTEXT_FILE, "w") as f:
        json.dump(ctx, f)


def load_context_from_file() -> list[int] | None:
    if CONTEXT_FILE.exists():
        with open(CONTEXT_FILE, "r") as f:
            return json.load(f)
    return None


def main():
    print("🤖 Advanced Camel Chat (with context persistence)\n")

    with CamelClient(model="gemma3:1b") as client:
        # Try loading previous context if available
        prev_ctx = load_context_from_file()
        if prev_ctx:
            client.load_context(prev_ctx)
            print("✅ Previous conversation context loaded!\n")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye!")

                # Save context for next run
                ctx = client.save_context()
                if ctx:
                    save_context_to_file(ctx)
                    print(f"💾 Context saved to {CONTEXT_FILE}")
                break

            print("Assistant: ", end="", flush=True)
            response = client.stream(user_input)
            print(response.text)  # newline after stream


if __name__ == "__main__":
    main()
