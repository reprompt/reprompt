import aiohttp
from . import config


async def is_hallucinated_async(prompt: str, response: str, user_input: str) -> dict:
    url = f"{config.api_base_url}/api/v1/isHallucinated"
    payload = {"prompt": prompt, "response": response, "userInput": user_input}
    headers = {
        "apiKey": config.api_key,
        "Authorization": f"Bearer {config.api_key}",  # Assuming the same key is used for Bearer token
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_message = await response.text()
                return {"error": f"Failed to check hallucination: ({response.status}) {error_message}"}
            return await response.json()
