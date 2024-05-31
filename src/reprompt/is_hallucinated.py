import aiohttp
from . import config


def get_api_url():
    return f"{config.api_base_url}/api/v1/isHallucinated"


def get_headers():
    return {"apiKey": config.api_key, "Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}


def create_payload(prompt: str, response: str, user_input: str, debug: bool = True):
    return {"prompt": prompt, "response": response, "userInput": user_input, "debug": debug}


async def is_hallucinated(prompt: str, response: str, user_input: str, debug: bool = True) -> dict:
    url = get_api_url()
    payload = create_payload(prompt, response, user_input, debug)
    headers = get_headers()

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_message = await response.text()
                return {"error": f"Failed to check hallucination: ({response.status}) {error_message}"}
            return await response.json()
