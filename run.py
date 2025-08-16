import os
import subprocess
import signal
import sys
import time
import re
import threading
import requests

processes = []

def install_python_dependencies():
    """Install Python dependencies for all services."""
    requirements_files = [
        'journal/requirements.txt',
        'forex_data_service/requirements.txt'
    ]
    
    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"Installing dependencies from {req_file}...")
            try:
                subprocess.run(['pip3', 'install', '-r', req_file], check=True)
                print(f"Dependencies from {req_file} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error installing dependencies from {req_file}: {e}")
                sys.exit(1)
        else:
            print(f"Warning: {req_file} not found, skipping...")

def signal_handler(sig, frame):
    print('Stopping servers...')
    for p in processes:
        # Send SIGTERM to the process group to ensure all child processes are terminated
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def build_frontend():
    """Build the frontend application."""
    print("Building frontend...")
    try:
        subprocess.run(['npm', 'run', 'build'], check=True)
        print("Frontend built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error building frontend: {e}")
        sys.exit(1)

def setup_database():
    """Ensure the database is clean and created."""
    db_file = os.path.join('instance', 'dev.db')
    if os.path.exists(db_file):
        print("Removing old database file...")
        os.remove(db_file)
    
    print("Creating new database...")
    try:
        subprocess.run(['python3', 'create_db.py'], check=True)
        print("Database created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def kill_process_on_port(port):
    try:
        # Find the process ID (PID) using the specified port
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')
        for pid in pids:
            if pid:
                print(f"Killing process {pid} on port {port}")
                os.kill(int(pid), signal.SIGKILL)
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")

def wait_for_service(port, service_name, timeout=30):
    """Wait for a service to be available on the specified port."""
    print(f"Waiting for {service_name} to be available on port {port}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://localhost:{port}/health', timeout=1)
            if response.status_code == 200:
                print(f"{service_name} is ready on port {port}")
                return True
        except:
            pass
        time.sleep(1)
    print(f"Warning: {service_name} did not become available on port {port} within {timeout} seconds")
    return False

def start_service_with_retry(service, max_retries=3):
    """Start a service with retry logic."""
    for attempt in range(max_retries):
        try:
            print(f"Starting {service['name']} service (attempt {attempt + 1}/{max_retries})...")
            pro = subprocess.Popen(
                service["command"],
                shell=True,
                preexec_fn=os.setsid,
                cwd=service["cwd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Give the process a moment to start
            time.sleep(2)
            
            # Check if process is still running
            if pro.poll() is None:
                print(f"{service['name']} started successfully")
                return pro
            else:
                # Process died, read output for debugging
                output, _ = pro.communicate()
                print(f"{service['name']} failed to start. Output: {output}")
                
        except Exception as e:
            print(f"Error starting {service['name']} service (attempt {attempt + 1}): {e}")
            
        if attempt < max_retries - 1:
            print(f"Retrying {service['name']} in 3 seconds...")
            time.sleep(3)
    
    print(f"Failed to start {service['name']} after {max_retries} attempts")
    return None

# Kill existing services before setting up the database
for port in [5005, 5007, 5000, 5175]:
    kill_process_on_port(port)

# Install Python dependencies first
install_python_dependencies()

# Build the frontend
build_frontend()

# Setup the database
setup_database()

services = [
    {
        "name": "journal_service",
        "command": "PYTHONPATH=. python3 journal/run_journal.py",
        "cwd": ".",
        "port": 5000
    },
    {
        "name": "forex_data_service",
        "command": "python3 forex_data_service/server.py",
        "cwd": ".",
        "port": 5010
    },
    {
        "name": "frontend",
        "command": "npm run dev",
        "cwd": ".",
        "port": 5175
    },
    {
        "name": "customer_service",
        "command": "node customer-service/server.js",
        "cwd": ".",
        "port": 5005
    },
    {
        "name": "trade_mentor_service",
        "command": "node trade_mentor_service/server.js",
        "cwd": ".",
        "port": 5008
    }
]

# Start services with proper error handling and health checks
for service in services:
    pro = start_service_with_retry(service)
    if pro:
        processes.append(pro)
        
        # Wait for critical services to be ready
        if service['name'] in ['journal_service']:
            wait_for_service(service['port'], service['name'])
    else:
        print(f"Critical service {service['name']} failed to start. Continuing with other services...")

print("All services started.")
print("Services status:")
for i, service in enumerate(services):
    if i < len(processes) and processes[i].poll() is None:
        print(f"  ✓ {service['name']} - Running")
    else:
        print(f"  ✗ {service['name']} - Not running")

# Keep the main script alive to manage child processes
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    signal_handler(None, None)
