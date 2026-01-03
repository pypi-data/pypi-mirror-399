# OneLab TTS Library

OneLab is a powerful Python library for Text-to-Speech (TTS) and Podcast generation, built on top of `ChatterboxTurboTTS`. It allows you to easily convert text to speech using various voices and create multi-speaker podcasts with custom logging and progress tracking.

## Features

*   **Text-to-Speech Conversion**: Convert individual text segments to audio using specific voices.
*   **Podcast Generation**: Create full conversations with multiple speakers.
*   **Dynamic Voice Loading**: Automatically detects available voices from the package's `sample` directory.
*   **Custom Logging**: Detailed logging and progress tracking during generation.
*   **Modular Design**: Clean and extensible architecture.

## Installation

You can install the package using pip:

```bash
pip install onelab
```

Or install directly from the source:

```bash
git clone https://github.com/satadeep3927/onelab.git
cd onelab
pip install .
```

## Usage

### Initialization

To use the library, simply initialize the `OneLab` class. The library automatically locates the bundled voice samples.

```python
from onelab import OneLab

# Initialize OneLab
onelab = OneLab(device="cpu") 
```

### Listing Available Voices

You can list all voices detected in the `sample` directory:

```python
voices = onelab.tts.list_voices()
print("Available voices:", voices)
```

### Converting Text to Speech

To convert a single line of text:

```python
wav = onelab.tts.convert("Hello, world!", voice="charlie")
# Save the output
import torchaudio
torchaudio.save("output.wav", wav, onelab.tts.model.sr)
```

### Creating a Podcast

To create a multi-speaker podcast, define your conversation segments and use the `podcast.create` method:

```python
from onelab import ConversationInput

data: ConversationInput = {
    "segments": [
        {"voice": "charlie", "text": "Hello Emilia!"},
        {"voice": "emilia", "text": "Hi Charlie! How are you?"},
    ]
}

# Generate the podcast
podcast_wav = onelab.tts.podcast.create(data)

# Save the podcast
torchaudio.save("podcast.wav", podcast_wav, onelab.tts.model.sr)
```

## API Reference

### `OneLab`

The main entry point for the library.

*   `__init__(device: str = "cpu")`: Initializes the library.

### `TextToSpeech` (accessed via `onelab.tts`)

Handles TTS operations.

*   `list_voices() -> List[str]`: Returns a list of available voice names.
*   `convert(text: str, voice: str) -> torch.Tensor`: Generates audio for the given text and voice.

### `Podcast` (accessed via `onelab.tts.podcast`)

Handles podcast generation.

*   `create(args: ConversationInput) -> torch.Tensor`: Generates a concatenated audio waveform for the entire conversation.

## License

MIT
