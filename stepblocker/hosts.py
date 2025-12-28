import os
import tempfile
import uuid
import subprocess

def read_hosts():
    try:
        with open("/etc/hosts", "r") as f:
            return f.read()
    except:
        return ""

def get_blocked_domains():
    blocked = []
    for line in read_hosts().split("\n"):
        line = line.strip()
        if line.startswith("127.0.0.1 ") or line.startswith("0.0.0.0 "):
            parts = line.split()
            if len(parts) >= 2 and parts[1] not in ["localhost", "broadcasthost"]:
                blocked.append(parts[1])
    return blocked

def clean_domain(d):
    d = d.strip().lower()
    for prefix in ["https://", "http://", "www."]:
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d.split("/")[0].split(":")[0]

def write_hosts_file(content):
    temp_path = os.path.join(tempfile.gettempdir(), f"hosts_{uuid.uuid4()}")
    script_path = os.path.join(tempfile.gettempdir(), f"hb_{uuid.uuid4()}.sh")
    
    with open(temp_path, "w") as f:
        f.write(content)
    with open(script_path, "w") as f:
        f.write(f'#!/bin/bash\ncp "{temp_path}" /etc/hosts\nrm "{temp_path}"\ndscacheutil -flushcache\nkillall -HUP mDNSResponder 2>/dev/null\nexit 0\n')
    os.chmod(script_path, 0o755)
    
    result = subprocess.run(
        ["osascript", "-e", f'do shell script "{script_path}" with administrator privileges'],
        capture_output=True
    )
    
    try:
        os.remove(script_path)
    except:
        pass
    
    return result.returncode == 0

def add_domains(domains):
    content = read_hosts()
    blocked = get_blocked_domains()
    to_add = []
    
    for d in domains:
        d = clean_domain(d)
        if d and "." in d:
            if d not in blocked:
                to_add.append(d)
            www = f"www.{d}" if not d.startswith("www.") else None
            if www and www not in blocked:
                to_add.append(www)
    
    if not to_add:
        return True, 0
    
    if not content.endswith("\n"):
        content += "\n"
    for d in to_add:
        content += f"127.0.0.1 {d}\n"
    
    return write_hosts_file(content), len(to_add)

def remove_domains(domains):
    content = read_hosts()
    to_remove = set(domains)
    new_lines = [
        line for line in content.split("\n")
        if not (
            line.strip().startswith(("127.0.0.1 ", "0.0.0.0 "))
            and len(line.split()) >= 2
            and line.split()[1] in to_remove
        )
    ]
    return write_hosts_file("\n".join(new_lines))
