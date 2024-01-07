def fetch_exercises_for_category(category_name):
    exercises = [
        {'category': 'The R Sound', 'word_or_phrase': 'red', 'audio_file_path': 'audios/audio_samples/red.mp3'},
        {'category': 'Short I Sound', 'word_or_phrase': 'sit', 'audio_file_path': 'audios/audio_samples/sit.mp3'},
        {'category': 'Long I Sound', 'word_or_phrase': 'seat', 'audio_file_path': 'audios/audio_samples/seat.mp3'},
        {'category': 'What kind of car do you want to drive Mr. Foreigner', 'word_or_phrase': 'What kind of car do you want to drive Mr. Foreigner?', 'audio_file_path': 'audios/audio_samples/r_phrase.mp3'},
    ]

    filtered_exercises = [exercise for exercise in exercises if exercise['category'] == category_name]
    return filtered_exercises
