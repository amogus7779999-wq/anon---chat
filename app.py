from flask import Flask, render_template_string, request, jsonify
import time

app = Flask(__name__)

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

body {
    margin:0;
    font-family:Arial;
    background:#0b141a;
    color:white;
}

.top {
    background:#202c33;
    padding:10px;
    text-align:center;
}

.chat {
    height:65vh;
    overflow:auto;
    padding:10px;
    display:flex;
    flex-direction:column;
}

.message {
    display:flex;
    align-items:flex-end;
    margin:5px 0;
}

.avatar {
    width:40px;
    height:40px;
    border-radius:50%;
    object-fit:cover;
    margin-right:8px;
}

.bubble {
    background:#202c33;
    padding:10px;
    border-radius:10px;
    max-width:70%;
}

.me {
    align-self:flex-end;
}

.me .bubble {
    background:#005c4b;
}

.reactions span {
    margin-right:5px;
    cursor:pointer;
    font-size:14px;
}

.form {
    display:flex;
    padding:10px;
    background:#202c33;
}

input {
    flex:1;
    padding:10px;
    border:none;
    border-radius:20px;
}

button {
    margin-left:5px;
    padding:10px;
    border:none;
    border-radius:20px;
    background:#00a884;
}

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

<script>

// --- НИК ---
let nick = localStorage.getItem("nick");
let changes = localStorage.getItem("nick_changes") || 0;

if(!nick){
    nick = prompt("Введите ник:");
    localStorage.setItem("nick", nick);
    localStorage.setItem("nick_changes", 0);
}else{
    if(changes < 3){
        if(confirm("Сменить ник? (макс 3 раза)")){
            let n = prompt("Новый ник:");
            if(n){
                nick = n;
                changes++;
                localStorage.setItem("nick", nick);
                localStorage.setItem("nick_changes", changes);
            }
        }
    }
}

// --- АВАТАР ---
let avatar = localStorage.getItem("avatar");

if(!avatar){
    let url = prompt("Вставь ссылку на аватар (или пропусти)");
    if(url){
        localStorage.setItem("avatar", url);
        avatar = url;
    }
}

// --- ЧАТ ---
async function load(){
    let r = await fetch("/messages");
    let data = await r.json();

    let chat = document.getElementById("chat");
    chat.innerHTML = "";

    data.forEach((m, i)=>{

        let wrap = document.createElement("div");
        wrap.className = "message";

        if(m.name == nick){
            wrap.classList.add("me");
        }

        let img = document.createElement("img");
        img.src = m.avatar || "";
        img.className = "avatar";

        let bubble = document.createElement("div");
        bubble.className = "bubble";

        let text = document.createElement("div");
        text.innerText = m.text;

        let reactions = document.createElement("div");
        reactions.className = "reactions";

        ["👍","😂","🔥","❤️"].forEach(e=>{
            let span = document.createElement("span");
            span.innerText = e + " " + (m.reactions[e] || 0);
            span.onclick = () => react(i, e);
            reactions.appendChild(span);
        });

        bubble.appendChild(text);
        bubble.appendChild(reactions);

        wrap.appendChild(img);
        wrap.appendChild(bubble);

        chat.appendChild(wrap);
    });

    chat.scrollTop = chat.scrollHeight;
}

async function send(){
    let msg = document.getElementById("msg").value;

    await fetch("/send", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({
            name: nick,
            msg: msg,
            avatar: localStorage.getItem("avatar")
        })
    });

    document.getElementById("msg").value="";
    load();
}

async function react(id, emoji){
    await fetch("/react", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({id, emoji})
    });
    load();
}

async function online(){
    let r = await fetch("/online");
    let data = await r.json();
    document.getElementById("online").innerText = "онлайн: " + data.length;
}

setInterval(load, 1200);
setInterval(online, 3000);

load();
online();

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

@app.route("/messages")
def get_messages():
    return jsonify(messages)

@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    name = data.get("name")
    msg = data.get("msg")
    avatar = data.get("avatar")

    if name and msg:
        if name == OWNER_NAME:
            text = f"[СОЗДАТЕЛЬ] {name}: {msg}"
        else:
            text = f"{name}: {msg}"

        messages.append({
            "name": name,
            "text": text,
            "avatar": avatar,
            "reactions": {}
        })

        users[name] = time.time()

    return "ok"

@app.route("/react", methods=["POST"])
def react():
    data = request.get_json()
    mid = data.get("id")
    emoji = data.get("emoji")

    if mid is not None:
        if emoji not in messages[mid]["reactions"]:
            messages[mid]["reactions"][emoji] = 0
        messages[mid]["reactions"][emoji] += 1

    return "ok"

@app.route("/online")
def online():
    now = time.time()
    for u in list(users):
        if now - users[u] > 10:
            del users[u]
    return jsonify(list(users.keys()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
