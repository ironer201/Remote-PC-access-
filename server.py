from flask import Flask, jsonify, request
import json
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "Key.txt")

# VERY IMPORTANT
os.environ["YDOTOOL_SOCKET"] = "/tmp/.ydotool_socket"

app = Flask(__name__)

@app.route("/shortcuts")
def get_shortcuts():
    with open(KEY_FILE, "r") as f:

        data = json.load(f)
    return jsonify(data)

@app.route("/execute", methods=["POST"])
def execute_shortcut():
    try:
        data = request.get_json()
        shortcut_id = data.get("id")

        with open(KEY_FILE, "r") as f:
            shortcuts = json.load(f)["shortcuts"]

        for sc in shortcuts:
            if sc["id"] == shortcut_id and sc["action"] == "key_combo":
                combo = sc["value"].replace("control", "ctrl")

                env = os.environ.copy()
                env["YDOTOOL_SOCKET"] = "/tmp/.ydotool_socket"

                subprocess.run(
                    ["ydotool", "key", combo],
                    env=env,
                    check=True
                )

                return jsonify({"status": "executed", "combo": combo})

        return jsonify({"status": "failed"}), 400

    except Exception as e:
        print("ERROR:", e)   # <-- VERY IMPORTANT
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
