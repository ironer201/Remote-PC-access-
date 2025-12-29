# backend.py
import json
import asyncio
import websockets
import os
import random
import subprocess
import time
from pynput.keyboard import Controller, Key

# =======================
# CONFIG / STATE
# =======================

FILE_NAME = "Key.txt"
LOG_FILE = "log.txt"
PORT = 8765
PIN = str(random.randint(100000, 999999))

keyboard = Controller()

shortcuts_data = {
    "shortcuts": []
}

# =======================
# UTILITIES
# =======================

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.ctime()} - {msg}\n")

# =======================
# SHORTCUT STORAGE API
# =======================

def load_shortcuts():
    if not os.path.exists(FILE_NAME):
        shortcuts_data["shortcuts"] = []
        return []

    with open(FILE_NAME, "r") as f:
        data = json.load(f)

    shortcuts_data["shortcuts"] = data.get("shortcuts", [])[:6]
    return shortcuts_data["shortcuts"]

def save_shortcuts():
    shortcuts_data["shortcuts"] = shortcuts_data["shortcuts"][:6]

    with open(FILE_NAME, "w") as f:
        json.dump(shortcuts_data, f, indent=4)

def update_shortcut(slot_id, label, value):
    found = False

    for sc in shortcuts_data["shortcuts"]:
        if sc["id"] == slot_id:
            sc["label"] = label
            sc["action"] = "key_combo"
            sc["value"] = value
            found = True
            break

    if not found:
        shortcuts_data["shortcuts"].append({
            "id": slot_id,
            "label": label,
            "action": "key_combo",
            "value": value
        })

    save_shortcuts()

# =======================
# KEYBOARD EXECUTION
# =======================

def press_combo(combo):
    if not combo:
        return

    keys = [k for k in combo.split("+") if k]

    key_map = {
        "ctrl": Key.ctrl,
        "control": Key.ctrl,
        "alt": Key.alt,
        "shift": Key.shift,
        "win": getattr(Key, "cmd", getattr(Key, "cmd_l", Key.ctrl)),
        "cmd": getattr(Key, "cmd", getattr(Key, "cmd_l", Key.ctrl)),
        "home": Key.home,
        "kp_home": Key.home,
        "numpad_home": Key.home,
        "end": Key.end,
        "kp_end": Key.end
    }

    resolved = []
    for k in keys:
        k_norm = k.lower().replace(" ", "_")
        resolved.append(key_map.get(k_norm, k))

    for k in resolved:
        try:
            keyboard.press(k)
        except Exception as e:
            log(f"Press error {k}: {e}")

    for k in reversed(resolved):
        try:
            keyboard.release(k)
        except Exception:
            pass

# =======================
# WEBSOCKET SERVER
# =======================

async def handler(ws):
    paired = False
    log("Client connected")

    await ws.send(json.dumps({
        "type": "pin",
        "pin": PIN
    }))

    async for msg in ws:
        data = json.loads(msg)

        if data["type"] == "pair":
            if data["pin"] == PIN:
                paired = True
                await ws.send(json.dumps({
                    "type": "shortcuts",
                    "shortcuts": load_shortcuts()
                }))
                log("Paired successfully")
            else:
                log("Wrong PIN")
                await ws.close()

        if not paired:
            continue

        if data["type"] == "execute":
            sc = next((s for s in load_shortcuts() if s["id"] == data["id"]), None)
            if not sc:
                continue

            if sc["action"] == "open_folder":
                subprocess.Popen(["xdg-open", sc["value"]])

            elif sc["action"] == "key_combo":
                press_combo(sc["value"])

            elif sc["action"] == "media":
                subprocess.Popen(["playerctl", sc["value"]])

            log(f"Executed: {sc['label']}")

async def run_server():
    print("PIN:", PIN)
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()
