from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from pathlib import Path
from typing import Optional, Union

# Enregistrer une clé custom pour MP3 (facultatif)
try:
    EasyID3.RegisterTextKey('key', 'TKEY')
except Exception:
    pass


class AudioFile:
    """
    Classe représentant un fichier audio et ses principales métadonnées.
    Gère la lecture et l'écriture des infos telles que genre, BPM, Key, etc.
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initialise l'objet AudioFile avec un chemin de fichier.
        """
        self.file_path = Path(file_path)
        self.genre: Optional[str] = None
        self.bpm: Optional[float] = None
        self.key: Optional[str] = None

        self.load_metadata()

    def load_metadata(self):
        """
        Lit les métadonnées du fichier audio et met à jour les attributs
        (self.genre, self.bpm, self.key, etc.) si elles sont disponibles.
        """
        if not self.file_path.is_file():
            print(f"Le fichier n'existe pas : {self.file_path}")
            return

        extension = self.file_path.suffix.lower()

        if extension == ".flac":
            # Gestion FLAC
            audio = FLAC(self.file_path)
            self.genre = audio.get("genre", [None])[0]
            self.bpm = audio.get("bpm", [None])[0]
            self.key = audio.get("key", [None])[0]

        elif extension == ".mp3":
            # Gestion MP3 (ID3v2)
            audio = File(self.file_path, easy=True)
            if audio is None:
                print(f"Format non reconnu pour : {self.file_path}")
                return

            self.genre = audio.get("genre", [None])[0]
            if "bpm" in audio:
                try:
                    self.bpm = float(audio["bpm"][0])
                except ValueError:
                    self.bpm = None
            self.key = audio.get("key", [None])[0]

        else:
            print(f"Format non pris en charge pour : {self.file_path}")

        print(f"Genre: {self.genre} | BPM: {self.bpm} | Key: {self.key}")

    def save_metadata(self):
        """
        Écrit (ou met à jour) les métadonnées du fichier audio.
        """
        if not self.file_path.is_file():
            print(f"Le fichier n'existe pas : {self.file_path}")
            return

        extension = self.file_path.suffix.lower()

        # Exemple de valeurs pour les tests
        self.genre = "myGenre"
        self.bpm = 666.6
        self.key = "C"

        if extension == ".flac":
            # Gestion FLAC
            audio = FLAC(self.file_path)
            if self.genre is not None:
                audio["genre"] = self.genre
            if self.bpm is not None:
                audio["bpm"] = str(self.bpm)
            if self.key is not None:
                audio["key"] = self.key
            audio.save()

        elif extension == ".mp3":
            # Gestion MP3
            try:
                audio = EasyID3(self.file_path)
            except Exception:
                audio = None

            if audio is None:
                print(f"Impossible de lire/créer des tags ID3 pour : {self.file_path}")
                return

            if self.genre is not None:
                audio["genre"] = self.genre
            if self.bpm is not None:
                audio["bpm"] = str(self.bpm)
            if self.key is not None:
                audio["key"] = self.key
            audio.save()

        else:
            print(f"Format non pris en charge pour l'écriture : {self.file_path}")

    def __repr__(self):
        """
        Représentation textuelle de l'objet pour le debug, etc.
        """
        return (f"<AudioFile path='{self.file_path}'"
                f" genre='{self.genre}' bpm='{self.bpm}' key='{self.key}'>")
