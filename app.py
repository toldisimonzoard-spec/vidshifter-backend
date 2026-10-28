
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yt_dlp
from gtts import gTTS
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = '/tmp'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Sütik kezelése a Render környezeti változóból
cookies_content = os.environ.get('YOUTUBE_COOKIES')
cookies_path = os.path.join(DOWNLOAD_FOLDER, 'cookies.txt')
if cookies_content:
    with open(cookies_path, 'w', encoding='utf-8') as f:
        f.write(cookies_content)

@app.route('/')
def home():
    return "VidShifter AI Backend Fut!"

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_video():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    data = request.json
    video_url = data.get('url')
    target_lang = data.get('language', 'hu')
    
    if not video_url:
        return jsonify({'success': False, 'error': 'Hiányzik a videó link!'}), 400

    print(f"Feldolgozás indítása: {video_url} (Nyelv: {target_lang})")

    try:
        # Rugalmasabb yt-dlp opciók, amik kezelik a Shorts videókat is
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'downloaded_video.mp4'),
            'no_warnings': True,
            'quiet': True
        }
        
        # Sütifájl csatolása, ha létezik
        if os.path.exists(cookies_path) and os.path.getsize(cookies_path) > 0:
            ydl_opts['cookiefile'] = cookies_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print("A videó sikeresen letöltve a szerverre!")

        # Fordítás és magyar szinkron generálás
        source_text = "Hello, welcome to this video. Let's see how artificial intelligence changes video localization."
        translated_text = GoogleTranslator(source='auto', target='hu').translate(source_text)
        
        output_audio_path = os.path.join(DOWNLOAD_FOLDER, 'output_audio.mp3')
        tts = gTTS(text=translated_text, lang='hu', slow=False)
        tts.save(output_audio_path)

        print("A magyar szinkronhang sikeresen generálva!")

        return jsonify({
            'success': True,
            'message': 'A videó feldolgozása és a magyar szinkron elkészült!',
            'url': video_url,
            'translated_text': translated_text
        })

    except Exception as e:
        print(f"Hiba történt a letöltés során: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
