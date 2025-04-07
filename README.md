# k4oss

OpenStage SSH Activator - Web Interface
=======================================

This tool provides a web-based interface to scan a local network for Siemens OpenStage devices
and remotely activate SSH access on them.

How to Run:
-----------

1. Install the required dependencies:
   pip install -r requirements.txt

2. Run the application:
   python main.py

3. Open your web browser and go to:
   http://localhost:5000

4. Enter the login password:
   kader11000

Features:
---------
- Auto-scan 192.168.1.0/24 for OpenStage devices.
- Manually add IPs for scanning.
- Activate SSH remotely on supported devices.
- Download a clean HTML report of the results.

Requirements:
-------------
- Python 3.x
- Flask
- Requests

Notes:
------
- Default credentials used: admin/admin
- SSH access settings are hardcoded (10 minutes)
