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
body { margin:0; font-family:Arial; background:#0f0f0f; color:white; }
.top { padding:10px; background:#1a1a1a; text-align:center; }
.chat { height:60vh; overflow:auto; padding:10px; }
.msg { background:#222; margin:5px 0; padding:8px; border-radius:8px; }
.form { display:flex; gap:5px; padding:10px; }
input { flex:1; padding:10px; border:none; border-radius:8px; }
button { padding:10px; border:none; border-radius:8px; background:#00ff99; }
.nick { text-align:center; color:#00ff99; }
.avatar { width:30px; height:30px; border-radius:50%; }
.reactions span { margin-right:5px; cursor:pointer; }
</style>
</head>
<body>

<div class="top">
<h2>АНОН Н.Ч</h2>
<div class="nick" id="nickDisplay"></div>
<div id="online"></div>
<input type="file" id="avatarInput">
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
    if(nick){
        localStorage.setItem("nick", nick);
        localStorage.setItem("nick_changes", 0);
    }
}else{
    if(changes < 3){
        if(confirm("Сменить ник? (макс 3 раза)")){
            let newNick = prompt("Новый ник:");
            if(newNick){
                nick = newNick;
                changes++;
                localStorage.setItem("nick", nick);
                localStorage.setItem("nick_changes", changes);
            }
        }
    }else{
        alert("Ник больше менять нельзя");
    }
}

document.getElementById("nickDisplay").innerText = "Ты: " + nick;


// --- АВАТАР ---
let avatar = localStorage.getItem("avatar");

document.getElementById("avatarInput").onchange = function(){
    let file = this.files[0];
    let reader = new FileReader();

    reader.onload = function(e){
        localStorage.setItem("avatar", e.target.result);
    };

    if(file){
        reader.readAsDataURL(file);
    }
};


// --- ЧАТ ---
async function load(){
    let r = await fetch("/messages");
    let data = await r.json();

    let chat = document.getElementById("chat");
    chat.innerHTML = "";

    data.forEach((m, i)=>{
        let d = document.createElement("div");
        d.className = "msg";

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

        d.appendChild(text);
        d.appendChild(reactions);
        chat.appendChild(d);
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

setInterval(load, 1500);
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

    if mid is not None and emoji:
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
