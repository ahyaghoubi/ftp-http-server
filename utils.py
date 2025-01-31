# utils.py
import socket
import logging

def get_local_ip():
    """Retrieve the local IP address of the machine, even without internet."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        # Fallback: pick the first private IP found or default to 127.0.0.1
        local_ip = "127.0.0.1"
        interfaces = socket.getaddrinfo(socket.gethostname(), None)
        for addr in interfaces:
            ip = addr[4][0]
            if ip.startswith(("192.", "10.", "172.")):
                local_ip = ip
                break
    return local_ip

def test_local_ip(ip):
    """Test if the detected local IP address is reachable by binding a test socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ip, 0))  # Bind to the IP and an ephemeral port
        return True
    except Exception as e:
        logging.warning(f"Unable to bind to IP {ip}: {e}")
        return False

def is_port_in_use(port):
    """Check if a port is already in use on 0.0.0.0."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("0.0.0.0", port)) == 0
