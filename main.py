
from flask import Flask, render_template_string, request, redirect, url_for
import requests
import threading

app = Flask(__name__)
PASSWORD = "kader11000"
session_password = "kader11000"
access_minutes = 10
session_minutes = 10
ip_range = "192.168.1."

devices = []

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenStage SSH Activator</title>
    <style>
        body { background-color: #121212; color: #eee; font-family: Arial; padding: 20px; }
        .device { border: 1px solid #444; border-radius: 10px; padding: 15px; margin: 10px 0; background: #1e1e1e; }
        .success { color: lightgreen; }
        .fail { color: red; }
        input[type=password], textarea { padding: 5px; width: 300px; }
    </style>
</head>
<body>
    {% if not auth %}
        <form method="post">
            <h2>Enter Password</h2>
            <input type="password" name="password" required>
            <button type="submit">Login</button>
        </form>
    {% else %}
        <h1>Discovered OpenStage Devices:</h1>

        <h3>Manual Target Input:</h3>
        <form method="post" action="/add_targets">
            <textarea name="targets" rows="3" placeholder="Enter one or more IPs, each on a new line"></textarea><br>
            <button type="submit">Add and Scan</button>
        </form>

        <a href="/report" style="color: lightblue;">Download HTML Report</a><br><br>

        {% for dev in devices %}
            <div class="device">
                <b>IP:</b> {{ dev['ip'] }}<br>
                <b>Status:</b> 
                {% if dev['status'] == 'ready' %}
                    <form method="post" action="/activate">
                        <input type="hidden" name="ip" value="{{ dev['ip'] }}">
                        <button type="submit">Activate SSH</button>
                    </form>
                {% elif dev['status'] == 'success' %}
                    <span class="success">SSH Activated</span>
                {% else %}
                    <span class="fail">{{ dev['status'] }}</span>
                {% endif %}
            </div>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

def is_openstage_device(ip):
    try:
        response = requests.get(f"http://{ip}", timeout=2)
        return "OpenStage" in response.text and "Siemens" in response.text
    except:
        return False

def scan_network():
    global devices
    devices = []
    for i in range(1, 255):
        ip = f"{ip_range}{i}"
        if is_openstage_device(ip):
            devices.append({"ip": ip, "status": "ready"})

def activate_ssh(ip):
    try:
        session = requests.Session()
        login = session.post(f"http://{ip}/login", data={"username": "admin", "password": "admin"}, timeout=5)
        if "Logout" not in login.text:
            return "Login Failed"
        payload = {
            "enable_access": "on",
            "session_password": session_password,
            "access_minutes": str(access_minutes),
            "session_minutes": str(session_minutes)
        }
        session.post(f"http://{ip}/secure_shell", data=payload, timeout=5)
        return "success"
    except Exception as e:
        return str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            threading.Thread(target=scan_network).start()
            return redirect(url_for("index", auth="1"))
        return render_template_string(html_template, auth=False)
    auth = request.args.get("auth") == "1"
    return render_template_string(html_template, auth=auth, devices=devices)

@app.route("/activate", methods=["POST"])
def activate():
    ip = request.form.get("ip")
    for dev in devices:
        if dev['ip'] == ip:
            result = activate_ssh(ip)
            dev['status'] = result
            break
    return redirect(url_for("index", auth="1"))

@app.route("/add_targets", methods=["POST"])
def add_targets():
    target_ips = request.form.get("targets", "").splitlines()
    for ip in target_ips:
        ip = ip.strip()
        if ip and not any(dev['ip'] == ip for dev in devices):
            if is_openstage_device(ip):
                devices.append({"ip": ip, "status": "ready"})
            else:
                devices.append({"ip": ip, "status": "Not OpenStage Device"})
    return redirect(url_for("index", auth="1"))

@app.route("/report")
def report():
    report_html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>SSH Activation Report</title>
        <style>
            body { background-color: #121212; color: #eee; font-family: Arial; padding: 20px; }
            .device { border: 1px solid #444; border-radius: 10px; padding: 15px; margin: 10px 0; background: #1e1e1e; }
            .success { color: lightgreen; }
            .fail { color: red; }
        </style>
    </head>
    <body>
        <h1>Scanned Devices Report:</h1>
    """
    for dev in devices:
        status_class = "success" if dev['status'] == "success" else "fail"
        report_html += f'<div class="device"><b>IP:</b> {dev["ip"]}<br><b>Status:</b> <span class="{status_class}">{dev["status"]}</span></div>'
    report_html += "</body></html>"
    return report_html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
