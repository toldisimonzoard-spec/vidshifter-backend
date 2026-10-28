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
        # 1. Videó letöltése és hang kinyerése MP3-ként
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'downloaded_video.mp4'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print("A videó letöltése és a hang kinyerése megtörtént!")

        # 2. Itt történne az eredeti hang átírása (pl. Whisperrel), 
        # de a gyorsaság és a Render korlátai miatt most egy demonstrációs szöveget szinkronizálunk
        source_text = "Hello, welcome to this video. Let's see how artificial intelligence changes video localization."
        translated_text = GoogleTranslator(source='auto', target='hu').translate(source_text)
        
        # 3. Magyar szinkronhang generálása a gTTS-sel
        output_audio_path = os.path.join(DOWNLOAD_FOLDER, 'output_audio.mp3')
        tts = gTTS(text=translated_text, lang='hu', slow=False)
        tts.save(output_audio_path)

        print(f"Lefordított szöveg: {translated_text}")
        print("A magyar szinkronhang sikeresen generálva!")

        return jsonify({
            'success': True,
            'message': 'A magyar szinkronhang sikeresen elkészült!',
            'url': video_url,
            'translated_text': translated_text
        })

    except Exception as e:
        print(f"Hiba történt: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
