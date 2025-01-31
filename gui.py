import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import sys
import logging

from ftp_server import start_ftp_server
from http_server import start_http_server
from utils import get_local_ip

def run_gui():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    ftp_server_instance = None
    http_server_instance = None

    def start_server():
        """Starts the FTP and HTTP servers, hides inputs, shows messages instead."""
        nonlocal ftp_server_instance, http_server_instance

        username = username_entry.get() or "user"
        password = password_entry.get() or "pass"
        try:
            ftp_port = int(ftp_port_entry.get() or 2121)
            http_port = int(http_port_entry.get() or 8000)
        except ValueError:
            messagebox.showerror("Error", "Ports must be numeric.")
            return

        directory = filedialog.askdirectory(title="Select Directory to Share")
        if not directory:
            messagebox.showerror("Error", "No directory selected.")
            return

        try:
            # Start servers
            ftp_server_instance = start_ftp_server(username, password, directory, ftp_port)
            http_server_instance = start_http_server(directory, http_port)

            # Run in background threads
            threading.Thread(target=ftp_server_instance.serve_forever, daemon=True).start()
            threading.Thread(target=http_server_instance.serve_forever, daemon=True).start()

            # Hide the input frame so the user no longer sees fields
            input_frame.pack_forget()

            # Show the messages_frame to display logs/status
            messages_frame.pack(fill="both", expand=True)

            # Get local ip
            local_ip = get_local_ip()

            # Update the status label
            status_label.config(
                text=(
                    f"Servers are running.\n"
                    f"FTP Server ready at ftp://{local_ip}:{ftp_port}\n"
                    f"HTTP Server ready at http://{local_ip}:{http_port}\n"
                    f"Username: {username}\n Password: {password}"
                ),
                fg="green"
            )

            # Replace the start button with the stop button
            start_button.pack_forget()
            stop_button.pack(pady=10)

        except Exception as e:
            logging.error("Error starting servers:", exc_info=True)
            messagebox.showerror("Server Error", str(e))

    def stop_server():
        nonlocal ftp_server_instance, http_server_instance
        if ftp_server_instance:
            ftp_server_instance.close_all()
            ftp_server_instance = None
        if http_server_instance:
            http_server_instance.shutdown()
            http_server_instance = None

        root.destroy()
        sys.exit(0)

    # ----- GUI LAYOUT -----
    root = tk.Tk()
    root.title("FTP and HTTP Server Setup")
    root.geometry("500x350")

    # Frame for inputs
    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="FTP & HTTP Server Configuration", font=("Sans-Serif", 14, "bold")).pack(pady=5)

    tk.Label(input_frame, text="Username:", font=("Sans-Serif", 12)).pack()
    username_entry = tk.Entry(input_frame, font=("Sans-Serif", 12))
    username_entry.insert(0, "user")
    username_entry.pack()

    tk.Label(input_frame, text="Password:", font=("Sans-Serif", 12)).pack()
    password_entry = tk.Entry(input_frame, show="*", font=("Sans-Serif", 12))
    password_entry.insert(0, "pass")
    password_entry.pack()

    tk.Label(input_frame, text="FTP Port:", font=("Sans-Serif", 12)).pack()
    ftp_port_entry = tk.Entry(input_frame, font=("Sans-Serif", 12))
    ftp_port_entry.insert(0, "2121")
    ftp_port_entry.pack()

    tk.Label(input_frame, text="HTTP Port:", font=("Sans-Serif", 12)).pack()
    http_port_entry = tk.Entry(input_frame, font=("Sans-Serif", 12))
    http_port_entry.insert(0, "8000")
    http_port_entry.pack()

    # Start button
    start_button = tk.Button(input_frame, text="Select Directory & Start Servers", font=("Sans-Serif", 12), command=start_server)
    start_button.pack(pady=10)

    # A separate frame for messages/status once the servers are running
    messages_frame = tk.Frame(root)
    # Initially hidden; we will pack it after servers start.

    status_label = tk.Label(messages_frame, text="Server status here", font=("Sans-Serif", 12), fg="blue")
    status_label.pack(pady=10)

    # Stop button
    stop_button = tk.Button(root, text="Stop Servers", font=("Sans-Serif", 12), command=stop_server)

    root.protocol("WM_DELETE_WINDOW", stop_server)
    root.mainloop()
