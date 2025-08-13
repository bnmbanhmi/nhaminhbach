# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""this is a test message. response with a test message"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""**Understanding the Intent**

I began by searching Google for \"test message\" to grasp the user's intent. Analyzing the results, I'm now honing in on the optimal response based on the various search outcomes. I'm focusing on identifying patterns to determine the most fitting reply.


**Formulating a Response**

I've moved on to the next step, analyzing the search results. I'm carefully sifting through the data to pinpoint the best way to craft the reply to the \"test message\". My focus is on synthesizing these findings into the most appropriate response. I'm aiming to offer the most relevant reply based on the gathered information.


**Exploring \"Test Message\"**

I've been examining the concept of a \"test message\" from various technical viewpoints. It appears to primarily function as a pre-flight check, akin to a dress rehearsal before a major performance. This allows for validation, debugging, and refinement before broader dissemination. I'm currently assessing its implications across different communication channels.


**Interpreting User Intent**

I've determined the user's \"test message\" is a functionality check within our AI interaction. It's a quick assessment to verify operational readiness. Considering the user's expertise, the test serves as a simple confirmation of the AI's functionality. My response should acknowledge the test and affirm system health.


"""),
                types.Part.from_text(text="""This is a test response to your test message. The system is functioning correctly."""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
