import yt_dlp
import os

# Set fixed download directory inside your package
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_media(url, format_, quality):
    output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

    # Configure yt-dlp options
    if format_ == "mp3":
        options = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
    else:  # MP4 video
        options = {
            'format': f"bestvideo[height<={quality}]+bestaudio/best",
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
        }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # If MP3, replace extension
            if format_ == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"
            elif format_ == "mp4":
                filename = os.path.splitext(filename)[0] + ".mp4"

            return filename  # Full path to the file

    except Exception as e:
        print(f"❌ Error downloading media: {e}")
        return None