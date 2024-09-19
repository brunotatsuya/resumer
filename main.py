from app import JobFinder
from config import setup_injector

setup_injector()

job_finder = JobFinder()
job_finder.fetch_jobs()
