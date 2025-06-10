import os
from langchain_huggingface import HuggingFaceEmbeddings
import requests

API_URL = "https://router.huggingface.co/nebius/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

response = query({
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Bonjour comment ça va ?"
                }
                
            ]
        }
    ],
    "model": "mistralai/Mistral-Small-3.1-24B-Instruct-2503"
})

print(response["choices"][0]["message"])


import os
import requests
import pinecone
from dotenv import load_dotenv

load_dotenv()

# Setup for Mistral API
API_URL = "https://router.huggingface.co/nebius/v1/chat/completions"
HF_TOKEN =  "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"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

# Setup for Pinecone
api_key = "pcsk_4cgUGb_DnYNfZT3q8RyuMyPQSqgRU9NpiqF2LCZQsNDRV7Swo8W82feWgDpBVhikrpghMQ"
region = "us-east-1"

# Create Pinecone instance
pc = pinecone.Pinecone(api_key=api_key)

# Use an index
index_name = "cyber-rag-index"
index = pc.Index(index_name)

def query_pinecone(prompt, top_k=3):
    # We embedd the prompt first 
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorized_prompt = embedding_model.embed_query(prompt)



    # We query the index for relevant chunks for that prompt
    response = index.query(
        vector=vectorized_prompt,
        top_k=top_k,
        include_metadata=True
    )

    return [match['metadata']['text'] for match in response['matches']]

def build_augmented_prompt(prompt, context, retrieved_chunks):
    """
    Combines Pinecone results + chat context + prompt into final Mistral prompt.
    """
    prompt_parts = []

    # Add retrieved context first
    if retrieved_chunks:
        prompt_parts.append("Relevant context:\n" + "\n---\n".join(retrieved_chunks) + "\n")

    # Add chat history
    for msg in context:
        sender = msg.get("sender")
        text = msg.get("text")
        if sender == "user":
            prompt_parts.append(f"User: {text}")
        elif sender == "bot":
            prompt_parts.append(f"Bot: {text}")

    # Add final question
    prompt_parts.append(f"User: {prompt}")

    return "\n".join(prompt_parts)

def query_mistral(final_prompt):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": final_prompt
                    }
                ]
            }
        ],
        "model": "mistralai/Mistral-Small-3.1-24B-Instruct-2503"
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()["choices"][0]["message"]

def generate_response(prompt, context):
    #  Step 1: Query Pinecone
    retrieved_chunks = query_pinecone(prompt)

    #  Step 2: Build prompt with history + RAG
    final_prompt = build_augmented_prompt(prompt, context, retrieved_chunks)

    # Step 3: Query Mistral
    #response = query_mistral(final_prompt)
    return final_prompt
