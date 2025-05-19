# 🧠 LangGraph Game App

This project is a LangGraph-based multi-game application built with Python, LangChain, Groq, and Streamlit. It features two games:
- 🔢 Number Guessing Game
- 💡 Word Clue Guesser

The backend is powered by FastAPI and LangGraph agents, while the frontend is a Streamlit interface for interactive play.

---

## 🚀 Getting Started
1. Install the required packages:
   ```
   pip install -r requirements.txt
    ```
   (Note: For this project, you will need python 3.12 or above)
   
2. Setup your .env file with the necessary environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=your_openai_model
   ```
  However, if you are using Groq, you will need to set the following environment variables:
   ```
   export GROQ_API_KEY=your_groq_api_key
   ```
   Following that, go to your utils/model.py file and add this:
   ```from langchain_groq import ChatGroq```

     ``` _ = load_dotenv(find_dotenv())```
     ``` model = ChatGroq(model="your-model-name") ```

(Note: You can use either OpenAI or Groq, but not both at the same time. Make sure to comment out the one you are not using in the `model.py` file.)

3. Run this command to make your run.sh file executable:
    ```
       chmod +x run.sh
    ```

4. Run the application:
   ```
   ./run.sh
   ```

