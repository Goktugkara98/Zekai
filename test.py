from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "https://openrouter.ai",
    "X-Title": "OpenRouter",
  },
  extra_body={},
  model="nousresearch/deephermes-3-mistral-24b-preview:free",
  messages=[
    {
      "role": "user",
      "content": "Hello, this is a test message"
    }
  ]
)
print(completion.choices[0].message.content)