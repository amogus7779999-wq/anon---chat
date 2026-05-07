from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import sqlite3, time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def db():
    return sqlite3.connect("chat.db")

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        text TEXT
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
body { margin:0; font-family:Arial; }

body.light { background:white; color:black; }
body.dark { background:#0b141a; color:white; }

.container { display:flex; height:100vh; }

.left { width:30%; padding:10px; overflow:auto; }
.right { flex:1; display:flex; flex-direction:column; }

.chat { flex:1; overflow:auto; padding:10px; display:flex; flex-direction:column; }

.msg { padding:8px; margin:5px; border-radius:10px; max-width:70%; background:#ddd; }
.dark .msg { background:#202c33; }
.me { align-self:flex-end; background:#00a884; color:white; }

.user { padding:8px; margin:5px; background:#ccc; cursor:pointer; border-radius:8px; }
.dark .user { background:#202c33; }

.bottom { display:flex; padding:10px; }
input { flex:1; padding:10px; border-radius:20px; border:none; }

button { padding:10px; margin-left:5px; border:none; border-radius:20px; }

.settings { position:fixed; top:10px; right:10px; }
</style>
</head>
<body>

<button class="settings" onclick="openSettings()">⚙</button>

<div class="container">

<div class="left">
<h3 id="title">PRIZRAK</h3>
<div id="users"></div>
</div>

<div class="right">

<div class="chat" id="chat"></div>

<div class="bottom">
<input id="msg" placeholder="Message">
<button onclick="send()" id="sendBtn">Send</button>
</div>

</div>

</div>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<script>

let socket = io();

let nick = localStorage.getItem("nick");
if(!nick){
    nick = prompt("Введите ник");
    localStorage.setItem("nick", nick);
}

let theme = localStorage.getItem("theme") || "dark";
setTheme(theme);

let lang = localStorage.getItem("lang") || "ru";
setLang(lang);

let currentChat = null;

// --- темы ---
function setTheme(t){
    document.body.className = t;
    localStorage.setItem("theme", t);
}

// --- язык ---
function setLang(l){
    localStorage.setItem("lang", l);

    if(l=="ru"){
        document.getElementById("sendBtn").innerText="Отправить";
    } else {
        document.getElementById("sendBtn").innerText="Send";
    }
}

// --- настройки ---
function openSettings(){
    let newNick = prompt("Ник:", nick);
    if(newNick){
        nick = newNick;
        localStorage.setItem("nick", nick);
    }

    let t = prompt("Тема: light/dark/system");
    if(t) setTheme(t);

    let l = prompt("Язык: ru/en");
    if(l) setLang(l);
}

// --- чат ---
function send(){
    let msg = document.getElementById("msg").value;
    if(!currentChat) return alert("Выбери пользователя");

    socket.emit("private_message", {
        to: currentChat,
        msg: msg,
        from: nick
    });

    document.getElementById("msg").value="";
}

function openChat(user){
    currentChat = user;
    socket.emit("load_private", {with:user});
}

socket.on("users", (data)=>{
    let box = document.getElementById("users");
    box.innerHTML="";

    data.forEach(u=>{
        if(u.name != nick){
            let d = document.createElement("div");
            d.className="user";
            d.innerText=u.name;
            d.onclick=()=>openChat(u.name);
            box.appendChild(d);
        }
    });
});

socket.on("private_chat", (data)=>{
    let chat=document.getElementById("chat");
    chat.innerHTML="";

    data.forEach(m=>{
        let d=document.createElement("div");
        d.className="msg";

        if(m.sender==nick) d.classList.add("me");

        d.innerText=m.sender+": "+m.text;
        chat.appendChild(d);
    });

    chat.scrollTop=chat.scrollHeight;
});

socket.emit("join",{name:nick});

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

@socketio.on("join")
def join(data):
    users[request.sid]={"name":data["name"]}
    emit("users", list(users.values()), broadcast=True)

@socketio.on("disconnect")
def disconnect():
    users.pop(request.sid,None)
    emit("users", list(users.values()), broadcast=True)

@socketio.on("load_private")
def load_private(data):
    user=users[request.sid]["name"]
    other=data["with"]

    con=db()
    cur=con.cursor()

    cur.execute("""
    SELECT sender,text FROM messages
    WHERE (sender=? AND receiver=?)
       OR (sender=? AND receiver=?)
    """,(user,other,other,user))

    rows=cur.fetchall()
    con.close()

    msgs=[{"sender":r[0],"text":r[1]} for r in rows]
    emit("private_chat",msgs)

@socketio.on("private_message")
def private_message(data):
    frm=data["from"]
    to=data["to"]
    msg=data["msg"]

    con=db()
    cur=con.cursor()

    cur.execute("INSERT INTO messages (sender,receiver,text) VALUES (?,?,?)",
                (frm,to,msg))

    con.commit()
    con.close()

    load_private({"with":to})

if __name__=="__main__":
    socketio.run(app,host="0.0.0.0",port=10000)
