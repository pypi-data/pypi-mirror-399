from inspect_ai.model import (
    ModelAPI,
    modelapi,
    GenerateConfig,
    ModelOutput,
    ChatMessage,
    ChatMessageAssistant,
    ChatCompletionChoice,
    ContentText
)
import os
import requests
import uuid
from openai import OpenAI
from anthropic import Anthropic
# The 'name' argument is the prefix you will use in the CLI
# e.g., --model casimats:model_name
@modelapi(name="casimats")
class CasiMatsModelAPI(ModelAPI):
    async def generate(
        self,
        input: list[ChatMessage],
        tools: list[dict],
        tool_choice: any,
        config: GenerateConfig,
    ) -> ModelOutput:
        
        # 1. Extract the prompt from the input messages
        # Depending on your backend, you might need to format this 
        # into a single string or keep it as a list of dicts.
        prompt = input[-1].text 
        values=self.model_name.split("/", 2)
        provider_version=values[0]
        provider_name = values[1]
        model_name = values[2]
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
        # 2. Call your custom backend (Example: a placeholder request)
        # In production, use an async HTTP client like 'httpx' here.
        # Test GCG Agent (Upstream)
        if(provider_name=="openai"):
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found")
            BASE_URL = "http://98.91.36.205/"+provider_version  # switch to /v0 or /v1 if needed
            USER_ID = "mcnairshah"

            session_id = str(uuid.uuid4())
            client = OpenAI(
                base_url=f"{BASE_URL}/openai/v1",
                api_key=f"rt_{USER_ID}_{OPENAI_API_KEY}",
                default_headers={"X-RedTeam-Session-ID": session_id},
            )

            resp = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = resp.choices[0].message.content
        elif(provider_name=="custom"):
            response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": model_name, 
                "messages": [{"role": "user", "content": prompt}]
            }
        )
            response_text = response.json()["choices"][0]["message"]["content"]
        elif(provider_name=="anthropic"):
            BASE_URL = "http://98.91.36.205/"+provider_version  # switch to /v0 or /v1 if needed
            USER_ID = "mcnairshah"
            ANTHROPIC_KEY = ANTHROPIC_API_KEY

            session_id = str(uuid.uuid4())

            client = Anthropic(
                base_url=f"{BASE_URL}/anthropic",
                auth_token=f"rt_{USER_ID}_{ANTHROPIC_KEY}",
                default_headers={"X-RedTeam-Session-ID": session_id},
            )

            msg = client.messages.create(
                model=model_name,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = msg.content[0].text
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

        # 3. Create the completion choice
        choice = ChatCompletionChoice(
            message=ChatMessageAssistant(
                content=[ContentText(text=response_text)]
            ),
            stop_reason="stop"
        )

        # 4. Return the standard ModelOutput
        return ModelOutput(
            model=self.model_name,
            choices=[choice],
        )