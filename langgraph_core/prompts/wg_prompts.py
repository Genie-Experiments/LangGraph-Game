from langchain_core.prompts import PromptTemplate

# Prompt for getting a question in the word game
get_question_prompt = PromptTemplate.from_template(
    """You are a word detective. The user has chosen a word from this list: {words}.
Ask a unique, descriptive yes/no/maybe question (not a guess) to help narrow it down.
Avoid repeating previous questions: {asked}.
This is question {question_number} of {max_q}.
Do NOT guess the word — just ask a useful question.
Do NOT return anything other than the question. 
Here is an example response: Is it a living thing?"""
)

# Prompt for guessing the word in the word game
guess_word_prompt = PromptTemplate.from_template(
    """You are a word detective. The possible words are: {words}.
Based on these question-answer pairs:
{qa}
Which word do you think the user picked? Make SURE to ONLY return ONE word from the list.
Do NOT include any other statements other than the guess word.
Here is an example response: Kiwi!"""
)