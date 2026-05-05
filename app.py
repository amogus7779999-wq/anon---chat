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
.chat { height:70vh; overflow:auto; padding:10px; }
.msg { background:#222; margin:5px 0; padding:8px; border-radius:8px; }
.form { display:flex; gap:5px; padding:10px; }
input { flex:1; padding:10px; border:none; border-radius:8px; }
button { padding:10px; border:none; border-radius:8px; background:#00ff99; }
.nick { text-align:center; padding:5px; color:#00ff99; }
</style>
</head>
<body>

<div class="top">
<h2>АНОН Н.Ч</h2>
<div class="nick" id="nickDisplay"></div>
</div>

<div class="chat" id="chat"></div>

<div class="form">
<input id="msg" placeholder="Сообщение">
<button onclick="send()">➤</button>
</div>

<script>

let nick = localStorage.getItem("nick");

if(!nick){
    nick = prompt("Введите ник (изменить потом нельзя):");
    if(nick){
        localStorage.setItem("nick", nick);
    }
}else{
    alert("⚠️ Ник можно задать только один раз и изменить нельзя");
}

document.getElementById("nickDisplay").innerText = "Ты: " + nick;

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
    let msg = document.getElementById("msg").value;

    await fetch("/send", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({name: nick, msg})
    });

    document.getElementById("msg").value="";
    load();
}

setInterval(load, 1500);
load();

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
        if name == OWNER_NAME:
            messages.append(f"[СОЗДАТЕЛЬ] {name}: {msg}")
        else:
            messages.append(f"{name}: {msg}")

        users[name] = time.time()

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
