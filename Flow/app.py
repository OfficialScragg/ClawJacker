from flask import Flask, request, send_from_directory

app = Flask(__name__)
replies_store = []  # list of { "query": str, "reply": str }


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/reply", methods=["POST"])
def reply():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")
    reply_text = data.get("reply", "")
    replies_store.append({"query": query, "reply": reply_text})
    return {"ok": True, "count": len(replies_store)}


@app.route("/replies", methods=["GET"])
def replies():
    return {"replies": replies_store}


if __name__ == "__main__":
    # HTTPS with adhoc self-signed cert (browser will warn; accept to use crypto.subtle).
    app.run(debug=True, host="0.0.0.0", port=5000)
