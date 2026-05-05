from flask import Flask, request, render_template_string

app = Flask(__name__)

messages = []

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Аноним чат</title>
    
</head>
<body>
    <h2>Общий чат</h2>

    <form method="post">
        <input type="text" name="name" placeholder="Ник" required>
        <input type="text" name="msg" placeholder="Сообщение" required>
        <button type="submit">Отправить</button>
    </form>

    <hr>

    {% for m in messages %}
        <p>{{ m }}</p>
    {% endfor %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        name = request.form.get("name")
        msg = request.form.get("msg")
        if name and msg:
            messages.append(f"{name}: {msg}")
    return render_template_string(html, messages=messages)

app.run(host="0.0.0.0", port=10000)
