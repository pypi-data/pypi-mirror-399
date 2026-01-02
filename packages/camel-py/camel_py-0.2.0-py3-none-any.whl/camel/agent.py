from camel.tools import Tool


class Agent:
    def __init__(self, client, tools: list[Tool]):
        self.client = client
        self.tools = {t.name: t for t in tools}
        self.user_model = client.model
        self._ensure_functiongemma()

    def _ensure_functiongemma(self):
        if not self.client._model_installed("functiongemma:270m"):
            print("FunctionGemma not found. Installing...")
            self.client.pull("functiongemma:270m")

    def run(self, prompt: str):
        ollama_tools = [self._tool_to_ollama(t) for t in self.tools.values()]
        messages = [{"role": "user", "content": prompt}]

        self.client.model = "functiongemma:270m"
        response = self.client.chat_with_tools(messages, tools=ollama_tools)

        tool_calls = response.raw.get("message", {}).get("tool_calls", [])

        if tool_calls:
            tool_call = tool_calls[0]
            tool_name = tool_call["function"]["name"]
            args = tool_call["function"]["arguments"]

            if not tool_name or tool_name not in self.tools:
                self.client.model = self.user_model
                return self.client.chat(prompt).text

            try:
                result = self.tools[tool_name].run(args)
            except Exception as e:
                self.client.model = self.user_model
                return self.client.chat(f"{prompt}\n\nError using tool: {e}").text

            self.client.model = self.user_model
            final_prompt = f"{prompt}\n\nTool '{tool_name}' returned: {result}\n\nProvide a natural response."
            final = self.client.chat(final_prompt)
            return final.text

        self.client.model = self.user_model
        return self.client.chat(prompt).text

    def _tool_to_ollama(self, tool: Tool):
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.schema,
            },
        }
