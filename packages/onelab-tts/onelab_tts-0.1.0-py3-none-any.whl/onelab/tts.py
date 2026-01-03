import logging
import os
from typing import List

import torch
from chatterbox.tts_turbo import ChatterboxTurboTTS

from .podcast import Podcast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("OneLabTTS")


class TextToSpeech:
    def __init__(self, device: str = "cpu"):
        """
        Initialize the TextToSpeech library.

        Args:
            device: Device to run the model on ("cpu" or "cuda").
        """
        logger.info(f"Initializing TextToSpeech on {device}...")
        self.model = ChatterboxTurboTTS.from_pretrained(device=device)
        
        # Determine the package directory where this file resides
        self.root_dir = os.path.dirname(os.path.abspath(__file__))

        # Dynamically load voices from the sample directory inside the package
        self.voice_map = {}
        sample_dir = os.path.join(self.root_dir, "sample")

        if os.path.exists(sample_dir):
            logger.info(f"Scanning for voices in {sample_dir}...")
            for file in os.listdir(sample_dir):
                if file.lower().endswith(".wav"):
                    voice_name = os.path.splitext(file)[0]
                    # Store relative path to keep it consistent with root_dir usage in Podcast
                    self.voice_map[voice_name] = os.path.join("sample", file)
            logger.info(
                f"Found {len(self.voice_map)} voices: {list(self.voice_map.keys())}"
            )
        else:
            logger.warning(
                f"Sample directory not found at {sample_dir}. No voices loaded."
            )

        self.podcast = Podcast(self.model, self.voice_map, self.root_dir)
        logger.info("TextToSpeech initialized.")

    def list_voices(self) -> List[str]:
        """List all available voices."""
        return list(self.voice_map.keys())

    def convert(self, text: str, voice: str) -> torch.Tensor:
        """
        Convert a single text segment to speech.
        """
        logger.info(f"Converting text with voice '{voice}'...")
        path = self.podcast._get_audio_prompt_path(voice)
        wav = self.model.generate(text, audio_prompt_path=path)
        return wav
