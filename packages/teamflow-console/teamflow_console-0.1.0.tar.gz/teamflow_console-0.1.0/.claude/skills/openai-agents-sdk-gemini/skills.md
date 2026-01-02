---
name: openai-agents-sdk-gemini
version: 1.0.0
description: Comprehensive OpenAI Agents SDK integration with Gemini API, supporting tools, functions, handoffs, and session management
author: Claude Code Skill
license: MIT
tags:
  - openai-agents
  - gemini
  - ai-sdk
  - tools
  - functions
  - handoffs
  - sessions
  - multi-agent
requirements:
  - agents>=0.15.0
  - openai>=1.0.0
  - python-dotenv>=1.0.0
  - asyncio
  - pydantic>=2.0.0
...

# OpenAI Agents SDK with Gemini API Skill

A comprehensive skill that enables you to build powerful AI agents using OpenAI's Agents SDK with Google's Gemini models. This skill provides complete integration including tools, functions, handoffs, and session management.

## Features

- **Multi-Model Support**: Use Gemini 2.5 Flash, Pro, and other models through OpenAI-compatible interface
- **Tool Integration**: Create and use custom tools with your agents
- **Function Calling**: Leverage Gemini's native function calling capabilities
- **Handoffs**: Transfer conversations between specialized agents
- **Session Management**: Maintain conversation state across multiple interactions
- **Parallel Execution**: Run multiple tools and agents concurrently
- **Error Handling**: Robust error handling and retry mechanisms
- **Streaming**: Real-time response streaming for better UX

## Quick Setup

### 1. Install Dependencies

```bash
pip install openai-agents python-dotenv pydantic
```

### 2. Set Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Basic Usage

```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
import os

# Initialize Gemini provider
provider = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Create model
model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash-lite",
)

# Create agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model=model,
)

# Run agent
runner = Runner(agent=agent)
result = await runner.run("Hello, how are you?")
print(result.final_output)
```

## Core Components

### 1. Agent Creation

```python
from agents import Agent
from typing import List

# Simple agent
agent = Agent(
    name="Weather Assistant",
    instructions="You are a weather assistant. Provide weather information in a friendly way.",
    model=model,
)

# Agent with tools
agent_with_tools = Agent(
    name="Weather Agent",
    instructions="You are a weather expert. Use the get_weather tool to fetch current weather data.",
    model=model,
    tools=[get_weather_tool],
)

# Specialized agent with handoffs
specialized_agent = Agent(
    name="Weather Specialist",
    instructions="You specialize in weather analysis and forecasting.",
    model=model,
    tools=[get_weather_tool, analyze_weather_pattern],
    handoffs=[temperature_specialist, forecast_specialist],
)
```

### 2. Tool Creation

```python
from agents import function_tool
import requests
from typing import Optional

@function_tool
def get_weather(location: str, units: str = "metric") -> str:
    """
    Fetch current weather information for a given location.

    Args:
        location: The city or location name
        units: Temperature units (metric, imperial, or kelvin)
    """
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = "http://api.weatherapi.com/v1/current.json"

    response = requests.get(
        f"{base_url}?key={api_key}&q={location}&aqi=no"
    )

    if response.status_code == 200:
        data = response.json()
        temp = data['current']['temp_c'] if units == "metric" else data['current']['temp_f']
        condition = data['current']['condition']['text']
        humidity = data['current']['humidity']
        wind_kph = data['current']['wind_kph']

        return f"""
        Weather in {location}:
        🌡️ Temperature: {temp}°{'C' if units == 'metric' else 'F'}
        ☁️ Condition: {condition}
        💧 Humidity: {humidity}%
        💨 Wind: {wind_kph} km/h
        """
    else:
        return f"Sorry, I couldn't fetch weather data for {location}."

@function_tool
async def search_web(query: str, num_results: int = 5) -> str:
    """
    Search the web for information.

    Args:
        query: Search query
        num_results: Number of results to return
    """
    # Implement web search using your preferred API
    # This is a placeholder implementation
    return f"Searching for: {query} (returning {num_results} results)"
```

### 3. Agent Handoffs

