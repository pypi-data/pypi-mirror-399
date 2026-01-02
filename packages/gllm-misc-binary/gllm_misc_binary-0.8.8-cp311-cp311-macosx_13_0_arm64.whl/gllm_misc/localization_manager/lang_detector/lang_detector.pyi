import abc
from _typeshed import Incomplete
from abc import ABC
from gllm_core.schema import Component
from gllm_misc.utils import is_valid_language_code as is_valid_language_code

DEPRECATION_MESSAGE: str

class BaseLangDetector(Component, ABC, metaclass=abc.ABCMeta):
    """An abstract base class for the language detectors used in Gen AI applications.

    This class provides a foundation for building language detectors in Gen AI applications. It includes
    initialization for the default language and abstract language detection logic that subclasses must implement.

    Attributes:
        default_language (str | None): The default language to return if no valid language is detected. If None, an
            error will be raised if no valid language is detected.
    """
    default_language: Incomplete
    def __init__(self, default_language: str | None = None) -> None:
        """Initializes the language detector.

        Args:
            default_language (str | None, optional): The default language to return if no valid language is detected.
                Defaults to None, in which case an error will be raised if no valid language is detected.

        Raises:
            ValueError: If the default language is not a valid ISO 639-1 code.
        """
    async def detect_language(self, text: str) -> str:
        """Detects the language of an input text.

        This method detects the language of an input text and returns the ISO 639-1 code of the detected language.
        In the case where the detected language is not a valid ISO 639-1 code or the detection fails, it will return the
        default language if provided or raise an error otherwise.

        Args:
            text (str): The input text to be detected.

        Returns:
            str: The ISO 639-1 code of the detected language.

        Raises:
            ValueError: If the detected language is not a valid ISO 639-1 code and no default language is provided.
        """
