from _typeshed import Incomplete
from gllm_inference.request_processor import LMRequestProcessor as LMRequestProcessor, UsesLM
from gllm_misc.localization_manager.lang_detector.lang_detector import BaseLangDetector as BaseLangDetector, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE

DEFAULT_LM_OUTPUT_KEY: str

class LMBasedLangDetector(BaseLangDetector, UsesLM):
    '''A language detector that utilizes a language model to detect the language of an input text.

    The `LMBasedLangDetector` utilizes a language model to detect the language of an input text and outputs the
    ISO 639-1 code of the detected language.

    Attributes:
        lm_request_processor (LMRequestProcessor): The language model request processor object.
        default_language (str | None, optional): The default language to return if no valid language is detected.
            If None, an error will be raised if no valid language is detected.
        lm_output_key (str | None, optional): The key in the language model\'s output that contains the language ID.

    Notes:
        The `lm_request_processor` must be configured to:
        1. Take a "text" key as input. The input text of the language detector should be passed as the value of this
           "text" key.
        2. Return a JSON object which contains the ISO 639-1 code of the detected language as a string. The key of the
           ISO 639-1 code is specified by the `lm_output_key` attribute.

        Output example, assuming the `lm_output_key` is "lang_id":
        {
            "lang_id": "<ISO 639-1 code>"
        }
    '''
    lm_request_processor: Incomplete
    lm_output_key: Incomplete
    def __init__(self, lm_request_processor: LMRequestProcessor, default_language: str | None = None, lm_output_key: str | None = ...) -> None:
        """Initializes a new instance of the LMBasedLangDetector class.

        Args:
            lm_request_processor (LMRequestProcessor): The language model request processor object.
            default_language (str | None, optional): The default language to return if no valid language is detected.
                Defaults to None, in which case an error will be raised if no valid language is detected.
            lm_output_key (str | None, optional): The key in the language model's output that contains the language ID.
                Defaults to `DEFAULT_LM_OUTPUT_KEY`.

        Raises:
            ValueError: If the default language is not a valid ISO 639-1 code.
        """
