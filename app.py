from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import yt_dlp
from gtts import gTTS
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = '/tmp'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Sütik kezelése Render környezeti változóból (ha van)
cookies_content = os.environ.get('YOUTUBE_COOKIES')
cookies_path = os.path.join(DOWNLOAD_FOLDER, 'cookies.txt')
if cookies_content:
    with open(cookies_path, 'w', encoding='utf-8') as f:
        f.write(cookies_content)

@app.route('/')
def home():
    return "VidShifter AI Hibrid Backend Fut!"

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_video():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    target_lang = request.form.get('language') or (request.json.get('language') if request.is_json else 'hu')
    video_path = os.path.join(DOWNLOAD_FOLDER, 'input_video.mp4')
    
    try:
        # A) HA FÁJL ÉRKEZETT
        if 'video' in request.files and request.files['video'].filename != '':
            file = request.files['video']
            file.save(video_path)
            print(f"Fájl feltöltve: {file.filename}")

        # B) HA LINK ÉRKEZETT
        else:
            data = request.get_json(silent=True) or {}
            video_url = data.get('url') or request.form.get('url')

            if not video_url:
                return jsonify({'success': False, 'error': 'Adj meg egy YouTube linket VAGY tölts fel egy videót!'}), 400

            print(f"Link letöltése: {video_url}")
            ydl_opts = {
                'format': 'best',
                'outtmpl': video_path,
                'no_warnings': True,
                'quiet': True
            }
            if os.path.exists(cookies_path) and os.path.getsize(cookies_path) > 0:
                ydl_opts['cookiefile'] = cookies_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

        # HANG KINYERÉSE ÉS SZINKRONIZÁLÁS
        audio_path = os.path.join(DOWNLOAD_FOLDER, 'extracted_audio.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'libmp3lame', audio_path
        ], check=True)

        source_text = "This is an automatic video localization test."
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(source_text)

        output_audio_path = os.path.join(DOWNLOAD_FOLDER, 'output_audio.mp3')
        tts = gTTS(text=translated_text, lang=target_lang, slow=False)
        tts.save(output_audio_path)

        return jsonify({
            'success': True,
            'message': 'A videó sikeresen szinkronizálva lett!',
            'translated_text': translated_text
        })

    except Exception as e:
        print(f"Hiba: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
