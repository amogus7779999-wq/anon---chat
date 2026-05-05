from flask import Flask, render_template_string, request, jsonify
import time

app = Flask(__name__)

messages = []
users = {}

html = """
<!DOCTYPE html>
<html>
<head>
    <title>👻 Призрак</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin:0; font-family:Arial; background:#0f0f0f; color:white; }
        .top { padding:10px; background:#1a1a1a; text-align:center; }
        .chat { height:80vh; overflow:auto; padding:10px; }
        .msg { background:#222; margin:5px 0; padding:8px; border-radius:8px; }
        .form { display:flex; gap:5px; padding:10px; }
        input { flex:1; padding:10px; border:none; border-radius:8px; }
        button { padding:10px; border:none; border-radius:8px; background:#00ff99; }
        .online { font-size:12px; color:#00ff99; }
    </style>
</head>
<body>

<div class="top">
    👻 Призрак чат
    <div class="online" id="online"></div>
</div>

<div class="chat" id="chat"></div>

<div class="form">
    <input id="name" placeholder="Ник">
    <input id="msg" placeholder="Сообщение">
    <button onclick="send()">➤</button>
</div>

<script>

let nameInput = document.getElementById("name");

if(localStorage.getItem("nick")){
    nameInput.value = localStorage.getItem("nick");
}

nameInput.oninput = () => {
    localStorage.setItem("nick", nameInput.value);
}

async function load(){
    let r = await fetch("/messages");
    let data = await r.json();

    let chat = document.getElementById("chat");
    chat.innerHTML = "";

    data.forEach(m=>{
        let d = document.createElement("div");
        d.className = "msg";
        d.innerText = m;
        chat.appendChild(d);
    });

    chat.scrollTop = chat.scrollHeight;
}

async function send(){
    let name = document.getElementById("name").value;
    let msg = document.getElementById("msg").value;

    await fetch("/send", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({name, msg})
    });

    document.getElementById("msg").value="";
    load();
}

async function online(){
    let r = await fetch("/online");
    let data = await r.json();
    document.getElementById("online").innerText = "online: " + data.length;
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

    if name and msg:
        messages.append(f"{name}: {msg}")
        users[name] = time.time()

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
