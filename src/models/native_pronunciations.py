from . import db

class NativePronunciation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    word_or_phrase = db.Column(db.String(100), nullable=False)
    audio_file_path = db.Column(db.String(200), nullable=False) 


