from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyACRnbM9cr02QfaPqUOUQH-Mr2ySBcuBo4")

response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents="Who won the US open this year?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(
            google_search_retrieval=types.GoogleSearchRetrieval()
        )]
    )
)
print(response)