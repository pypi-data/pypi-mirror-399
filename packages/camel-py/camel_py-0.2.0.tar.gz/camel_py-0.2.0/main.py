from camel import CamelClient


def main():
    print("💬 Simple Camel Chat (stream handled internally, type 'exit' to quit)\n")

    with CamelClient() as client:
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye!")
                break

            print("Assistant: ", end="", flush=True)
            response = client.stream(user_input)
            print(response.text)


if __name__ == "__main__":
    main()
