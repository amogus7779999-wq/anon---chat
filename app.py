from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

messages = []
users = {}

OWNER_NAME = "MUDREC"

html = """
<!DOCTYPE html>
<html>
<head>
<title>АНОН Н.Ч</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>

body { margin:0; font-family:Arial; background:#0b141a; color:white; }

.top { background:#202c33; padding:10px; text-align:center; }

.chat { height:65vh; overflow:auto; padding:10px; display:flex; flex-direction:column; }

.message { display:flex; margin:5px 0; align-items:flex-end; }

.avatar { width:40px; height:40px; border-radius:50%; margin-right:8px; }

.bubble { background:#202c33; padding:10px; border-radius:10px; max-width:70%; }

.me { align-self:flex-end; }

.me .bubble { background:#005c4b; }

.reactions span {
    margin-right:6px;
    cursor:pointer;
    font-size:14px;
}

.form { display:flex; padding:10px; background:#202c33; }

input { flex:1; padding:10px; border:none; border-radius:20px; }

button { margin-left:5px; padding:10px; border:none; border-radius:20px; background:#00a884; }

</style>
</head>
<body>

<div class="top">
<h3>АНОН Н.Ч</h3>
<div id="online"></div>
</div>

<div class="chat" id="chat"></div>

<div class="form">
<input id="msg" placeholder="Сообщение">
<button onclick="send()">➤</button>
</div>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<script>

let socket = io();

let nick = localStorage.getItem("nick");
if(!nick){
    nick = prompt("Введите ник:");
    localStorage.setItem("nick", nick);
}

let avatar = localStorage.getItem("avatar");
if(!avatar){
    let url = prompt("Ссылка на аватар:");
    if(url){
        localStorage.setItem("avatar", url);
        avatar = url;
    }
}

function send(){
    let msg = document.getElementById("msg").value;

    socket.emit("send_message", {
        name: nick,
        msg: msg,
        avatar: avatar
    });

    document.getElementById("msg").value="";
}

socket.on("load_messages", (data)=>{
    document.getElementById("chat").innerHTML = "";
    data.forEach(addMessage);
});

socket.on("new_message", (m)=>{
    addMessage(m);
});

socket.on("update_reactions", (data)=>{
    loadAll(data);
});

socket.on("online", (count)=>{
    document.getElementById("online").innerText = "онлайн: " + count;
});

function react(id, emoji){
    socket.emit("react", {id, emoji});
}

function loadAll(data){
    let chat = document.getElementById("chat");
    chat.innerHTML = "";
    data.forEach(addMessage);
}

function addMessage(m, i){
    let chat = document.getElementById("chat");

    let wrap = document.createElement("div");
    wrap.className = "message";

    if(m.name == nick){
        wrap.classList.add("me");
    }

    let img = document.createElement("img");
    img.src = m.avatar;
    img.className = "avatar";

    let bubble = document.createElement("div");
    bubble.className = "bubble";

    let text = document.createElement("div");
    text.innerText = m.text;

    let reactions = document.createElement("div");
    reactions.className = "reactions";

    ["👍","😂","🔥","❤️"].forEach(e=>{
        let span = document.createElement("span");
        let count = m.reactions[e] || 0;
        span.innerText = e + (count ? " " + count : "");
        span.onclick = () => react(messages.indexOf(m), e);
        reactions.appendChild(span);
    });

    bubble.appendChild(text);
    bubble.appendChild(reactions);

    wrap.appendChild(img);
    wrap.appendChild(bubble);

    chat.appendChild(wrap);
    chat.scrollTop = chat.scrollHeight;
}

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

@socketio.on("connect")
def connect():
    users[request.sid] = time.time()
    emit("load_messages", messages)
    emit("online", len(users), broadcast=True)

@socketio.on("disconnect")
def disconnect():
    users.pop(request.sid, None)
    emit("online", len(users), broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    name = data["name"]
    msg = data["msg"]
    avatar = data["avatar"]

    if name == OWNER_NAME:
        text = f"[СОЗДАТЕЛЬ] {name}: {msg}"
    else:
        text = f"{name}: {msg}"

    m = {
        "name": name,
        "text": text,
        "avatar": avatar,
        "reactions": {}
    }

    messages.append(m)

    emit("new_message", m, broadcast=True)

@socketio.on("react")
def handle_react(data):
    mid = data["id"]
    emoji = data["emoji"]

    if emoji not in messages[mid]["reactions"]:
        messages[mid]["reactions"][emoji] = 0

    messages[mid]["reactions"][emoji] += 1

    emit("update_reactions", messages, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
