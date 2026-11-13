# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.8-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from .fitness_tools import calculate_heart_rate_zones
from .firestore_tools import (
    add_exercise,
    get_exercise_details,
    get_recent_workout_logs,
    list_exercises,
    log_workout,
)
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from .image_tools import generate_fitness_image
from .maps_tools import geocode_address, search_nearby_places
from .nutrition_tools import get_food_nutrition
from .video_tools import generate_exercise_video

SANDBOX_RESOURCE_NAME = "projects/588570932746/locations/us-east1/reasoningEngines/3954361683459178496/sandboxEnvironments/8828000849646059520"
MEMORY_BANK_ID = "3954361683459178496"

code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """Save durable user facts and preferences to Memory Bank after each turn."""
    await callback_context.add_session_to_memory()
    return None


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from .a2ui_utils import a2ui_callback


def memory_bank_service_builder():
    """Builds the VertexAiMemoryBankService targeting the deployed Agent Engine."""
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-04-ec0b87ee001f",
        location="us-east1",
        agent_engine_id=MEMORY_BANK_ID,
    )


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are FitPulse Coach, an expert fitness, strength, and nutrition coach. "
        "You help athletes and fitness enthusiasts find exercises, learn proper movement mechanics, "
        "look up nutritional information for foods and ingredients, log completed workouts, "
        "compute cardiovascular heart rate training zones, find nearby gyms and parks, "
        "generate visual milestone badges and meal plating images, generate short exercise demonstration videos, and manage their training catalog. "
        "You remember the user's stated fitness goals, personal records, workout preferences, "
        "injuries, and dietary needs across conversations and use them to personalize your coaching. "
        "Critically, you always remember, track, and strictly respect all user allergies, food intolerances, "
        "and medical/dietary restrictions across sessions, never recommending foods or ingredients containing their allergens. "
        "When performing complex calculations (e.g. macro/calorie splits, periodization percentages, "
        "or 1-rep-max estimates), execute Python code in your Agent Engine sandbox."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        calculate_heart_rate_zones,
        get_food_nutrition,
        generate_fitness_image,
        generate_exercise_video,
        geocode_address,
        search_nearby_places,
        list_exercises,
        get_exercise_details,
        add_exercise,
        log_workout,
        get_recent_workout_logs,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
