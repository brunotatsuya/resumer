import time
from typing import List

import chromedriver_autoinstaller
import inject
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from app.interfaces.linkedin_job import LinkedinJob
from config import Config

from . import constants


class LinkedinJobCrawler:
    """
    A crawler for LinkedIn job postings.
    """

    @inject.autoparams()
    def __init__(self, config: Config):
        self.config = config
        self.driver = None
        self.waiter = None

    def __get_selected_job_description(self):
        job_details = self.driver.find_element(By.ID, constants.JOB_DETAILS_DIV_ID)
        description_text = job_details.get_attribute("innerHTML")
        soup = BeautifulSoup(description_text, "html.parser")
        return soup.get_text()

    def __is_job_promoted(self, job: WebElement):
        try:
            footer = job.find_element(
                By.CSS_SELECTOR, f"ul.{constants.JOB_FOOTER_UL_CLASS}"
            )
            soup = BeautifulSoup(footer.get_attribute("innerHTML"), "html.parser")
            return "Promoted" in soup.get_text()
        except:
            return False

    def setup_driver(self):
        """
        Sets up the Selenium WebDriver.
        """
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome()
        self.waiter = WebDriverWait(self.driver, 10)

    def login(self):
        """
        Log in to LinkedIn.
        """
        self.driver.get(constants.LOGIN_URL)
        username = self.driver.find_element(By.ID, constants.USERNAME_FIELD_ID)
        password = self.driver.find_element(By.ID, constants.PASSWORD_FIELD_ID)
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
        username.send_keys(self.config.LINKEDIN_EMAIL)
        password.send_keys(self.config.LINKEDIN_PASSWORD)
        submit.click()
        self.waiter.until(lambda driver: driver.current_url != constants.LOGIN_URL)

    def navigate_to_search_page(
        self,
        keyword: str,
        checkpoint: int,
        date_posted_range: constants.LinkedinPostDateRange,
    ):
        """
        Navigates to the search page for a given keyword.

        Args:
            keyword (str): The keyword to search for.
            checkpoint (int): The checkpoint to start from.
        """
        search_url = f"{constants.SEARCH_BASE_URL}?f_JT=F&f_TPR={date_posted_range.value}&f_WT=2&geoId=91000000&keywords={keyword}&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD&start={checkpoint}"
        self.driver.get(search_url)

    def get_jobs_list(self) -> List[WebElement]:
        """
        Gets the list of jobs from the current search page.

        Returns:
            list: The list of jobs.
        """
        return self.driver.find_elements(
            By.CSS_SELECTOR, f"li.{constants.JOB_LI_CLASS}"
        )

    def focus_on_job(self, job: WebElement):
        """
        Focuses on a job.

        Args:
            job (WebElement): The job to focus on.
        """
        job.click()
        time.sleep(2)
        job.find_element(By.TAG_NAME, "a").click()

    def extract_job_data(self, job: WebElement) -> LinkedinJob:
        """
        Extracts data from a job.

        Args:
            job (WebElement): The job to extract data from.

        Returns:
            LinkedinJob: The extracted data.
        """
        title_link = job.find_element(By.TAG_NAME, "a")
        return LinkedinJob(
            id=job.get_attribute(constants.JOB_ITEM_ID_ATTRIBUTE),
            title=title_link.get_attribute(constants.JOB_ITEM_TITLE_ATTRIBUTE),
            company=job.find_element(
                By.CSS_SELECTOR, f"span.{constants.JOB_ITEM_COMPANY_SPAN_CLASS}"
            ).text,
            location=job.find_element(
                By.CSS_SELECTOR, f"li.{constants.JOB_ITEM_LOCATION_LI_CLASS}"
            ).text,
            description=self.__get_selected_job_description(),
        )

    def crawl_job(self, job: WebElement) -> LinkedinJob:
        """
        Crawls a single job.

        Args:
            job (WebElement): The job to crawl.

        Returns:
            LinkedinJob: The extracted data.
        """
        self.focus_on_job(job)
        time.sleep(3)
        return self.extract_job_data(job)

    def crawl_jobs(
        self,
        keyword: str,
        date_posted_range: constants.LinkedinPostDateRange,
        callback: callable,
    ) -> List[LinkedinJob]:
        """
        Crawls jobs for a given keyword.

        Args:
            keyword (str): The keyword to search for.
            date_posted_range (constants.LinkedinPostDateRange): last week or last month.
            callback (callable): The callback to call for each job.

        Returns:
            List[LinkedinJob]: The extracted data
        """
        checkpoint = 0
        return_data = []

        while True:
            self.navigate_to_search_page(keyword, checkpoint, date_posted_range)
            time.sleep(10)
            jobs = self.get_jobs_list()
            if all([self.__is_job_promoted(job) for job in jobs]):
                break
            for job in jobs:
                try:
                    job_data = self.crawl_job(job)
                    return_data.append(job_data)
                    callback(job_data)
                except StaleElementReferenceException:
                    continue
            checkpoint += 25

        return return_data

    def close_driver(self):
        """
        Closes the Selenium WebDriver.
        """
        self.driver.quit()
