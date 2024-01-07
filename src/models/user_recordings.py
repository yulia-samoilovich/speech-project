from . import db

class UserRecording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    user_audio_path = db.Column(db.String(200), nullable=False)
