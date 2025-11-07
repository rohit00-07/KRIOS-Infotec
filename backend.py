# backend.py
from flask import Flask, request, jsonify
import requests, os, json, time
from automation import open_powerbi, open_pbix, load_csv_into_model, create_bar_chart, refresh_data, apply_filter

app = Flask(__name__)

# ==== CONFIG ====
GROQ_API_KEY = ""
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "mixtral-8x7b"  # change if needed

PROMPT_TEMPLATE = '''
You are a JSON command generator for automating Power BI Desktop.
You will only reply in JSON format like this:
{{
  "action": "open_power_bi",
  "parameters": {{}}
}}

Input: "{user_prompt}"

Return the most appropriate JSON command for this input.
'''


def call_groq(user_prompt):
    prompt = PROMPT_TEMPLATE.format(user_prompt=user_prompt)
    headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"}

    payload = {
        "model": MODEL,
        "messages": [{"role":"user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0
    }
    resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Extract model content (adjust based on Groq response shape)
    content = data['choices'][0]['message']['content']
    return content

def safe_parse_json(text):
    # Try to find first '{' and parse JSON substring (models sometimes add whitespace)
    try:
        start = text.index('{')
        json_text = text[start:]
        obj = json.loads(json_text)
        return obj
    except Exception as e:
        raise ValueError(f"Failed to parse JSON from model output: {e}\nModel output:\n{text}")

@app.route("/prompt", methods=["POST"])
def handle_prompt():
    body = request.json
    user_prompt = body.get("prompt", "")
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    model_output = call_groq(user_prompt)
    try:
        cmd = safe_parse_json(model_output)
    except ValueError as e:
        return jsonify({"error": str(e), "raw": model_output}), 500

    action = cmd.get("action")
    # Support both "params" and "parameters" keys
    params = cmd.get("params") or cmd.get("parameters", {})
    explain = cmd.get("explain", "")
    
    # DEBUG: Print the full command for troubleshooting
    print(f"DEBUG - Full cmd: {cmd}")
    print(f"DEBUG - Action: {action}, Params: {params}")

    # Map actions to functions (validate allowed actions)
    try:
        if action == "open_powerbi":
            open_powerbi()
            result = "Power BI opened"
        elif action == "open_pbix":
            pbix_path = params.get("path")
            open_pbix(pbix_path)
            result = f"Opened PBIX: {pbix_path}"
        elif action == "load_csv_into_model":
            csv_path = params.get("path")
            load_csv_into_model(csv_path)
            result = f"CSV load initiated: {csv_path}"
        elif action == "create_bar_chart":
            x = params.get("x")
            y = params.get("y")
            dataset = params.get("dataset")
            create_bar_chart(x, y, dataset)
            result = f"Created bar chart: {y} by {x}"
        elif action == "refresh_data":
            refresh_data()
            result = "Refresh triggered"
        elif action == "apply_filter":
            field = params.get("field")
            op = params.get("operator")
            val = params.get("value")
            apply_filter(field, op, val)
            result = f"Filter applied: {field} {op} {val}"
        else:
            return jsonify({"error": "Unknown action", "action": action}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"ok": True, "action": action, "explain": explain, "result": result})

if __name__ == "__main__":
    print("Starting backend on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)