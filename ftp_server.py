# ftp_server.py
import os
import logging
from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
from utils import get_local_ip, test_local_ip, is_port_in_use

def start_ftp_server(username, password, directory, ftp_port):
    """
    Create and return an FTPServer instance. Caller can run server.serve_forever() in a thread.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError("Selected directory doesn't exist or is inaccessible.")

    local_ip = get_local_ip()
    if not test_local_ip(local_ip):
        local_ip = "127.0.0.1"
        logging.warning("Using localhost because the detected IP is unreachable.")

    if is_port_in_use(ftp_port):
        raise OSError(f"FTP port {ftp_port} is already in use.")

    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, directory, perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = range(60000, 60100)

    address = (local_ip, ftp_port)
    ftp_server = servers.FTPServer(address, handler)
    ftp_server.max_cons = 256  # optional: set connection limits
    ftp_server.max_cons_per_ip = 5

    logging.info(f"FTP Server ready at ftp://{local_ip}:{ftp_port} (User: {username}, Pass: {password})")
    return ftp_server
