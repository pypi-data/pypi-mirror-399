from _typeshed import Incomplete
from gllm_misc.localization_manager.translator.translator import BaseTranslator as BaseTranslator, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE

class GoogleTranslator(BaseTranslator):
    """A translator that utilizes Google Translate to translate an input text to a target language.

    The `GoogleTranslator` utilizes Google Translate to translate an input text to a target language.

    Attributes:
        translator (Translator): The Google Translate client.
        default_output (str | None): The default output to return if no valid output is detected.
            If None, an error will be raised if no valid output is detected.
    """
    translator: Incomplete
    def __init__(self, default_output: str | None = None) -> None:
        """Initializes a new instance of the GoogleTranslator class.

        Args:
            default_output (str | None): The default output to return if no valid output is detected.
                Defaults to None, in which case an error will be raised if no valid output is detected.
        """
