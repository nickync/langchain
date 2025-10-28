from fastapi import FastAPI
from pydantic import BaseModel
#from chat_chain import get_answer
from agent import agent_app
from fastapi.responses import HTMLResponse

app = FastAPI(title="Ollama Chat AAPPI", version="1.0.0")

class ChatRequest(BaseModel):
    message: str

# @app.post("/chat")
# async def chat_endpoint(req: ChatRequest):
#     response = get_answer(req.message)
#     return {"response": response}

@app.post("/chat")
async def ask_agent(query: ChatRequest):
    result = agent_app.invoke({"input": query.message})
    return {"answer": result["result"]}

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
              body: JSON.stringify({message: msg})
            });
            console.log(res);
            const data = await res.json();
            console.log(data);
            chatBox.innerHTML += `<div class='msg bot'>🤖 ${data.answer}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
          };
        </script>
      </body>
    </html>
    """