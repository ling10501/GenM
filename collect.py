import os
import socket
import psutil
import platform

def collect_system_info():
    info = {
        "os_version": platform.platform(),
        "cpu_count": os.cpu_count(),
        "memory": psutil.virtual_memory().total,
        "hostname": socket.gethostname(),
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

if __name__ == "__main__":
    system_info = collect_system_info()
    process_info = collect_process_info()
    network_info = collect_network_info()

    # Save or send the collected data to a central location for analysis
    print(system_info)
    print(process_info)
    print(network_info)
