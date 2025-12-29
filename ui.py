# frontend.py
import tkinter as tk
import backend

# =======================
# LOAD SHORTCUTS
# =======================

shortcuts = backend.load_shortcuts()

if not shortcuts:
    shortcuts = [
        {"id": i, "label": f"Button {i+1}", "value": ""}
        for i in range(6)
    ]

# =======================
# EDIT WINDOW
# =======================

def edit_shortcut(sc, btn):
    win = tk.Toplevel(root)
    win.title(f"Edit {sc['label']}")
    win.geometry("400x350")

    combo_var = tk.StringVar(value=sc["value"])

    tk.Label(
        win,
        text="Press keys on keyboard to record combo",
        fg="blue"
    ).pack(pady=5)

    entry = tk.Entry(win, textvariable=combo_var, font=("Arial", 14), width=25)
    entry.pack(pady=10)
    entry.focus_set()

    def add_key(k):
        k = k.lower()
        current = combo_var.get().split("+") if combo_var.get() else []
        if k not in current:
            current.append(k)
        combo_var.set("+".join(current))

    def on_key(event):
        add_key(event.keysym)
        return "break"

    entry.bind("<Key>", on_key)

    frame = tk.Frame(win)
    frame.pack(pady=5)

    special_keys = ["Control", "Alt", "Shift", "Win", "Home", "End"]

    for i, k in enumerate(special_keys):
        tk.Button(
            frame,
            text=k,
            width=8,
            command=lambda key=k: add_key(key)
        ).grid(row=i // 3, column=i % 3, padx=2, pady=2)

    def save():
        sc["value"] = combo_var.get()
        btn.config(text=f"{sc['label']}\n({sc['value']})")

        # ONLY backend API call
        backend.update_shortcut(sc["id"], sc["label"], sc["value"])
        win.destroy()

    tk.Button(win, text="Save Shortcut", bg="green", fg="white", command=save).pack(pady=10)
    tk.Button(win, text="Clear", command=lambda: combo_var.set("")).pack()

# =======================
# MAIN WINDOW
# =======================

root = tk.Tk()
root.title("Shortcut Controller")

for sc in shortcuts:
    btn = tk.Button(root, text=sc["label"], width=30, height=3)
    btn.pack(pady=5, padx=20)
    btn.config(command=lambda s=sc, b=btn: edit_shortcut(s, b))

root.mainloop()
