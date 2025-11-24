import inject
from app.interfaces.candidate import Candidate
from app.interfaces.linkedin_job import LinkedinJob
from database.connection import MongoConnection
from integrations.openai.client import OpenAIClient


class JobSelector:
    """
    Selects relevant jobs for a candidate.
    """

    @inject.autoparams()
    def __init__(self, mongo_connection: MongoConnection, openai_client: OpenAIClient):
        self.linkedin_collection = mongo_connection.get_collection("linkedin")
        self.candidates_collection = mongo_connection.get_collection("candidates")
        self.openai_client = openai_client
        self.current_candidate: Candidate = None

    def __create_candidate_if_not_exists(self, id: str) -> dict:
        new_candidate = Candidate(id=id, name="Candidate 1", classified_job_ids={})
        new_candidate_data = new_candidate.model_dump()
        self.candidates_collection.insert_one(new_candidate_data)
        return new_candidate_data

    def switch_to_candidate(self, id: str):
        """
        Switches to a specific candidate.
        """
        candidate_data = self.candidates_collection.find_one({"id": id})
        if not candidate_data:
            candidate_data = self.__create_candidate_if_not_exists(id)
        self.current_candidate = Candidate.model_validate(candidate_data)

    def classify_new_jobs(self):
        """
        Gets the unclassified jobs for the current candidate and classify them.
        """
        jobs = self.linkedin_collection.find()
        already_classified_jobs_ids = list(
            self.current_candidate.classified_job_ids.keys()
        )
        to_process = [
            LinkedinJob.model_validate(job)
            for job in jobs
            if job["id"] not in already_classified_jobs_ids
        ]

        print(f"{len(to_process)} jobs to classify.")

        for idx, job in enumerate(to_process):
            print(f"Classifying job {job.id} ({idx+1}/{len(to_process)})...")
            self.classify(job)

    def classify(self, job: LinkedinJob):
        locations_of_interest = ["portugal", "france", "european union"]
        if (
            all([loc not in job.location.lower() for loc in locations_of_interest])
            and job.location.lower() != "remote"
        ):
            self.update_job_relevancy(job.id, False)
            return
        company_blacklist = ["Crossover", "Lumenalta"]
        if any([company in job.company.lower() for company in company_blacklist]):
            self.update_job_relevancy(job.id, False)
            return
        job_relevant = self.openai_client.is_job_relevant(job)
        self.update_job_relevancy(job.id, job_relevant)

    def get_relevant_jobs_for_current_user(self):
        """
        Gets the relevant jobs for the current candidate.
        """
        return [
            f"https://www.linkedin.com/jobs/view/{job_id}"
            for job_id, relevant in self.current_candidate.classified_job_ids.items()
            if relevant
        ]

    def update_job_relevancy(self, job_id: str, relevant: bool):
        self.current_candidate.classified_job_ids[job_id] = relevant
        self.candidates_collection.find_one_and_replace(
            {"id": self.current_candidate.id}, self.current_candidate.model_dump()
        )
