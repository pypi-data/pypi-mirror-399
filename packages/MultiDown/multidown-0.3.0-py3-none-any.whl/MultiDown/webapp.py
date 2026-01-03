import threading
import webbrowser
import os
import time
from flask import Flask, request, render_template_string, send_file
from .downloader import download_media

app = Flask(__name__)

# Load HTML from static/index.html
with open(__file__.replace("webapp.py", "static/index.html")) as f:
    HTML_TEMPLATE = f.read()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_ = request.form.get('format')
    quality = request.form.get('quality', '720')

    file_path = download_media(url, format_, quality)

    if file_path and os.path.exists(file_path):
        def delayed_delete(path):
            # Wait a few seconds to ensure browser finishes download
            time.sleep(10)
            try:
                os.remove(path)
                print(f"✅ Deleted file: {path}")
            except Exception as e:
                print(f"❌ Error deleting file: {e}")

        # Schedule deletion in background
        threading.Thread(target=delayed_delete, args=(file_path,), daemon=True).start()

        return send_file(file_path, as_attachment=True, conditional=True)

    return "<pre>❌ Failed to download the media. Check the link or format.</pre>"

def start_server():
    threading.Thread(target=lambda: app.run(port=8000)).start()
    webbrowser.open("http://localhost:8000")