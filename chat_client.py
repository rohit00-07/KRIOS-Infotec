# chat_client.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import requests
import threading

BACKEND = "http://127.0.0.1:5000/prompt"

def send_prompt(prompt_text, output_widget, input_widget, send_button):
    send_button.config(state='disabled')
    output_widget.insert(tk.END, f"You: {prompt_text}\n")
    output_widget.see(tk.END)

    def worker():
        try:
            resp = requests.post(BACKEND, json={"prompt": prompt_text}, timeout=120)
            data = resp.json()
            if resp.status_code == 200 and data.get("ok"):
                output_widget.insert(tk.END, f"Assistant: {data.get('explain')}\nResult: {data.get('result')}\n\n")
            else:
                output_widget.insert(tk.END, f"Error: {data}\n\n")
        except Exception as e:
            output_widget.insert(tk.END, f"Request error: {e}\n\n")
        finally:
            send_button.config(state='normal')
            input_widget.delete(0, tk.END)
            output_widget.see(tk.END)

    threading.Thread(target=worker, daemon=True).start()

root = tk.Tk()
root.title("PowerBI Chat Overlay")
root.geometry("420x520+50+50")
root.attributes("-topmost", True)

output = ScrolledText(root, wrap=tk.WORD, height=25)
output.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

entry_frame = tk.Frame(root)
entry_frame.pack(fill=tk.X, padx=5, pady=5)

input_var = tk.StringVar()
entry = tk.Entry(entry_frame, textvariable=input_var)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

def on_send():
    prompt = input_var.get().strip()
    if not prompt:
        return
    send_prompt(prompt, output, entry, send_btn)

send_btn = tk.Button(entry_frame, text="Send", command=on_send)
send_btn.pack(side=tk.RIGHT)

root.mainloop()