from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    
    print(f"Feldolgozásra váró link: {video_url}, nyelv: {target_lang}")
    return jsonify({
        'success': True, 
        'message': 'A videó feldolgozása elindult a felhőben!', 
        'url': video_url
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
