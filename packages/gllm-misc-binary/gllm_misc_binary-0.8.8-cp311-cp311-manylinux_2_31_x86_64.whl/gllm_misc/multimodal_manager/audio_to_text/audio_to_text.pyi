import abc
from abc import ABC, abstractmethod
from gllm_core.schema import Component
from gllm_misc.multimodal_manager.audio_to_text.schema import AudioTranscript as AudioTranscript

AUDIO_DEPRECATION_MESSAGE: str

class BaseAudioToText(Component, ABC, metaclass=abc.ABCMeta):
    """An abstract base class for audio to text used in Gen AI applications.

    This class provides a foundation for building audio to text converter components in Gen AI applications.
    """
    def __init__(self) -> None:
        """Initialize the base audio to text component."""
    @abstractmethod
    async def convert(self, audio_source: str) -> list[AudioTranscript]:
        """Converts audio to text from a given source.

        This abstract method must be implemented by subclasses to define how the audio is converted to text.
        It is expected to return a list of audio transcripts.

        Args:
            audio_source (str): The source of the audio to be transcribed.

        Returns:
            list[AudioTranscript]: A list of audio transcripts.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
