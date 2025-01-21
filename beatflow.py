import logging
from core.AudioFile import AudioFile

if __name__ == "__main__":
    try:
        audio_file = AudioFile("D:\\dev\\BeatFlow\\input.flac")
        # audio_file.save_metadata()
    except Exception as e:
        logging.error(f"Exception occurred: {e}")

