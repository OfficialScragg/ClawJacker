# ClawJacker PoC

Proof-of-concept demonstrating an attack against the OpenClaw gateway. This repository contains two components:

---

## Flow

**Flow** is a **demo web page** that shows the attack on the victim browser in a single page.

- You run the Flow app and open the page in a browser that can reach OpenClaw (e.g. on the same machine as OpenClaw).
- The page brute-forces the gateway password, authenticates, sends a fixed sequence of agent messages, and displays the results in a chat-like UI.
- Use it to **see the attack flow step-by-step** (connect → brute force → auth → agent query → reply) all in one place. It is intended for demonstration and understanding, not for controlling a victim from afar.

**Run:** From the `Flow/` directory, start the app (e.g. `python app.py`) and open the URL it serves (e.g. `https://localhost:5000`). Ensure OpenClaw is running on `localhost:18789`.

---

## Proxy

**Proxy** is a **full-fledged attack** that gives a **remote attacker** full control to talk to the **victim’s local OpenClaw instance**.

- The attacker runs the Proxy server and opens the attacker chat page.
- The victim is tricked into opening a page (e.g. a fake “OpenClaw Security Tutorial”) served by the same Proxy server.
- The victim’s browser connects to OpenClaw on **their** localhost and to the attacker’s WebSocket relay. The victim’s browser acts as a **proxy** between the attacker and the victim’s OpenClaw.
- The attacker can then **chat with the OpenClaw agent** through the victim’s browser: every message the attacker sends is forwarded to the victim’s OpenClaw, and every reply is sent back to the attacker.
- This allows **remote control** of the victim’s OpenClaw from anywhere, as long as the victim has the Proxy page open in their browser.

**Run:** From the `Proxy/` directory, start the proxy server (e.g. `python proxy_server.py`). Open the attacker URL (e.g. `http://localhost:5001`) to use the chat. Have the victim open the victim URL (e.g. `http://localhost:5001/victim` or the same host from their machine). The attacker page shows when a victim is connected and then relays all conversation to the victim’s local OpenClaw.
