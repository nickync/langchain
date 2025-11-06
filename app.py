from fastapi import FastAPI
from pydantic import BaseModel
#from chat_chain import get_answer
from agent import agent_app
from fastapi.responses import HTMLResponse
from typing import Dict, List, Tuple, Optional
import uuid

app = FastAPI(title="Ollama Chat AAPPI", version="1.0.0")

# In-memory storage for conversation history per session
# In production, you'd use a database (Redis, PostgreSQL, etc.)
conversation_memory: Dict[str, List[Tuple[str, str]]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # Optional session ID, will be generated if not provided

# @app.post("/chat")
# async def chat_endpoint(req: ChatRequest):
#     response = get_answer(req.message)
#     return {"response": response}

@app.post("/chat")
async def ask_agent(query: ChatRequest):
    # Generate or use provided session_id
    session_id = query.session_id or str(uuid.uuid4())
    
    # Get conversation history for this session
    conversation_history = conversation_memory.get(session_id, [])
    
    # Invoke agent with conversation history
    result = agent_app.invoke({
        "input": query.message,
        "conversation_history": conversation_history
    })
    
    # Get the agent's response
    agent_response = result.get("result", "Unable to generate response.")
    
    # Save this conversation turn to memory
    conversation_history.append((query.message, agent_response))
    # Keep only last 20 conversation turns to prevent memory from growing too large
    conversation_memory[session_id] = conversation_history[-20:]
    
    return {
        "answer": agent_response,
        "session_id": session_id  # Return session_id so client can use it
    }

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
      <head>
        <title>AI Chat</title>
        <style>
          body { font-family: sans-serif; max-width: 600px; margin: 40px auto; }
          #chat-box { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; }
          #input { width: 80%; padding: 8px; }
          #send { padding: 8px 16px; }
          .msg { margin: 5px 0; }
          .user { color: blue; }
          .bot { color: green; }
        </style>
      </head>
      <body>
        <h2>FastAPI Chat</h2>
        <div id="chat-box"></div>
        <input id="input" placeholder="Type your message..." />
        <button id="send">Send</button>
        <script>
          // Store session ID in browser's localStorage to persist across page reloads
          let sessionId = localStorage.getItem('chat_session_id');
          if (!sessionId) {
            sessionId = 'session_' + Date.now();
            localStorage.setItem('chat_session_id', sessionId);
          }
          
          const input = document.getElementById('input');
          const send = document.getElementById('send');
          const chatBox = document.getElementById('chat-box');
          send.onclick = async () => {
            const msg = input.value.trim();
            if (!msg) return;
            chatBox.innerHTML += `<div class='msg user'>🧑‍💬 ${msg}</div>`;
            input.value = '';
            const res = await fetch('/chat', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({message: msg, session_id: sessionId})
            });
            console.log(res);
            const data = await res.json();
            console.log(data);
            // Update session ID if server returned a new one
            if (data.session_id) {
              sessionId = data.session_id;
              localStorage.setItem('chat_session_id', sessionId);
            }
            chatBox.innerHTML += `<div class='msg bot'>🤖 ${data.answer}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
          };
          
          // Allow Enter key to send
          input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
              send.click();
            }
          });
        </script>
      </body>
    </html>
    """