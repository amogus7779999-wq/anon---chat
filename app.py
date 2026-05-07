from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import sqlite3
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def db():
    return sqlite3.connect("chat.db")

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        text TEXT,
        t REAL
    )
    """)

    con.commit()
    con.close()

init_db()

users = {}

html = """
<!DOCTYPE html>
<html>
<head>
<title>PRIZRAK</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body { margin:0; font-family:Arial; background:#0b141a; color:white; }

.container { display:flex; height:100vh; }

/* список чатов */
.left {
    width:30%;
    background:#111b21;
    padding:10px;
    overflow:auto;
}

.chat-item {
    padding:10px;
    margin:5px;
    background:#202c33;
    border-radius:8px;
    cursor:pointer;
}

.chat-item:hover {
    background:#2a3942;
}

/* чат */
.right {
    flex:1;
    display:flex;
    flex-direction:column;
}

.header {
    padding:10px;
    background:#111b21;
}

.chat {
    flex:1;
    padding:10px;
    overflow:auto;
    display:flex;
    flex-direction:column;
}

.msg {
    background:#202c33;
    padding:8px;
    margin:5px;
    border-radius:10px;
    max-width:70%;
}

.me {
    align-self:flex-end;
    background:#005c4b;
}

.bottom {
    display:flex;
    padding:10px;
    background:#111b21;
}

input {
    flex:1;
    padding:10px;
    border-radius:20px;
    border:none;
}

button {
    margin-left:5px;
    padding:10px;
    border-radius:20px;
    border:none;
    background:#00a884;
}
</style>
</head>

<body>

<div class="container">

<div class="left" id="chatList">
<h3>Чаты</h3>
</div>

<div class="right">

<div class="header" id="activeChat">Выбери чат</div>

<div class="chat" id="chat"></div>

<div class="bottom">
<input id="msg" placeholder="Сообщение">
<button onclick="send()">➤</button>
</div>

</div>

</div>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<script>

let socket = io();

let nick = localStorage.getItem("nick");
if(!nick){
    nick = prompt("Введите ник:");
    localStorage.setItem("nick", nick);
}

let currentChat = null;
let chats = {};

// --- отправка ---
function send(){
    let msg = document.getElementById("msg").value;
    if(!currentChat) return;

    socket.emit("msg", {
        to: currentChat,
        from: nick,
        msg: msg
    });

    document.getElementById("msg").value="";
}

// --- открыть чат ---
function openChat(user){
    currentChat = user;
    document.getElementById("activeChat").innerText = user;
    socket.emit("load", {with:user});
}

// --- список чатов ---
socket.on("chat_list", (data)=>{
    let box = document.getElementById("chatList");
    box.innerHTML = "<h3>Чаты</h3>";

    data.forEach(u=>{
        if(u != nick){
            let d = document.createElement("div");
            d.className = "chat-item";
            d.innerText = u;
            d.onclick = ()=>openChat(u);
            box.appendChild(d);
        }
    });
});

// --- сообщения ---
socket.on("messages", (data)=>{
    let chat = document.getElementById("chat");
    chat.innerHTML = "";

    data.forEach(m=>{
        let d = document.createElement("div");
        d.className = "msg";

        if(m.from == nick){
            d.classList.add("me");
        }

        d.innerText = m.from + ": " + m.msg;
        chat.appendChild(d);
    });

    chat.scrollTop = chat.scrollHeight;
});

socket.emit("join", {name:nick});

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

# --- вход ---
@socketio.on("join")
def join(data):
    users[request.sid] = data["name"]

    emit("chat_list", list(set(users.values())), broadcast=True)

# --- сообщения ---
@socketio.on("msg")
def msg(data):
    con = db()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO messages (sender, receiver, text, t)
    VALUES (?, ?, ?, ?)
    """, (data["from"], data["to"], data["msg"], time.time()))

    con.commit()
    con.close()

    load({"with": data["to"]})

# --- загрузка чата ---
@socketio.on("load")
def load(data):
    user = users[request.sid]
    other = data["with"]

    con = db()
    cur = con.cursor()

    cur.execute("""
    SELECT sender, text FROM messages
    WHERE (sender=? AND receiver=?)
       OR (sender=? AND receiver=?)
    ORDER BY t
    """, (user, other, other, user))

    rows = cur.fetchall()
    con.close()

    msgs = [{"from": r[0], "msg": r[1]} for r in rows]

    emit("messages", msgs)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