```python
from agents import handoff

# Create specialized agents
temperature_agent = Agent(
    name="Temperature Specialist",
    instructions="You specialize in temperature analysis and heat patterns.",
    model=model,
)

forecast_agent = Agent(
    name="Forecast Specialist",
    instructions="You specialize in weather forecasting and predictions.",
    model=model,
)

# Main agent with handoffs
main_agent = Agent(
    name="Weather Central",
    instructions="""
    You are a central weather assistant. For temperature-specific questions,
    hand off to the Temperature Specialist. For forecast questions,
    hand off to the Forecast Specialist.
    """,
    model=model,
    handoffs=[
        handoff(temperature_agent, "temperature_analysis"),
        handoff(forecast_agent, "weather_forecast"),
    ],
)

# Example usage with handoffs
runner = Runner(agent=main_agent)
result = await runner.run(
    "What's the temperature trend for next week?"
)
# Will automatically hand off to forecast_agent
```

### 4. Session Management

```python
from agents import Runner, Agent
import asyncio

# CORRECT: Using built-in session management
from agents import SQLiteSession

# Create a session
session = SQLiteSession("conversation_123")

# First turn
result = await Runner.run(
    agent,
    "What's the weather in London?",
    session=session
)
print(result.final_output)

# Second turn - agent automatically remembers context
result = await Runner.run(
    agent,
    "How about tomorrow?",
    session=session
)
print(result.final_output)
```

### 5. Multi-Agent Collaboration

```python
from agents import Agent, Runner, handoff
import asyncio

# Create specialized agents
research_agent = Agent(
    name="Research Specialist",
    instructions="You research and gather information from multiple sources.",
    model=model,
    tools=[search_web, fetch_document],
)

analysis_agent = Agent(
    name="Analysis Specialist",
    instructions="You analyze data and provide insights.",
    model=model,
    tools=[analyze_data, create_charts],
)

report_agent = Agent(
    name="Report Writer",
    instructions="You compile information into well-structured reports.",
    model=model,
    tools=[generate_report, export_to_pdf],
)

# Coordinator agent
coordinator = Agent(
    name="Project Coordinator",
    instructions="""
    You coordinate multi-agent workflows. Break down complex tasks
    and delegate to appropriate specialists.
    """,
    model=model,
    handoffs=[
        handoff(research_agent, "research"),
        handoff(analysis_agent, "analysis"),
        handoff(report_agent, "report"),
    ],
)

async def run_complex_task(task: str):
    """Execute a complex task using multiple agents"""
    # CORRECT: The coordinator will break down the task and hand off as needed
    result = await Runner.run(
        coordinator,
        f"Complete this task: {task}\n\n"
        "Break it down into research, analysis, and reporting phases."
    )
    return result
```

### 6. Streaming Responses

```python
from agents import Runner, Agent
import asyncio

async def stream_response(agent: Agent, message: str):
    """Stream agent responses in real-time"""
    print("Response: ", end="", flush=True)

    # CORRECT: Stream usage
    async for event in Runner.run_streamed(agent, message):
        if event.type == "agent_step_stream":
            for chunk in event.output:
                print(chunk.content, end="", flush=True)

    print()  # New line after completion

# Usage
await stream_response(weather_agent, "Tell me about today's weather forecast")
```

### 7. Error Handling and Retries

```python
from agents import Runner, Agent
from typing import Optional
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def run_with_retry(agent: Agent, message: str, max_retries: int = 3):
    """Run agent with automatic retry on errors"""
    for attempt in range(max_retries):
        try:
            # CORRECT: Direct Runner.run usage
            result = await Runner.run(agent, message)
            return result.final_output
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logging.error("All retry attempts failed")
                return f"Sorry, I encountered an error: {str(e)}"
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

    return None

# Usage
response = await run_with_retry(weather_agent, "What's the weather in Paris?")
```

## Advanced Features

### 1. Custom Model Configuration

```python
from agents import OpenAIChatCompletionsModel, AsyncOpenAI

# Configure Gemini with custom settings
provider = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
    timeout=60.0,
    max_retries=3,
)

model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash-lite",  # Experimental model
    temperature=0.7,
    top_p=0.9,
    max_tokens=2048,
    presence_penalty=0.1,
    frequency_penalty=0.1,
)
```

### 2. Tool Result Caching

