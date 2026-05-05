from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

import os

messages = []

def load_messages():
    if os.path.exists("messages.txt"):
        with open("messages.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return []

def save_message(msg):
    with open("messages.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

html = """
<!DOCTYPE html>
<html>
<head>
    <title>👻 Призрак</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial;
            background: #111;
            color: white;
            margin: 0;
            padding: 10px;
        }

        h2 {
            text-align: center;
            color: #00ff99;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 15px;
        }

        input {
            padding: 10px;
            border-radius: 8px;
            border: none;
        }

        button {
            padding: 10px;
            border-radius: 8px;
            border: none;
            background: #00ff99;
            font-weight: bold;
        }

        .msg {
            background: #222;
            padding: 8px;
            margin: 5px 0;
            border-radius: 6px;
        }
    </style>
</head>
<body>

<h2>👻 Призрак</h2>

<form id="form">
    <input name="name" placeholder="Ник" required>
    <input name="msg" placeholder="Сообщение" required>
    <button type="submit">Отправить</button>
</form>

<div id="chat"></div>

<script>
async function loadMessages(){
    let res = await fetch('/messages');
    let data = await res.json();
    let chat = document.getElementById('chat');
    chat.innerHTML = "";
    data.forEach(m => {
        let div = document.createElement("div");
        div.className = "msg";
        div.innerText = m;
        chat.appendChild(div);
    });
}

document.getElementById("form").onsubmit = async (e) => {
    e.preventDefault();
    let form = new FormData(e.target);
    await fetch("/send", {
        method: "POST",
        body: form
    });
    e.target.reset();
    loadMessages();
};

setInterval(loadMessages, 2000);
loadMessages();
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

@app.route("/send", methods=["POST"])
def send():
    name = request.form.get("name")
    msg = request.form.get("msg")
    if name and msg:
        messages.append(f"{name}: {msg}")
    return "ok"

@app.route("/messages")
def get_messages():
    return jsonify(messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
