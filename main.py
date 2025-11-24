from app import JobFinder, JobSelector
from config import setup_injector

setup_injector()

job_finder = JobFinder()
job_selector = JobSelector()

#job_finder.fetch_jobs()
job_selector.switch_to_candidate("brunotatsuya")
job_selector.classify_new_jobs()
x = job_selector.get_relevant_jobs_for_current_user()
print(1)