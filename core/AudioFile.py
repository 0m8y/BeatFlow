from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from pathlib import Path
from typing import Optional, Union
import aubio
import subprocess
import os

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

    def analyze_bpm(self) -> Optional[float]:
        """
        Analyse le BPM du fichier audio (MP3/FLAC) à l'aide de la bibliothèque aubio.
        :return: Le BPM calculé ou None en cas d'échec.
        """
        if not self.file_path.is_file():
            print(f"Le fichier n'existe pas : {self.file_path}")
            return None

        extension = self.file_path.suffix.lower()
        if extension not in [".mp3", ".flac", ".wav"]:
            print(f"Format non pris en charge pour l'analyse du BPM : {extension}")
            return None

        # Convertir en WAV si nécessaire
        temp_file = None
        if extension in [".mp3", ".flac"]:
            temp_file = self.file_path.with_suffix(".temp.wav")
            command = ["ffmpeg", "-i", str(self.file_path), "-ar", "44100", "-ac", "2", "-y", str(temp_file)]
            try:
                subprocess.run(command, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de la conversion en WAV : {e.stderr.decode('utf-8')}")
                return None
            input_file = temp_file
        else:
            input_file = self.file_path

        try:
            # Initialiser l'analyseur de BPM
            win_s = 1024          # Taille de la fenêtre FFT
            hop_s = win_s // 2  # Taille du saut
            bpm_analyzer = aubio.tempo("default", win_s, hop_s, 0)

            # Lire les données audio
            s = aubio.source(str(input_file), 0, hop_s)
            samplerate = s.samplerate

            # Calculer le BPM
            total_frames = 0
            beats = []
            while True:
                samples, read = s()
                if bpm_analyzer(samples):
                    beats.append(bpm_analyzer.get_bpm())
                total_frames += read
                if read < hop_s:
                    break

            # Retourner la moyenne des BPM détectés
            if beats:
                self.bpm = sum(beats) / len(beats)
                print(f"BPM calculé : {self.bpm}")
                return self.bpm
            else:
                print("Impossible de détecter le BPM.")
                return None
        except Exception as e:
            print(f"Erreur lors de l'analyse du BPM : {e}")
            return None
        finally:
            # Supprimer le fichier temporaire si utilisé
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)


    def __repr__(self):
        """
        Représentation textuelle de l'objet pour le debug, etc.
        """
        return (f"<AudioFile path='{self.file_path}'"
                f" genre='{self.genre}' bpm='{self.bpm}' key='{self.key}'>")
