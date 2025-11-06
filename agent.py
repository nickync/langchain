from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Tuple
import os


class AgentState(TypedDict):
    input: str
    plan: str
    result: str
    error: str
    iterations: int
    history: List[str]
    next_action: str  # Used for routing
    conversation_history: List[Tuple[str, str]]  # List of (user_message, agent_response) tuples

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
        result = eval(expression, {"__builtins__": {}})
        return {"success": True, "result": str(result), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Invalid math expression: {str(e)}"}
    
#llm = ChatOllama(model="llama3.1:70b", temperature=0.6)
llm = ChatOllama(model="deepseek-r1", temperature=0.6)

graph = StateGraph(AgentState)

def think_step(state):
    print("[DEBUG] I'm in think step (iteration", state.get("iterations", 0) + 1, ")")
    user_input = state["input"]
    iterations = state.get("iterations", 0)
    error = state.get("error", "")
    history = state.get("history", [])
    result = state.get("result", "")
    conversation_history = state.get("conversation_history", [])
    
    # Build context from conversation history
    context = ""
    if conversation_history:
        context += "\n\nPrevious conversation:\n"
        # Include last 5 conversation turns for context
        for user_msg, agent_msg in conversation_history[-5:]:
            context += f"User: {user_msg}\n"
            context += f"Assistant: {agent_msg}\n"
    
    # Build context from current attempt history
    if history:
        context += "\nPrevious attempts in this turn:\n" + "\n".join(history[-3:])  # Last 3 attempts
    
    if error:
        context += f"\nLast error: {error}"
    
    if result and iterations > 0:
        context += f"\nPrevious result: {result}"
    
    # Increment iteration count
    state["iterations"] = iterations + 1
    state["error"] = ""  # Clear previous error
    
    print("[DEBUG] Invoking llm in think step")
    prompt = (
        "You are a smart assistant. Choose ONE action based on the user's message:\n\n"
        "USE DO_MATH ONLY when the user asks a clear arithmetic calculation (numbers + operations):\n"
        "  Example: 'what is 2+2' → DO_MATH: 2+2\n"
        "  Example: 'calculate 10 * 5' → DO_MATH: 10*5\n\n"
        "USE DO_SEARCH ONLY when the user EXPLICITLY asks to search, find, or look for FILES:\n"
        "  Example: 'search for files containing python' → DO_SEARCH: python\n"
        "  Example: 'find files with error' → DO_SEARCH: error\n"
        "  Example: 'look for files about machine learning' → DO_SEARCH: machine learning\n"
        "  DO NOT use DO_SEARCH for general questions, explanations, or information requests!\n\n"
        "USE ANSWER for everything else (questions, explanations, conversations, etc.):\n"
        "  Example: 'what is Python?' → ANSWER: Python is a programming language...\n"
        "  Example: 'explain machine learning' → ANSWER: Machine learning is...\n"
        "  Example: 'how does this work?' → ANSWER: [explanation]\n"
        "  Example: 'tell me about X' → ANSWER: [information about X]\n\n"
        "IMPORTANT: When in doubt, use ANSWER. Only use DO_SEARCH when user explicitly mentions searching for files.\n\n"
        "Respond in STRICT format:\n"
        "- DO_MATH: <python_arithmetic_expression>\n"
        "- DO_SEARCH: <keyword_or_phrase>\n"
        "- ANSWER: <concise_answer>"
    )
    if context:
        prompt += context
    prompt += f"\n\nCurrent user message: {user_input}"
    
    response = llm.invoke([HumanMessage(content=prompt)])
    plan = response.content.strip()
    print("[DEBUG] Response from llm in think step:", plan)
    state["plan"] = plan
    return state

def act_step(state):
    print("[DEBUG] I'm in act step")
    
    plan = state.get("plan", "").strip()
    print(f"[DEBUG] plan is {plan}")
    user_input = state["input"]
    history = state.get("history", [])
    
    try:
        if plan.startswith("DO_MATH"):
            expr = plan.split(":", 1)[1].strip() if ":" in plan else user_input
            print(f"[INFO] Performing math operation on expression: {expr}")
            math_result = simple_math(expr)
            if math_result["success"]:
                state["result"] = math_result["result"]
                state["error"] = ""
                history.append(f"Math: {expr} → {math_result['result']}")
            else:
                state["error"] = math_result["error"]
                state["result"] = ""
                history.append(f"Math failed: {expr} → {math_result['error']}")
                
        elif plan.startswith("DO_SEARCH"):
            # Safeguard: Check if user actually requested a file search
            search_keywords = ["search", "find", "look for", "look up", "file", "files"]
            user_lower = user_input.lower()
            is_search_request = any(keyword in user_lower for keyword in search_keywords)
            
            if not is_search_request:
                # False positive - treat as ANSWER instead
                print(f"[WARNING] DO_SEARCH triggered but user didn't explicitly request search. Treating as ANSWER.")
                response = llm.invoke([HumanMessage(content=user_input)])
                state["result"] = response.content
                state["error"] = ""
                history.append(f"Answer (corrected from false search): {response.content[:100]}...")
            else:
                keyword = plan.split(":", 1)[1].strip() if ":" in plan else user_input
                print(f"[INFO] Searching for: {keyword}")
                search_result = search_files(keyword)
                state["result"] = search_result
                state["error"] = ""
                history.append(f"Search: {keyword} → {search_result[:100]}...")
            
        elif plan.startswith("ANSWER"):
            answer = plan.split(":", 1)[1].strip() if ":" in plan else ""
            state["result"] = answer or ""
            state["error"] = ""
            history.append(f"Answer: {answer[:100]}...")
        else:
            print("[INFO] Falling back to LLM for direct answer")
            response = llm.invoke([HumanMessage(content=user_input)])
            state["result"] = response.content
            state["error"] = ""
            history.append(f"Direct LLM response: {response.content[:100]}...")
            
    except Exception as e:
        error_msg = f"Action failed: {str(e)}"
        print(f"[ERROR] {error_msg}")
        state["error"] = error_msg
        state["result"] = ""
        history.append(f"Error: {error_msg}")
    
    state["history"] = history[-5:]  # Keep last 5 history entries
    return state

def validate_step(state):
    """Validate if the result is satisfactory or needs more work"""
    print("[DEBUG] I'm in validate step")
    
    result = state.get("result", "")
    error = state.get("error", "")
    iterations = state.get("iterations", 0)
    user_input = state["input"]
    plan = state.get("plan", "")
    max_iterations = 5
    
    next_action = "output"  # Default to output
    
    # Check max iterations
    if iterations >= max_iterations:
        print(f"[INFO] Max iterations ({max_iterations}) reached")
        next_action = "output"
    # If there's an error, we should retry
    elif error:
        print(f"[INFO] Error detected, retrying: {error}")
        next_action = "think"
    # If result is empty or invalid, retry
    elif not result or result.strip() == "":
        print("[INFO] Empty result, retrying")
        next_action = "think"
    else:
        # Use LLM to validate if this is a satisfactory answer
        try:
            validation_prompt = (
                f"User asked: {user_input}\n"
                f"Agent plan was: {plan}\n"
                f"Agent result: {result}\n\n"
                "Is this result satisfactory and complete? Respond with ONLY one word:\n"
                "- 'satisfactory' if the result fully answers the user's question\n"
                "- 'retry' if the result is incomplete, incorrect, or needs more work"
            )
            validation = llm.invoke([HumanMessage(content=validation_prompt)])
            decision = validation.content.strip().lower()
            print(f"[INFO] Validation decision: {decision}")
            
            if "retry" in decision or "incomplete" in decision or "incorrect" in decision:
                next_action = "think"
            else:
                next_action = "output"
        except Exception as e:
            print(f"[WARNING] Validation step failed: {e}, defaulting to output")
            next_action = "output"
    
    state["next_action"] = next_action
    return state

def route_after_validate(state):
    """Routing function to determine next step after validation"""
    return state.get("next_action", "output")

def output_step(state):
    print("[DEBUG] I'm in output step")
    final_result = state.get("result", "Unable to generate response.")
    user_input = state.get("input", "")
    conversation_history = state.get("conversation_history", [])
    
    # Add this conversation turn to history (will be saved by app.py)
    # We'll let app.py handle the actual saving to maintain conversation across requests
    
    # Return both for backward compatibility
    return {"answer": final_result, "result": final_result}


graph.add_node("think", think_step)
graph.add_node("act", act_step)
graph.add_node("validate", validate_step)
graph.add_node("output", output_step)

graph.add_edge("think", "act")
# Always go to validate after acting
graph.add_edge("act", "validate")
# Conditional routing from validate: either retry (think) or finish (output)
graph.add_conditional_edges(
    "validate",
    route_after_validate,
    {
        "think": "think",
        "output": "output"
    }
)
graph.add_edge("output", END)

graph.set_entry_point("think")

agent_app = graph.compile()
