# http_server.py
import os
import cgi
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
from utils import get_local_ip, is_port_in_use
from datetime import datetime

def format_file_size(size):
    """Convert file size to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        original_path = super().translate_path(path)
        relative_path = os.path.relpath(original_path, os.getcwd())
        full_path = os.path.join(self.directory, relative_path)
        
        # Security: Prevent directory traversal
        if not os.path.realpath(full_path).startswith(os.path.realpath(self.directory)):
            raise PermissionError("Access denied")
        return full_path

    def do_GET(self):
        """Handle GET requests with proper large file handling"""
        if self.path == '/upload':
            self.handle_upload_get()
        elif self.path == '/':
            self.handle_root_get()
        else:
            try:
                self.handle_file_request()
            except BrokenPipeError:
                # Client disconnected prematurely, no need to log as error
                logging.debug("Client disconnected during download")
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")

    def handle_file_request(self):
        """Serve files with chunked transfer and connection checking"""
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            self.send_error(404, "File not found")
            return

        file_size = os.path.getsize(path)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(file_size))
        self.end_headers()

        with open(path, 'rb') as f:
            while True:
                try:
                    chunk = f.read(16 * 1024)  # 16KB chunks
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()  # Ensure chunk is sent immediately
                except (BrokenPipeError, ConnectionResetError):
                    # Client disconnected during transfer
                    logging.debug(f"Client aborted download: {self.path}")
                    break

    def handle_root_get(self):
        """Show directory listing with upload link"""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            {self.common_styles()}
            <title>File Server - {os.path.basename(self.directory)}</title>
        </head>
        <body>
            <div class="container">
                <h1 class="my-4">📁 {os.path.basename(self.directory)}</h1>
                <a href="/upload" class="btn btn-primary mb-4">
                    <i class="bi bi-upload"></i> Upload Files
                </a>
                {self.generate_directory_listing()}
            </div>
        </body>
        </html>
        """
        self.send_html_response(html)

    def handle_upload_get(self):
        """Show modern upload form with drag & drop"""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            {self.common_styles()}
            <title>Upload Files</title>
            {self.uploader_scripts()}
        </head>
        <body>
            <div class="container">
                <h1 class="my-4"><i class="bi bi-cloud-upload"></i> Upload Files</h1>
                <a href="/" class="btn btn-outline-secondary mb-4">
                    <i class="bi bi-arrow-left"></i> Back to Files
                </a>
                
                <div class="card">
                    <div class="card-body">
                        <div id="drop-zone" class="drop-zone">
                            <input type="file" name="file" id="file-input" multiple 
                                   class="d-none" onchange="handleFiles(this.files)">
                            <label for="file-input" class="drop-zone-label">
                                <i class="bi bi-file-earmark-arrow-up fs-1"></i>
                                <div>Drag & drop files here or click to select</div>
                                <div class="text-muted">(Maximum 4GB per file)</div>
                            </label>
                        </div>
                        
                        <div id="upload-list" class="mt-4"></div>
                        
                        <button class="btn btn-success mt-3 d-none" id="start-upload"
                                onclick="startUpload()">
                            <i class="bi bi-upload"></i> Start Upload
                        </button>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        self.send_html_response(html)

    def common_styles(self):
        return """
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
        <style>
            .drop-zone {
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 3rem;
                text-align: center;
                transition: all 0.3s;
            }
            .drop-zone.dragover {
                border-color: #0d6efd;
                background-color: rgba(13, 110, 253, 0.05);
            }
            .drop-zone-label {
                cursor: pointer;
            }
            .file-item {
                padding: 1rem;
                border-bottom: 1px solid #eee;
            }
            .progress {
                height: 25px;
                margin-top: 5px;
            }
            .table-hover tbody tr:hover {
                background-color: rgba(13, 110, 253, 0.05);
            }
        </style>
        """

    def uploader_scripts(self):
        return """
        <script>
            let filesToUpload = [];
            
            // Drag & drop handlers
            const dropZone = document.getElementById('drop-zone');
            
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('dragover');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
                handleFiles(e.dataTransfer.files);
            });

            function handleFiles(files) {
                for (let file of files) {
                    addFileToList(file);
                }
                document.getElementById('start-upload').classList.remove('d-none');
            }

            function addFileToList(file) {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <i class="bi bi-file-earmark"></i> 
                            ${file.name} (${formatSize(file.size)})
                        </div>
                        <div class="w-50 mx-3">
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: 0%" aria-valuenow="0" 
                                     aria-valuemin="0" aria-valuemax="100">
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                document.getElementById('upload-list').appendChild(fileItem);
                filesToUpload.push(file);
            }

            async function startUpload() {
                const uploadBtn = document.getElementById('start-upload');
                uploadBtn.disabled = true;
                uploadBtn.innerHTML = `<i class="bi bi-upload"></i> Uploading...`;
                let successCount = 0;

                for (let i = 0; i < filesToUpload.length; i++) {
                    const file = filesToUpload[i];
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const xhr = new XMLHttpRequest();
                    const progressBar = document.querySelectorAll('.progress-bar')[i];
                    
                    xhr.upload.addEventListener('progress', (e) => {
                        if (e.lengthComputable) {
                            const percent = (e.loaded / e.total) * 100;
                            progressBar.style.width = `${percent}%`;
                            progressBar.textContent = `${Math.round(percent)}%`;
                        }
                    });

                    xhr.open('POST', '/upload', true);
                    
                    xhr.onload = () => {
                        if (xhr.status === 200) {
                            progressBar.classList.add('bg-success');
                            progressBar.textContent = 'Done!';
                            successCount++;
                            
                            // Redirect when all files complete
                            if(successCount === filesToUpload.length) {
                                setTimeout(() => window.location.href = '/', 1000);
                            }
                        } else {
                            progressBar.classList.add('bg-danger');
                            progressBar.textContent = 'Error!';
                        }
                    };

                    xhr.onerror = () => {
                        progressBar.classList.add('bg-danger');
                        progressBar.textContent = 'Error!';
                    };

                    xhr.send(formData);
                }
            }

            function formatSize(bytes) {
                const units = ['B', 'KB', 'MB', 'GB'];
                let size = bytes;
                for (const unit of units) {
                    if (size < 1024) return `${size.toFixed(1)} ${unit}`;
                    size /= 1024;
                }
                return `${size.toFixed(1)} TB`;
            }
        </script>
        """


    def do_POST(self):
        """Handle file uploads with proper success response"""
        try:
            if self.path != '/upload':
                self.send_error(404, "Not found")
                return

            content_type = self.headers['Content-Type']
            if not content_type.startswith('multipart/form-data'):
                raise ValueError("Invalid content type")

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'},
                keep_blank_values=True
            )

            # Process uploaded files
            for field in form.list:
                if field.filename:
                    file_path = os.path.join(self.directory, field.filename)
                    total_size = 0

                    # Write file in chunks
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = field.file.read(16 * 1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            total_size += len(chunk)
                            if total_size > 4 * 1024**3:
                                os.remove(file_path)
                                raise ValueError("File size exceeds 4GB limit")

            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')

        except Exception as e:
            self.send_error(500, f"Upload failed: {str(e)}")
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)

    def generate_directory_listing(self):
        """Generate styled directory listing"""
        rows = []
        with os.scandir(self.directory) as entries:
            for entry in entries:
                stat = entry.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                size = format_file_size(stat.st_size)
                icon = 'bi-folder' if entry.is_dir() else 'bi-file-earmark'
                rows.append(f"""
                    <tr>
                        <td>
                            <i class="bi {icon} me-2"></i>
                            <a href="/{entry.name}" class="text-decoration-none">
                                {entry.name}
                            </a>
                        </td>
                        <td>{size}</td>
                        <td>{mod_time}</td>
                    </tr>
                """)
        
        return f"""
        <table class="table table-hover">
            <thead class="table-light">
                <tr>
                    <th>Name</th>
                    <th>Size</th>
                    <th>Modified</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """

    def send_html_response(self, html):
        """Helper method to send HTML responses"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

def start_http_server(directory, http_port):
    """
    Create and return an HTTPServer instance serving from 'directory'.
    Caller can run http_server.serve_forever() in a thread.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError("Selected directory doesn't exist or is inaccessible.")

    if is_port_in_use(http_port):
        raise OSError(f"HTTP port {http_port} is already in use.")

    # Verify write permissions
    if not os.access(directory, os.W_OK):
        raise PermissionError("No write permissions for the directory")

    handler_class = lambda *args: CustomHandler(*args, directory=directory)
    server_address = ("0.0.0.0", http_port)
    http_server = HTTPServer(server_address, handler_class)

    local_ip = get_local_ip()
    logging.info(f"HTTP Server ready at http://{local_ip}:{http_port}")
    logging.info(f"Serving directory: {directory}")
    return http_server