from _typeshed import Incomplete
from gllm_inference.request_processor import LMRequestProcessor as LMRequestProcessor, UsesLM
from gllm_misc.localization_manager.translator.translator import BaseTranslator as BaseTranslator, DEPRECATION_MESSAGE as DEPRECATION_MESSAGE
from gllm_misc.utils.language import get_language_name as get_language_name

DEFAULT_LM_OUTPUT_KEY: str

class LMBasedTranslator(BaseTranslator, UsesLM):
    '''A translator that utilizes a language model to translate an input text to a target language.

    The `LMBasedTranslator` utilizes a language model to translate an input text to a target language.

    Attributes:
        lm_request_processor (LMRequestProcessor): The language model request processor object.
        default_output (str | None): The default output to return if no valid output is detected.
            If None, an error will be raised if no valid output is detected.
        lm_output_key (str, optional): The key in the language model\'s output that contains the translated text.

    Notes:
        The `lm_request_processor` must be configured to:
        1. Take the following keys as input:
           - "text": The input text to be translated.
           - "origin_lang": The name of the origin language (e.g. "en" for English).
           - "target_lang": The name of the target language (e.g. "es" for Spanish).
        2. Return a JSON object which contains the translated text as a string. The key of the translated text is
           specified by the `lm_output_key` attribute.
        Output example, assuming the `lm_output_key` is "translated_text":
        {
            "translated_text": "<translated text>"
        }
    '''
    lm_request_processor: Incomplete
    lm_output_key: Incomplete
    def __init__(self, lm_request_processor: LMRequestProcessor, default_output: str | None = None, lm_output_key: str = ...) -> None:
        """Initializes a new instance of the LMBasedTranslator class.

        Args:
            lm_request_processor (LMRequestProcessor): The language model request processor object.
            default_output (str | None): The default output to return if no valid output is detected.
                Defaults to None, in which case an error will be raised if no valid output is detected.
            lm_output_key (str, optional): The key in the language model's output that contains the translated text.
                Defaults to `DEFAULT_LM_OUTPUT_KEY`.
        """
