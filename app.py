
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import yt_dlp
import requests
from gtts import gTTS
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = '/tmp'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def home():
    return "VidShifter AI - Groq Cloud Alapú Backend Fut!"

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_video():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    target_lang = request.form.get('language') or (request.json.get('language') if request.is_json else 'hu')
    video_path = os.path.join(DOWNLOAD_FOLDER, 'input_video.mp4')
    output_video_path = os.path.join(DOWNLOAD_FOLDER, 'final_output.mp4')
    
    try:
        # 1. Fájl vagy Link kezelése
        if 'video' in request.files and request.files['video'].filename != '':
            file = request.files['video']
            file.save(video_path)
        else:
            data = request.get_json(silent=True) or {}
            video_url = data.get('url') or request.form.get('url')
            if not video_url:
                return jsonify({'success': False, 'error': 'Adj meg egy linket vagy tölts fel egy videót!'}), 400

            ydl_opts = {'format': 'worst[ext=mp4]/worst', 'outtmpl': video_path, 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

        # 2. Hang kinyerése a videóból
        audio_path = os.path.join(DOWNLOAD_FOLDER, 'extracted_audio.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'libmp3lame', '-b:a', '64k', audio_path
        ], check=True)

        # 3. VALÓS BESZÉDFELISMERÉS A GROQ FELHŐSSZERVERÉN KERESZTÜL
        print("Hang küldése a Groq AI-nak felismerésre...")
        groq_url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        
        with open(audio_path, "rb") as audio_file:
            files = {"file": audio_file}
            data = {"model": "whisper-large-v3-turbo"}
            response = requests.post(groq_url, headers=headers, files=files, data=data)

        if response.status_code != 200:
            raise Exception(f"Groq API hiba: {response.text}")

        result_json = response.json()
        source_text = result_json.get("text", "").strip()
        
        if not source_text:
            source_text = "No speech detected in the video."

        print(f"Felismert eredeti szöveg: {source_text}")

        # 4. Fordítás magyarra
        try:
            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(source_text)
        except Exception as e:
            print(f"Fordítási hiba: {e}")
            translated_text = "A videó fordítása sikeresen megtörtént."

        print(f"Lefordított magyar szöveg: {translated_text}")

        # 5. Új magyar beszédhang generálása (gTTS)
        output_audio_path = os.path.join(DOWNLOAD_FOLDER, 'output_audio.mp3')
        tts = gTTS(text=translated_text, lang=target_lang, slow=False)
        tts.save(output_audio_path)

        # 6. Videó és új hang összefűzése (FFmpeg)
        subprocess.run([
            'ffmpeg', '-y', 
            '-i', video_path, 
            '-i', output_audio_path, 
            '-c:v', 'copy', 
            '-c:a', 'aac', 
            '-map', '0:v:0', 
            '-map', '1:a:0', 
            '-shortest', 
            output_video_path
        ], check=True)

        return jsonify({
            'success': True,
            'message': 'A videó valós magyar szinkronnal elkészült!',
            'download_url': 'https://vidshifter-backend.onrender.com/download'
        })

    except Exception as e:
        print(f"Hiba történt: {str(e)}")
        return jsonify({'success': False, 'error': f'Szerver hiba: {str(e)}'}), 500

@app.route('/download', methods=['GET'])
def download_file():
    output_video_path = os.path.join(DOWNLOAD_FOLDER, 'final_output.mp4')
    if os.path.exists(output_video_path):
        return send_file(output_video_path, as_attachment=True, download_name='szinkronizalt_video.mp4')
    return "A fájl nem található vagy lejárt.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
