from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict
import os


class AgentState(TypedDict):
    input: str
    plan: str
    result: str

def search_files(keyword, dir=".."):
    print("[DEBUG] search_files() called with:", keyword)
    results = []
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith(".txt"):
                try:
                    path = os.path.join(root, file)
                    print(f"[DEBUG] root {root} file {file}",root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        if keyword.lower() in f.read().lower():
                            results.append(path)

                except Exception as e:
                    continue
    if not results:
        return f"No files found containing the keyword '{keyword}'."
    
    return f"Files containing the keyword '{keyword}': " + ", ".join(results)

def simple_math(expression):
    print("[DEBUG] simple_math() called with:", expression)
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return "Invalid math expression."
    
llm = ChatOllama(model="llama3.1:70b", temperature=0.6)

graph = StateGraph(AgentState)

def think_step(state):
    print("[DEBUG] I'm in think step")
    user_input = state["input"]
    response = llm.invoke([
        HumanMessage(content=f"You are a smart assistant. The user said:'{user_input}'. If the user asks to calculate, say 'DO_MATH'. If the user asks to search files, say 'DO_SEARCH'. Otherwise, just answer directly.")
    ])
    state["plan"] = response.content.strip()
    return state

def act_step(state):
    print("[DEBUG] I'm in act step")
    
    plan = state["plan"]
    print(f"[DEBUG] plan is {plan}")
    user_input = state["input"]
    if "DO_MATH" in plan or not 'Invalid math expression' in plan:
        print(f"[INFO] Performing math operation : {user_input}")
        state["result"] = simple_math(user_input)
    elif "DO_SEARCH" in plan:
        keyword = user_input.replace("search", "").strip()
        state["result"] = search_files(keyword)
    else:
        reponse = llm.invoke([HumanMessage(content=user_input)])
        state["result"] = reponse.content
    return state

def output_step(state):
    print("[DEBUG] I'm in output step")
    return {"answer": state["result"]}


graph.add_node("think", think_step)
graph.add_node("act", act_step)
graph.add_node("output", output_step)

graph.add_edge("think", "act")
graph.add_edge("act", "output")
graph.add_edge("output", END)

graph.set_entry_point("think")

agent_app = graph.compile()