```python
from functools import lru_cache
from typing import Dict, Any
import hashlib
import json

class CachedTool:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds

    def _hash_key(self, args: Dict[str, Any]) -> str:
        """Create hash key from function arguments"""
        key_str = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def is_cached(self, key: str) -> bool:
        """Check if result is cached and not expired"""
        if key not in self.cache:
            return False

        import time
        if time.time() - self.cache[key]["timestamp"] > self.ttl:
            del self.cache[key]
            return False

        return True

    def get_cached(self, key: str) -> Any:
        """Get cached result"""
        return self.cache[key]["data"]

    def set_cache(self, key: str, data: Any):
        """Set cached result"""
        import time
        self.cache[key] = {
            "data": data,
            "timestamp": time.time(),
        }

# Usage with tools
cached_weather = CachedTool(ttl_seconds=600)  # 10 minute cache

@function_tool
def get_weather_cached(location: str) -> str:
    """Get weather with caching"""
    key = cached_weather._hash_key({"location": location})

    if cached_weather.is_cached(key):
        print("Returning cached weather data")
        return cached_weather.get_cached(key)

    # Fetch fresh data
    weather_data = get_weather(location)
    cached_weather.set_cache(key, weather_data)

    return weather_data
```

### 3. Tool Input Validation

```python
from pydantic import BaseModel, Field
from typing import Literal
import re

class WeatherInput(BaseModel):
    location: str = Field(
        min_length=2,
        max_length=100,
        description="City or location name"
    )
    units: Literal["metric", "imperial", "kelvin"] = Field(
        default="metric",
        description="Temperature units"
    )

    def validate_location(cls, v):
        """Validate location format"""
        if not re.match(r'^[a-zA-Z\s,-]+$', v):
            raise ValueError("Location contains invalid characters")
        return v.title()

@function_tool
def get_weather_validated(input_data: WeatherInput) -> str:
    """Get weather with validated input"""
    return get_weather(input_data.location, input_data.units)
```

## Best Practices

### 1. Agent Instructions

- Be specific about the agent's role and capabilities
- Include examples of desired behavior
- Set clear boundaries for what the agent should and shouldn't do
- Include formatting instructions for consistent output

### 2. Tool Design

- Keep tools focused on single responsibilities
- Use clear, descriptive names
- Include comprehensive docstrings
- Validate inputs and handle errors gracefully
- Use appropriate return types

### 3. Session Management

- Store only necessary conversation history
- Implement context windows to manage memory
- Use session IDs for multi-user scenarios
- Clear sensitive data when appropriate

### 4. Error Handling

- Always handle API failures gracefully
- Implement exponential backoff for retries
- Provide helpful error messages to users
- Log errors for debugging

### 5. Performance

- Use streaming for long responses
- Cache expensive operations
- Implement rate limiting for API calls
- Consider parallel execution for independent tasks

## Troubleshooting

### Common Issues

1. **API Key Errors**

   ```python
   # Verify your API key is set correctly
   import os
   api_key = os.getenv("GEMINI_API_KEY")
   if not api_key:
       raise ValueError("GEMINI_API_KEY not found in environment")
   ```

2. **Rate Limiting**

   ```python
   # Implement rate limiting
   import time
   from typing import Dict

   class RateLimiter:
       def __init__(self, calls_per_minute: int = 60):
           self.calls_per_minute = calls_per_minute
           self.calls = []

       def wait_if_needed(self):
           now = time.time()
           # Remove calls older than 1 minute
           self.calls = [c for c in self.calls if now - c < 60]

           if len(self.calls) >= self.calls_per_minute:
               sleep_time = 60 - (now - self.calls[0])
               time.sleep(sleep_time)

           self.calls.append(now)
   ```

3. **Model Not Available**
   ```python
   # Check model availability
   async def check_model_availability(model_name: str):
       try:
           response = await provider.models.retrieve(model_name)
           return True
       except:
           return False
   ```

## Complete Example

Here's a complete weather assistant implementation using all the features:

