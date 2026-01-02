import abc
from _typeshed import Incomplete
from abc import ABC
from gllm_core.schema import Component
from gllm_misc.utils import is_valid_language_code as is_valid_language_code

DEPRECATION_MESSAGE: str

class BaseTranslator(Component, ABC, metaclass=abc.ABCMeta):
    """An abstract base class for the translators used in Gen AI applications.

    This class provides a foundation for building translators in Gen AI applications. It includes
    initialization for the default language and abstract translation logic that subclasses must implement.

    Attributes:
        default_output (str | None): The default output to return when the translation process fails. If None, an
            error will be raised if the translation process fails.
    """
    default_output: Incomplete
    def __init__(self, default_output: str | None = None) -> None:
        """Initializes the translator.

        Args:
            default_output (str | None, optional): The default output to return when the translation process fails.
                Defaults to None, in which case an error will be raised if the translation process fails.
        """
    async def translate(self, text: str, target_lang: str, origin_lang: str | None = None) -> str:
        """Translates an input text.

        This method is a wrapper around the `_translate` method.

        Args:
            text (str): The input text to be translated.
            target_lang (str): The ISO 639-1 code of the target language.
            origin_lang (str | None, optional): The ISO 639-1 code of the origin language. Defaults to None.

        Returns:
            str: The translated text.

        Raises:
            ValueError: If the origin or target language is not a valid ISO 639-1 code or if the translation process
                fails and no default output is provided.
        """
