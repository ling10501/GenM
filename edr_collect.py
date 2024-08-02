import psutil
import platform
import subprocess
import os
import json

def collect_edr_indicators():
    indicators = {}

    # Check for running processes with security-related names
    security_process_keywords = ['sensor', 'agent', 'monitor', 'defender', 'protect', 'endpoint', 'edr', 'av']
    indicators['security_processes'] = [
        proc.info['name'] for proc in psutil.process_iter(['name']) 
        if any(keyword in proc.info['name'].lower() for keyword in security_process_keywords)
    ]

    # Check for EDR/AV-related services (Windows only)
    if platform.system() == "Windows":
        indicators['security_services'] = []
        try:
            result = subprocess.check_output("sc query type= service", shell=True).decode()
            for keyword in security_process_keywords:
                if keyword in result.lower():
                    indicators['security_services'].append(keyword)
        except Exception as e:
            indicators['security_services_error'] = str(e)

    # Check for virtualization (Linux/Unix)
    if platform.system() in ["Linux", "Darwin"]:
        try:
            output = subprocess.check_output("systemd-detect-virt", shell=True).decode().strip()
            indicators['virtualization'] = output if output != "none" else None
        except subprocess.CalledProcessError:
            indicators['virtualization'] = None

    # Check for known EDR/AV directories
    edr_directories = [
        "C:\\Program Files\\CrowdStrike",
        "C:\\Program Files\\SentinelOne",
        "C:\\Program Files\\Carbon Black",
        "C:\\Program Files\\Microsoft Defender for Endpoint",
        "C:\\Program Files\\McAfee",
        "C:\\Program Files\\Palo Alto Networks",
        "C:\\Program Files\\FireEye",
        "C:\\Program Files\\Sophos",
        "C:\\Program Files\\Bitdefender",
        "C:\\Program Files\\Trend Micro",
        "C:\\Program Files\\Symantec",
        "C:\\Program Files (x86)\\CrowdStrike",
        "C:\\Program Files (x86)\\SentinelOne",
        "C:\\Program Files (x86)\\Carbon Black",
        "C:\\Program Files (x86)\\Microsoft Defender for Endpoint",
        "C:\\Program Files (x86)\\McAfee",
        "C:\\Program Files (x86)\\Palo Alto Networks",
        "C:\\Program Files (x86)\\FireEye",
        "C:\\Program Files (x86)\\Sophos",
        "C:\\Program Files (x86)\\Bitdefender",
        "C:\\Program Files (x86)\\Trend Micro",
        "C:\\Program Files (x86)\\Symantec",
        "/opt/CrowdStrike",
        "/opt/SentinelOne",
        "/opt/CarbonBlack",
        "/opt/MicrosoftDefender",
        "/opt/McAfee",
        "/opt/PaloAltoNetworks",
        "/opt/FireEye",
        "/opt/Sophos",
        "/opt/Bitdefender",
        "/opt/TrendMicro",
        "/opt/Symantec"
    ]
    indicators['edr_directories'] = [dir for dir in edr_directories if os.path.exists(dir)]

    return indicators

def identify_security_software(indicators):
    edr_keywords = ['crowdstrike', 'sentinelone', 'carbon black', 'fireeye', 'mcafee', 'falcon', 'edr', 'xagt']
    av_keywords = ['defender', 'kaspersky', 'avp', 'norton', 'bitdefender', 'symantec', 'sophos', 'trend micro', 'av']

    detected_edr = []
    detected_av = []

    # Check processes for EDR and AV keywords
    for process in indicators['security_processes']:
        process_name_lower = process.lower()
        if any(keyword in process_name_lower for keyword in edr_keywords):
            detected_edr.append(process)
        elif any(keyword in process_name_lower for keyword in av_keywords):
            detected_av.append(process)

    # Check directories for EDR and AV installations
    for directory in indicators['edr_directories']:
        directory_lower = directory.lower()
        if any(keyword in directory_lower for keyword in edr_keywords):
            detected_edr.append(directory)
        elif any(keyword in directory_lower for keyword in av_keywords):
            detected_av.append(directory)

    # Compile results
    security_software_info = {
        'edr_installed': bool(detected_edr),
        'av_installed': bool(detected_av),
        'detected_edr': detected_edr,
        'detected_av': detected_av
    }

    return security_software_info

def evaluate_sandbox_percentage(indicators):
    """
    Evaluate the likelihood that the system is running in a sandbox environment.
    The function returns a percentage value based on the presence of common sandbox indicators.
    """
    score = 0
    max_score = 5  # Define the maximum possible score based on the checks

    # Check for known virtualization environment
    if indicators.get('virtualization'):
        score += 1

    # Check for security-related processes (indicative of EDR or sandbox environment)
    if indicators['security_processes']:
        score += 1

    # Check for EDR/AV directories (presence might indicate an isolated or monitored environment)
    if indicators['edr_directories']:
        score += 1

    # Check for minimal system resources (common in sandboxes)
    if psutil.virtual_memory().total < (2 * 1024 * 1024 * 1024):  # Less than 2GB of RAM
        score += 1

    if psutil.cpu_count() <= 2:  # Less than or equal to 2 CPU cores
        score += 1

    # Calculate the percentage likelihood
    sandbox_percentage = (score / max_score) * 100
    return sandbox_percentage

def save_indicators_to_file(indicators, filename='edr_indicators.json'):
    with open(filename, 'w') as f:
        json.dump(indicators, f, indent=4)

if __name__ == "__main__":
    indicators = collect_edr_indicators()
    security_info = identify_security_software(indicators)
    indicators.update(security_info)
    sandbox_percentage = evaluate_sandbox_percentage(indicators)
    indicators['sandbox_likelihood'] = f"{sandbox_percentage}%"
    save_indicators_to_file(indicators)
    print(f"Indicators collected and saved to edr_indicators.json")
    print(f"Likelihood of being in a sandbox environment: {sandbox_percentage}%")
    print(f"Detected EDR: {security_info['detected_edr']}")
    print(f"Detected AV: {security_info['detected_av']}")