```python
import asyncio
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from agents import (
    Agent, Runner, function_tool, handoff,
    AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
)
from pydantic import BaseModel
import requests
import json
import logging

# Configuration
set_tracing_disabled(True)
logging.basicConfig(level=logging.INFO)

# Initialize Gemini provider
provider = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)

model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash-lite",
    temperature=0.7,
)

# Tool schemas
class WeatherInput(BaseModel):
    location: str = Field(min_length=2, max_length=100)
    units: str = Field(default="metric", regex="^(metric|imperial|kelvin)$")

# Tools
@function_tool
async def get_weather(location: str, units: str = "metric") -> str:
    """Fetch current weather for a location"""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather API key not configured"

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data["current"]
            location_name = data["location"]["name"]

            temp = current["temp_c"] if units == "metric" else current["temp_f"]
            unit_symbol = "°C" if units == "metric" else "°F"

            return f"""
📍 Location: {location_name}
🌡️ Temperature: {temp}{unit_symbol}
☁️ Condition: {current['condition']['text']}
💧 Humidity: {current['humidity']}%
💨 Wind: {current['wind_kph']} km/h
📊 Pressure: {current['pressure_mb']} mb
            """
        else:
            return f"Error fetching weather data: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@function_tool
async def get_forecast(location: str, days: int = 3) -> str:
    """Get weather forecast for upcoming days"""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            location_name = data["location"]["name"]
            forecast_days = data["forecast"]["forecastday"]

            forecast_text = f"📍 {location_name} - {days}-Day Forecast:\n\n"

            for day in forecast_days:
                date = day["date"]
                max_temp = day["day"]["maxtemp_c"]
                min_temp = day["day"]["mintemp_c"]
                condition = day["day"]["condition"]["text"]
                rain_chance = day["day"]["daily_chance_of_rain"]

                forecast_text += f"📅 {date}\n"
                forecast_text += f"🌡️ {min_temp}°C - {max_temp}°C\n"
                forecast_text += f"☁️ {condition}\n"
                forecast_text += f"🌧️ {rain_chance}% chance of rain\n\n"

            return forecast_text
        else:
            return f"Error fetching forecast: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Specialized agents
temperature_agent = Agent(
    name="Temperature Specialist",
    instructions="You specialize in temperature data and heat patterns. Provide detailed temperature analysis.",
    model=model,
)

forecast_agent = Agent(
    name="Forecast Specialist",
    instructions="You specialize in weather forecasting and predictions. Analyze forecast trends.",
    model=model,
)

# Main weather agent
weather_agent = Agent(
    name="Weather Assistant",
    instructions="""
    You are a helpful weather assistant. Provide weather information in a clear,
    friendly format with emojis for better readability.

    - Use the get_weather tool for current conditions
    - Use the get_forecast tool for predictions
    - Hand off to Temperature Specialist for detailed temperature analysis
    - Hand off to Forecast Specialist for advanced forecasting questions

    Always include relevant emojis and format your responses for easy reading.
    """,
    model=model,
    tools=[get_weather, get_forecast],
    handoffs=[
        handoff(temperature_agent, "temp_analysis"),
        handoff(forecast_agent, "forecast_analysis"),
    ],
)

# CORRECT: Using built-in session management
async def main():
    # Create a session for conversation history
    session = SQLiteSession("weather_chat_123")

    print("Weather Assistant Chat (type 'quit' to exit)")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye! 👋")
            break

        print("\nAssistant: ", end="", flush=True)

        # CORRECT: Direct Runner.run with session
        result = await Runner.run(
            weather_agent,
            user_input,
            session=session
        )
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## Contributing

This skill is open for contributions. Please feel free to:

- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## Migration Guide

### From Old (Incorrect) API to New (Correct) API

| OLD (Incorrect)                | NEW (Correct)                         |
| ------------------------------ | ------------------------------------- |
| `runner = Runner(agent=agent)` | Use `Runner.run()` directly           |
| `await runner.run(message)`    | `await Runner.run(agent, message)`    |
| `Runner.run(agent, input)`     | `await Runner.run(agent, message)`    |
| `runner.run_stream()`          | `Runner.run_streamed(agent, message)` |

### Quick Migration

```python
# OLD CODE - DON'T USE
runner = Runner(agent=agent)
result = await runner.run("Hello")

# NEW CODE - USE THIS
result = await Runner.run(agent, "Hello")
```

## Quick Reference Card

```python
# Basic Usage
result = await Runner.run(agent, "message")
result = Runner.run_sync(agent, "message")

# With Options
result = await Runner.run(agent, "message", max_turns=5, session=session)

# Streaming
async for event in Runner.run_streamed(agent, "message"):
    # Handle events

# Sessions
session = SQLiteSession("session_id")
result = await Runner.run(agent, "message", session=session)
```

## License

MIT License - feel free to use this skill in your projects!

## Support

For issues or questions:

1. Check this documentation
2. Review the OpenAI Agents SDK documentation: https://openai.github.io/openai-agents-python/
3. Check Gemini API documentation: https://ai.google.dev/gemini-api/docs
4. Create an issue in the repository
