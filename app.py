from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "VidShifter AI Backendfut!"

@app.route('/process', methods=['POST'])
def process_video():
    data = request.json
    video_url = data.get('url')
    # Itt fogja majd feldolgozni a videót a felhő
    return jsonify({"status": "success", "message": "A videó feldolgozása elindult a felhőben!", "url": video_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)