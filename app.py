from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import uuid

app = Flask(**name**)
CORS(app)

DOWNLOAD_DIR = tempfile.gettempdir()

@app.route(’/’)
def index():
return app.send_static_file(‘index.html’)

@app.route(’/info’, methods=[‘POST’])
def get_info():
data = request.json
url = data.get(‘url’, ‘’).strip()
if not url:
return jsonify({‘error’: ‘No URL provided’}), 400

```
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        seen = set()

        for f in info.get('formats', []):
            height = f.get('height')
            ext = f.get('ext', '')
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')

            if vcodec == 'none' and acodec == 'none':
                continue

            if height and vcodec != 'none':
                label = f"{height}p"
                key = label
                if key not in seen:
                    seen.add(key)
                    formats.append({
                        'format_id': f['format_id'],
                        'label': label,
                        'ext': ext,
                        'type': 'video',
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                    })
            elif vcodec == 'none' and acodec != 'none':
                key = f"audio_{ext}"
                if key not in seen:
                    seen.add(key)
                    formats.append({
                        'format_id': f['format_id'],
                        'label': f'Audio ({ext.upper()})',
                        'ext': ext,
                        'type': 'audio',
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                    })

        # Sort video by quality desc
        formats.sort(key=lambda x: (
            0 if x['type'] == 'video' else 1,
            -int(x['label'].replace('p','')) if x['type'] == 'video' else 0
        ))

        return jsonify({
            'title': info.get('title', 'Video'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'platform': info.get('extractor_key', ''),
            'formats': formats[:8],
        })

except Exception as e:
    return jsonify({'error': str(e)}), 500
```

@app.route(’/download’, methods=[‘POST’])
def download_video():
data = request.json
url = data.get(‘url’, ‘’).strip()
format_id = data.get(‘format_id’, ‘bestvideo+bestaudio/best’)

```
if not url:
    return jsonify({'error': 'No URL'}), 400

file_id = str(uuid.uuid4())
out_path = os.path.join(DOWNLOAD_DIR, file_id + '.%(ext)s')

ydl_opts = {
    'format': format_id + '+bestaudio/best' if 'audio' not in format_id else format_id,
    'outtmpl': out_path,
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'merge_output_format': 'mp4',
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'video')

    # Find downloaded file
    final_file = None
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(file_id):
            final_file = os.path.join(DOWNLOAD_DIR, f)
            break

    if not final_file:
        return jsonify({'error': 'Download failed'}), 500

    ext = final_file.split('.')[-1]
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    download_name = f"{safe_title}.{ext}"

    return send_file(
        final_file,
        as_attachment=True,
        download_name=download_name,
        mimetype='video/mp4' if ext == 'mp4' else 'application/octet-stream'
    )

except Exception as e:
    return jsonify({'error': str(e)}), 500
```

if **name** == ‘**main**’:
port = int(os.environ.get(‘PORT’, 5000))
app.run(host=‘0.0.0.0’, port=port)
