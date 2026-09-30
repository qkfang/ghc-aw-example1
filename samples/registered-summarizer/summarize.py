"""Registered AI solution (AI-0001) - summarises a policy document with Azure OpenAI."""
import os
import sys

from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-06-01",
)


def summarize(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarise the document in 5 bullet points."},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(summarize(open(sys.argv[1], encoding="utf-8").read()))
