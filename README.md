# **FTP & HTTP Server Setup Application**

A powerful cross-platform application for configuring and launching **FTP** and **HTTP** servers with a user-friendly graphical interface. Securely share directories with custom credentials and provide browser-based access with ease.

---

## **🚀 Features**

### 🔹 **Dual Server Support**
- Run **FTP** and **HTTP** servers simultaneously with a single application.

### 🎨 **User-Friendly GUI**
- No command-line knowledge required—set up everything with a simple interface.

### 🌍 **Web File Manager**
- 📁 **Browser-based directory listing** for easy file access.
- ⬆️ **Drag-and-drop file uploads** (supports files up to 4GB).
- 📊 **Real-time upload progress bar**.
- 📂 **Multiple file selection** for efficient file management.

### 🔐 **FTP Server Features**
- Set **custom username & password** for secure access.
- **Directory sharing** for selected folders.
- **Passive mode support** for better firewall compatibility.

### 🖥️ **Cross-Platform Compatibility**
- Works on **Windows, macOS, and Linux** seamlessly.

### 🌐 **Automatic IP Detection**
- Displays the local IP address for easy connection to servers.

### 📡 **Real-Time Status Monitoring**
- View **server states, active connections, and logs** in real time.

---

## **📌 How to Install & Use**

### 1️⃣ **Download the Application**
- **Windows**: [server_setup_windows.exe](https://github.com/ahyaghoubi/ftp-http-Server/releases)  
- **macOS**: [server_setup_macos](https://github.com/ahyaghoubi/ftp-http-Server/releases)  
- **Linux**: [server_setup_linux](https://github.com/ahyaghoubi/ftp-http-Server/releases)  

### 2️⃣ **Run the Application**
- **Windows**: Double-click `server_setup_windows.exe`
- **macOS/Linux**: Open a terminal and run:
  ```bash
  chmod +x server_setup
  ./server_setup
  ```

### 3️⃣ **Configure Servers**
- Enter **FTP login credentials** (username & password).
- Select the **directory to share**.
- Set **custom ports** (Default: FTP → `2121`, HTTP → `8000`).
- Click **"Start Servers"** to launch both FTP and HTTP servers.

### 4️⃣ **Access Your Servers**
- **FTP Access**: Use an FTP client (e.g., FileZilla) and connect using **IP:PORT**.
- **HTTP Access**: Open a browser and go to:
  ```
  http://[YOUR_IP]:[HTTP_PORT]
  ```
  - **Upload files** using drag-and-drop.
  - **Download files** with a single click.

### 5️⃣ **Stop Servers**
- Click **"Stop Servers"** to safely shut down both services.

---

## **💡 Additional Information**

### 🔄 **Port Forwarding (Optional)**
If you want to make your server accessible over the internet, consider setting up **port forwarding** on your router:
- **FTP (Default Port: 2121)** → Forward **2121** to your local machine.
- **HTTP (Default Port: 8000)** → Forward **8000** to your local machine.
- Use services like **No-IP** or **DynDNS** for a fixed domain name.

### 🔧 **System Requirements**
- **Windows 10+**, **macOS 11+**, or **Linux (Ubuntu, Debian, Arch, etc.)**.
- No additional dependencies required—just run the executable!

### 🔒 **Security Tips**
- Always **use strong passwords** for your FTP server.
- Keep the application updated for **security patches**.
- If using publicly, enable **firewall rules** to restrict access.

---

## **📜 License**
This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it!

---

## **📬 Support & Contributions**
- Found a bug? [Open an Issue](https://github.com/ahyaghoubi/ftp-http-Server/issues)
- Want to contribute? Feel free to **fork** and submit **pull requests**!

📧 **Contact**: [GitHub Repository](https://github.com/ahyaghoubi/ftp-http-Server)