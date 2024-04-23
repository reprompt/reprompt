This directory stores each Python Package.


# Installing Reprompt

Specify the specific version of reprompt in your requirements.txt file.

```
reprompt==0.0.7.8
```

And install it.

```
pip install -r requirements.txt
```

## Initialize with API key

To use reprompt, you need to initialize it with an API key. Obtain your API key from the [Reprompt dashboard](https://app.repromptai.com/). Once you have your API key, initialize the reprompt package as follows:

![Screenshot 2024-04-17 at 5 01 07 PM](https://github.com/reprompt/reprompt/assets/1288339/afa3dc4f-0cc8-4b46-8a83-a3f19babfa8c)


```
import reprompt
reprompt.init(api_key="your_api_key_here")
```

If you omit initializing reprompt with an `api_key` it uses the environment variable `REPROMPT_API_KEY`.


## Implementing Edits


To implement edits based on feedback from Reprompt, use the get_edits function. This function sends a string to Reprompt and returns suggested edits, which can be used to generate preferential responses:

```python
from reprompt import get_edits

# Assuming `message` is the user's input
overrides = await get_edits(message)
```

## Add edits

Head over to [Reprompt Dashboard](https://app.repromptai.com/tune) and create a couple edits.

![](https://github.com/reprompt/reprompt/assets/1288339/85ff3dcc-1f97-4c7d-845f-00d3b49814a8)

### Simple Integration Example

```python
from __future__ import annotations

import json
import os

import openai
import reprompt

from fastapi import FastAPI, Request
from starlette.responses import FileResponse

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
```

### Integration tips

**What are edits?**
AI edits refer to the examples returned by the get_edits function. These edits are based on the feedback and adjustments made in the Reprompt dashboard, aimed at enhancing the model's responses.

**What should I do with IF statements in my prompt?**
If statements such as `If the email sounds angry or frustrated, start the reply with an apology.` or `If the received email is brief, keep the reply concise.` often don't work as expected in prompts. Instead of relying on conditional logic within the prompt, it's more effective to use examples. Providing GPT with clear examples of desired outputs can significantly improve the performance and relevance of the responses.

**Do I need to change anything in my prompt to work with get_edits?**

No significant changes are required in your prompt structure. The edits received from get_edits should be added to the end of your prompt as examples. These edits are designed to guide the model towards generating responses that align with your specific requirements.


_Before integrating edits_
Initially, the prompt might attempt to cover various scenarios with implicit IF statements or general instructions, lacking specificity or examples:

```
You are an AI assistant tasked with drafting responses to incoming emails. Your capabilities include understanding the content of each email, identifying the appropriate tone based on the context, and formulating clear, concise, and polite responses. Please ensure to apologize if the email sounds frustrated or angry, prioritize replies marked as urgent, and keep your responses brief if the original email is short.
```

_After integrating edits_
After integrating edits, the prompt includes specific examples that guide the AI in handling various types of emails. These examples act as models for the AI to follow, improving its ability to generate appropriate responses:

```
You are an AI assistant tasked with drafting responses to incoming emails. Your capabilities include understanding the content of each email, identifying the appropriate tone based on the context, and formulating clear, concise, and polite responses.

### EXAMPLE ANSWERS ###

${json.dumps(edits)}
```


**How do I handle hardcoded examples in my prompt?**

You should remove hardcoded examples from your prompt. This not only saves tokens but also allows the prompt to be more focused and targeted. Our platform enables your Product Manager (PM) to write examples that can be dynamically pulled in at query time, optimizing the prompt's effectiveness.


**What information do I need to provide with the user message?**

When using get_edits, you only need to tell us the user message. There's no need to include the entire prompt structure, as the edits provided will be appended to the bottom of your prompt as positive and negative examples.


**Is chat history or a session ID required?**
No, you don't need to provide chat history or a session ID. The get_edits functionality focuses on the current interaction.

**What should I do with IF statements in my prompt?**
IF statements often don't work as expected in prompts. Instead of relying on conditional logic within the prompt, it's more effective to use examples. Providing GPT with clear examples of desired outputs can significantly improve the performance and relevance of the responses.

**Should I always call json.dumps on the edits?**
It's not always necessary to use json.dumps on the edits unless you're incorporating them into a JSON-structured prompt or need to format them as a string for other reasons.

**When I make edits in the Reprompt dashboard, does it need to be Markdown or JSON?**
The format for editing examples should match the expected output format of your application. If you expect the output to be in Markdown, then the edits should also be made in Markdown to ensure consistency.


### Integration Example with a RAG

Here's how you might integrate Reprompt into a specific part of your FastAPI application, focusing on generating responses with OpenAI and using Reprompt for tracing and edits:


```python
from fastapi import FastAPI, HTTPException, Request, JSONResponse
import reprompt
from reprompt import FunctionTrace, write_traces, get_edits
import openai
import os
import weaviate
import json
import urllib.parse

app = FastAPI()

# Initialize OpenAI and Reprompt with API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
reprompt.init(api_key="your_reprompt_api_key_here", debug=False)

# Placeholder for Weaviate client initialization
weaviate_client = weaviate.Client("http://weaviate-instance:8080")

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    user_query = body.get("query", "")
    if not user_query:
        raise HTTPException(status_code=400, detail="No query provided")

    # Start tracing the chat function
    trace = FunctionTrace("chat", {"query": user_query})

    # Perform a semantic search with Weaviate
    weaviate_trace = FunctionTrace("weaviate_search", {"query": user_query})
    search_results = weaviate_search(user_query)
    weaviate_trace.end_trace({"results": search_results})

    # Fetch preferential edits from Reprompt
    edits_trace = FunctionTrace("fetch_edits", {"query": user_query})
    edits = await get_edits(user_query)
    edits_trace.end_trace({"edits": edits})

    # Construct the prompt with search results and edits
    prompt = construct_prompt(user_query, search_results, edits)

    # Generate a response using an LLM
    llm_trace = FunctionTrace("llm_generate_response", {"prompt": prompt})
    llm_response = generate_response_with_llm(prompt)
    llm_trace.end_trace({"response": llm_response})

    # Write all traces
    write_traces([trace, weaviate_trace, edits_trace, llm_trace])

    return JSONResponse(content={"response": llm_response})

def weaviate_search(query: str):
    # Implement the logic to search with Weaviate
    # Placeholder function
    return [{"text": "Document text", "metadata": {"filename": "doc1.pdf", "page_number": 5}}]

def construct_prompt(user_query: str, search_results: list, edits: dict):
    # Construct a detailed prompt for the LLM using the user query, search results, and edits
    # Adapted from the provided Bernina example to fit ChatWithYourDocs
    system_prompt = """
You are an AI assistant named ChatWithYourDocs. Your task is to analyze extracted parts of long documents and answer questions based on this information.

Respond to the user's question using the related knowledge.
Do not make up responses; if the answer is unknown, state that you do not know.
If additional information is required to accurately answer, request further details from the user.
Try to ground your answer based on the related knowledge provided.
Include the IDs of the knowledge you refer to in your response as related_knowledge_ids.
Never mention filenames or sections in the response.
For step by step instructions, use unordered lists so it's easy to read.
Do not use knowledge from unrelated documents.

The response should be in the following JSON format: {
  "response": "<answer in Markdown format>",
  "related_knowledge_ids": ["<id>"]
}

If you use a direct preferential answer for the question,
then do not populate the related_knowledge_ids unless specified in the preferential answer.
"""

    # Incorporate search results and edits into the prompt
    system_prompt += f"""
### RELATED KNOWLEDGE ###
{json.dumps(search_results)}
### PREFERENTIAL RELATED ANSWERS ###
{json.dumps(edits)}
"""

    return system_prompt


def generate_response_with_llm(prompt: str):
    # Call the OpenAI API to generate a response based on the constructed prompt
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.1,
        messages=[
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": message}
        ],
        response_format={ "type": "json_object" }
    )

    bot_response_json = json.loads(response.choices[0].message.content)
    markdown_response = bot_response_json["response"]

```


## Tracing with Function Trace

Sending traces to reprompt allows you to replay the chat history and directly use it to edit the responses.

To trace function calls in your application, use the `FunctionTrace` class. Here's an example of how to trace a function:

```python
from reprompt.tracing import FunctionTrace

def your_function_to_trace():
    # Your function code here
    pass

trace = FunctionTrace("your_function_name", {"arg1": "value1"})
your_function_to_trace()
trace.end_trace({"result": "your_function_result"})
```

This will automatically collect the traces and upload them.
![Screenshot 2024-04-17 at 5 01 54 PM](https://github.com/reprompt/reprompt/assets/1288339/2eb0f04e-741f-49af-9ef9-b3c130e79248)

### Tracing Example

Here is an example if you are building an AI chain if you're using FastAPI + Weaviate + OpenAI.

```python
from fastapi import FastAPI, HTTPException, Request, JSONResponse
import reprompt
from reprompt import FunctionTrace, write_traces

app = FastAPI()

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    user_query = body.get("query", "")

    # Start tracing the entire process
    trace = FunctionTrace("semantic_response", {"query": user_query})

    # Perform a semantic search with Weaviate
    weaviate_trace = FunctionTrace("weaviate_search", {"query": user_query})
    search_results = weaviate_search(user_query)
    weaviate_trace.end_trace({"results": search_results})

    # Generate a response using an LLM based on the search results
    llm_trace = FunctionTrace("llm_generate_response", {"search_results": search_results})
    llm_response = llm_generate_response(search_results)
    llm_trace.end_trace({"response": llm_response})

    # End tracing the entire process
    trace.end_trace({"response": llm_response})

    # Write all traces
    write_traces([trace, weaviate_trace, llm_trace])

    return JSONResponse(content={"response": llm_response})

def weaviate_search(query: str):
    # Implement the logic to search with Weaviate

def llm_generate_response(search_results):
    # Implement the logic to generate a response using an LLM

```
