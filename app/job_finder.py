import inject

from database import MongoConnection
from integrations import LinkedinJobCrawler, LinkedinPostDateRange

from .interfaces.linkedin_job import LinkedinJob


class JobFinder:
    """
    Fetches job postings from various sources.
    """

    @inject.autoparams()
    def __init__(
        self, linkedin_crawler: LinkedinJobCrawler, mongo_connection: MongoConnection
    ):
        self.linkedin_crawler = linkedin_crawler
        self.linkedin_collection = mongo_connection.get_collection("linkedin")

    def __save_job_if_new(self, job_data: LinkedinJob):
        """
        Saves a job to the database if it is new.

        Args:
            job_data (LinkedinJob): The job data to save.
        """
        if self.linkedin_collection.find_one({"id": job_data.id}):
            return
        self.linkedin_collection.insert_one(job_data.model_dump())

    def fetch_jobs(self):
        """
        Crawls job postings from LinkedIn and saves into the database.
        """
        fetch_for = ["Software Engineer", "Software Developer"]

        self.linkedin_crawler.setup_driver()
        self.linkedin_crawler.login()
        for keyword in fetch_for:
            self.linkedin_crawler.crawl_jobs(
                keyword, LinkedinPostDateRange.LAST_WEEK, self.__save_job_if_new
            )
        self.linkedin_crawler.close_driver()
