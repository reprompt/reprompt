from __future__ import annotations

import json
import os

import openai
from fastapi import FastAPI, Request
from starlette.responses import FileResponse

import reprompt

openai.api_key = os.getenv("OPENAI_API_KEY")
reprompt.init(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="api")


@app.post("/api/chat")
async def chat_with_openai(request: Request):
    body = await request.json()
    print(body)
    user_input = body["message"]

    edits = await reprompt.get_edits(user_input)
    prompt = """
You are an AI assistant tasked with drafting responses to incoming emails.
Your capabilities include understanding the content of each email, identifying the appropriate tone based on
the context, and formulating clear, concise, and polite responses.

"""

    # Incorporate edits from reprompt
    prompt += f"""
### EXAMPLE ANSWERS ###
{json.dumps(edits)}
"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
    )
    return {"response": response.choices[0].message.content}


@app.get("/")
async def read_index():
    return FileResponse("index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
