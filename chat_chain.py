from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1:70b", base_url="http://localhost:11434")

template = """You are a professional AI assistant helping users with technical and business questions.
Always answer clearly, step by step, and give examples when useful.

Question: {user_input}
"""

prompt = PromptTemplate(
    input_variables=["user_input"],
    template=template,
)

#chat_chain = LLMChain(llm=llm, prompt=prompt)

def get_answer(user_input: str) -> str:
    formatted_prompt = prompt.format(user_input=user_input) 
    result = llm.invoke(formatted_prompt)
    return result.content
