import inject
from openai import OpenAI
from openai.types.chat import ChatCompletion

from app.interfaces.linkedin_job import LinkedinJob
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

    def is_job_relevant(self, job: LinkedinJob) -> bool:
        """
        Asks OpenAI's if a job is relevant to the candidate.

        Args:
            job (LinkedinJob): The job to ask about.

        Returns:
            bool: True if the job is relevant, False otherwise.
        """
        prompt = """You'll be given a job description and you need to check if it's relevant or not accordingly with the following things:
1. If is not in Portuguese or English, then it's not relevant.
2. If it's hybrid or on-site, then it's not relevant.
3. If it requires more than 6 years of experience, then it's not relevant.
4. If it's not a IT position (developer, engineer, tech lead, etc), then it's not relevant.
5. If it requires mandatory programming language not included in (Python, JS/TS, Ruby), then it's not relevant.
6. Otherwise, is relevant."""
        prompt += f"\n\nJob title: {job.title}"
        prompt += f"\nJob description: {job.description}"
        prompt += "\n\nIs this job relevant? YOU SHOULD ANSWER ONLY WITH TRUE OR FALSE."
        
        response = self.__make_single_interaction(prompt)
        return "true" in response.choices[0].message.content.lower()