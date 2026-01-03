import logging
import os

from .schema import ConversationInput, Segment
from .tts import TextToSpeech

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class OneLab:
    def __init__(self, device: str = "cpu"):
        self.tts = TextToSpeech(device=device)


__all__ = ["OneLab", "ConversationInput", "Segment"]
