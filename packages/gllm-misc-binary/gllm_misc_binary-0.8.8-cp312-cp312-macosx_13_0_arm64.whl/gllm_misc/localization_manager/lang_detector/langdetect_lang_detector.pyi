from _typeshed import Incomplete
from gllm_misc.localization_manager.lang_detector.lang_detector import BaseLangDetector as BaseLangDetector, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE

class LangdetectLangDetector(BaseLangDetector):
    """A language detector that uses the Langdetect library to detect the language of an input text.

    The `LangdetectLangDetector` utilizes the Langdetect library to detect the language of an input text and outputs
    the ISO 639-1 code of the detected language.

    Attributes:
        detector (Detector): The Langdetect language detector object.
        default_language (str | None): The default language to return if no valid language is detected. If None, an
            error will be raised if no valid language is detected.
    """
    detector: Incomplete
    def __init__(self, default_language: str | None = None) -> None:
        """Initializes the language detector.

        Args:
            default_language (str | None): The default language to return if no valid language is detected. Defaults to
                None, in which case an error will be raised if no valid language is detected.

        Raises:
            ValueError: If the default language is not a valid ISO 639-1 code.
        """
