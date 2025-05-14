from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq

_ = load_dotenv(find_dotenv())
model = ChatGroq(model="llama3-8b-8192")