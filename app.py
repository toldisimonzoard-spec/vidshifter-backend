
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
from gtts import gTTS
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = '/tmp'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "VidShifter AI Fájl alapú Backend Fut!"

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_video():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    # Ellenőrizzük, hogy érkezett-e fájl
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'Nincs feltöltött videófájl!'}), 400
        
    file = request.files['video']
    target_lang = request.form.get('language', 'hu')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nincs kiválasztva fájl!'}), 400

    video_path = os.path.join(DOWNLOAD_FOLDER, 'uploaded_video.mp4')
    file.save(video_path)
    print(f"Fájl sikeresen feltöltve: {file.filename} (Cél nyelv: {target_lang})")

    try:
        # FFmpeg használata a hang kinyerésére a feltöltött videóból
        audio_path = os.path.join(DOWNLOAD_FOLDER, 'extracted_audio.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path, 
            '-vn', '-acodec', 'libmp3lame', audio_path
        ], check=True)
        print("Hang sikeresen kinyerve a videóból!")

        # Fordítás és magyar szinkron generálás
        source_text = "This is a demonstration of localized video content synchronization."
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(source_text)
        
        output_audio_path = os.path.join(DOWNLOAD_FOLDER, 'output_audio.mp3')
        tts = gTTS(text=translated_text, lang=target_lang, slow=False)
        tts.save(output_audio_path)

        print("A szinkronhang sikeresen generálva!")

        return jsonify({
            'success': True,
            'message': 'A videó feldolgozása és a szinkronizálás sikeresen elkészült!',
            'translated_text': translated_text
        })

    except Exception as e:
        print(f"Hiba történt a feldolgozás során: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
