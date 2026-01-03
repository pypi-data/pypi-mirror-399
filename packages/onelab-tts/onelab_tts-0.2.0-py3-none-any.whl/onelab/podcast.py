import logging
import os
from typing import Dict, List

import torch
from chatterbox.tts_turbo import ChatterboxTurboTTS

from .schema import ConversationInput

logger = logging.getLogger("OneLabTTS")


class Podcast:
    def __init__(
        self, model: ChatterboxTurboTTS, voice_map: Dict[str, str], root_dir: str
    ):
        self.model = model
        self.voice_map = voice_map
        self.root_dir = root_dir

    def _get_audio_prompt_path(self, voice: str) -> str:
        rel_path = self.voice_map.get(voice)
        if not rel_path:
            raise ValueError(
                f"Voice '{voice}' not found. Available voices: {list(self.voice_map.keys())}"
            )

        # Construct absolute path
        path = os.path.join(self.root_dir, rel_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Audio prompt file not found at: {path}")
        return path

    def create(self, args: ConversationInput) -> torch.Tensor:
        """
        Creates a podcast from a conversation input.
        """
        segments: List[torch.Tensor] = []
        total_segments = len(args["segments"])

        logger.info(f"Starting podcast creation with {total_segments} segments.")

        for i, segment in enumerate(args["segments"]):
            voice = segment["voice"]
            text = segment["text"]

            # Custom progress logging
            progress = (i + 1) / total_segments * 100
            logger.info(
                f"[{progress:.1f}%] Processing segment {i+1}/{total_segments} ({voice}): {text[:50]}..."
            )

            try:
                prompt_path = self._get_audio_prompt_path(voice)
                wav = self.model.generate(text, audio_prompt_path=prompt_path)
                segments.append(wav)
            except Exception as e:
                logger.error(f"Failed to generate segment {i+1}: {e}")
                raise e

        # Concatenate all segments into a single waveform
        if not segments:
            logger.warning("No segments generated.")
            return torch.empty(0)

        conversation = torch.cat(segments, dim=-1)
        logger.info("Podcast creation completed successfully.")
        return conversation
