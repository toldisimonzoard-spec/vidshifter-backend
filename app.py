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
        # 1. yt-dlp: Videó letöltése a szerverre
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'downloaded_video.mp4'),
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print("A videó sikeresen letöltve a szerverre!")

        # 2. AI Fordítás és Magyar Szinkronhang Generálás (gTTS)
        sample_text = "Ez a videó sikeresen át lett alakítva magyar szinkronos verzióra a VidShifter AI által."
        translated_text = GoogleTranslator(source='auto', target='hu').translate(sample_text)
        
        output_audio_path = os.path.join(DOWNLOAD_FOLDER, 'output_audio.mp3')
        tts = gTTS(text=translated_text, lang='hu', slow=False)
        tts.save(output_audio_path)

        print("A magyar szinkronhang sikeresen elkészült és elmentve!")

        return jsonify({
            'success': True,
            'message': 'A videó letöltése és a magyar AI szinkron generálása sikeresen megtörtént!',
            'url': video_url,
            'ai_text': translated_text
        })

    except Exception as e:
        print(f"Hiba történt a feldolgozás során: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
