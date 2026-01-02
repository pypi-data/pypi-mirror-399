from camel import CamelClient
from camel.agent import Agent
from camel.tools import Tool


def get_weather(location: str) -> str:
    return f"Weather in {location}: 72°F, sunny"


weather_tool = Tool(
    name="get_weather",
    description="Gets the current weather conditions for any city or location. Use this whenever the user asks about weather, temperature, or climate conditions.",
    schema={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "The city or location name"}
        },
        "required": ["location"],
    },
    function=get_weather,
)

client = CamelClient(model="gemma3:1b")
agent = Agent(client, tools=[weather_tool])

print("Running agent...")
result = agent.run("What's the weather in chennai?")
print(f"Result: {result}")
