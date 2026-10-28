from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yt_dlp

app = Flask(__name__)
CORS(app)

# Ideiglenes mappa a letöltött videók számára
DOWNLOAD_FOLDER = '/tmp'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "VidShifter AI Backend Fut!"

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_video():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    data = request.json
    video_url = data.get('url')
    target_lang = data.get('language')
    
    if not video_url:
        return jsonify({'success': False, 'error': 'Hiányzik a videó link!'}), 400

    print(f"Feldolgozás indítása: {video_url} (Nyelv: {target_lang})")

    try:
        # yt-dlp beállítások a videó letöltéséhez
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'downloaded_video.mp4'),
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print("A videó sikeresen letöltve a szerverre!")

        # Itt történik majd a hang kinyerése, az OpenAI/Whisper átírás, 
        # a fordítás és a TTS (szinkronhang generálás)

        return jsonify({
            'success': True,
            'message': 'A videó letöltése és AI előkészítése sikeresen megtörtént!',
            'url': video_url
        })

    except Exception as e:
        print(f"Hiba történt a feldolgozás során: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
