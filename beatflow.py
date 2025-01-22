import logging
from core.AudioFile import AudioFile

if __name__ == "__main__":
    try:
        audio_file = AudioFile("D:\OneDrive\OMAY PROJECT\All Tracks FLAC\Track 40.flac")
        audio_file.analyze_bpm()
        # audio_file.save_metadata()
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
