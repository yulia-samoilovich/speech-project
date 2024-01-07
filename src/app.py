import base64
from flask import Flask, render_template, send_file, current_app, jsonify, url_for
from audio_processing.record_audio import record_audio
from audio_processing.transcription import *
from audio_processing.exercise_service import *
from visualization.plot_results import plot_results
import threading
import os
from models import db

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['recording_lock'] = threading.Lock()
app.config['processing_done'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pronunciation.db'
db.init_app(app)

with app.app_context():
    db.create_all()

from models.native_pronunciations import NativePronunciation
from models.user_recordings import UserRecording

def audio_processing_thread():
    with app.app_context():
        if not current_app.config['processing_done']:
            app_obj = current_app._get_current_object()
            audio_wav_path = os.path.join(app_obj.root_path, 'data', 'user_recordings', 'recording.wav')

            # Record the audio
            recording = record_audio(audio_wav_path=audio_wav_path)

            # Define paths for the plots
            waveform_plot_path = os.path.join(current_app.static_folder, 'images', 'waveform_plot.png')
            pitch_plot_path = os.path.join(current_app.static_folder, 'images', 'pitch_plot.png')

            # Call the plot_results function
            result_data = plot_results(recording, waveform_plot_path, pitch_plot_path)

            # Update the result_data dictionary and set processing_done flag
            current_app.config['result_data'] = result_data
            current_app.config['processing_done'] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio_analysis')
def audio_analysis():
    result_data = current_app.config.get('result_data', {})
    return render_template('audio_analysis.html', url=result_data.get('waveform_plot_path', 'pitch_plot_path'))
    
@app.route('/pronunciation_practice')
def pronunciation_practice():
    categories = ["The R Sound", "Short I Sound", "Long I Sound"] 
    return render_template('pronunciation_practice.html', categories=categories)


@app.route('/pronunciation_practice/<category_name>')
def pronunciation_category_data(category_name):
    exercises = fetch_exercises_for_category(category_name)
    exercises_data = [
        {
            'word_or_phrase': exercise['word_or_phrase'], 
            'pronunciationUrl': url_for('static', filename=exercise['audio_file_path'])
        } for exercise in exercises
    ]
    return jsonify(exercises_data)



@app.route('/record_and_plot', methods=['POST'])
def record_and_plot():
    with app.app_context():
        audio_thread = threading.Thread(target=audio_processing_thread)
        audio_thread.start()
        audio_thread.join()

        result_data = current_app.config.get('result_data', {})
        if result_data:
            waveform_data, pitch_data = None, None
            if 'waveform_plot_path' in result_data and os.path.exists(result_data['waveform_plot_path']):
                with open(result_data['waveform_plot_path'], 'rb') as image_file:
                    waveform_data = base64.b64encode(image_file.read()).decode('utf-8')

            if 'pitch_plot_path' in result_data and os.path.exists(result_data['pitch_plot_path']):
                with open(result_data['pitch_plot_path'], 'rb') as image_file:
                    pitch_data = base64.b64encode(image_file.read()).decode('utf-8')

            return render_template('audio_analysis.html', waveform_data=waveform_data, pitch_data=pitch_data, result_data=result_data)
        else:
            return render_template('audio_analysis.html', waveform_data=None, pitch_data=None, result_data=None)

@app.route('/waveform_plot.png')
def waveform_plot_png():
    waveform_plot_path = current_app.config.get('result_data', {}).get('waveform_plot_path')
    if waveform_plot_path is not None and os.path.exists(waveform_plot_path):
        return send_file(waveform_plot_path, mimetype='image/png')
    else:
        return "No waveform plot available."
    
@app.route('/pitch_plot.png')
def pitch_plot_png():
    pitch_plot_path = current_app.config.get('result_data', {}).get('pitch_plot_path')
    if pitch_plot_path is not None and os.path.exists(pitch_plot_path):
        return send_file(pitch_plot_path, mimetype='image/png')
    else:
        return "No pitch plot available."
    

if __name__ == '__main__':
    app.run(debug=True)
