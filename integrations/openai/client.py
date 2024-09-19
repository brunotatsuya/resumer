import inject
from openai import OpenAI
from openai.types.chat import ChatCompletion

from config import Config

from .constants import DEFAULT_MODEL


class OpenAIClient:
    """
    A client for interacting with the OpenAI API.
    """

    @inject.autoparams()
    def __init__(self, config: Config):
        self.config = config
        self.client = self.__create_client()

    def __create_client(self) -> OpenAI:
        """
        Creates an OpenAI library client instance.

        Returns:
            OpenAI: An OpenAI library client instance.
        """
        return OpenAI(api_key=self.config.OPENAI_API_KEY)

    def __make_single_interaction(self, prompt: str) -> ChatCompletion:
        """
        Makes a single interaction with the OpenAI API.

        Args:
            prompt (str): The prompt to send to the API, as of the user POV.

        Returns:
            ChatCompletion: The response from the API.
        """

        return self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=DEFAULT_MODEL
        )
