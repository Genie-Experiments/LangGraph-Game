import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

model = ChatOpenAI(
    temperature=temperature,
    model_name=model_name,
    api_key=api_key
)

