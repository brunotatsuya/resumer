from enum import Enum

LOGIN_URL = "https://www.linkedin.com/login"
SEARCH_BASE_URL = "https://www.linkedin.com/jobs/search"

USERNAME_FIELD_ID = "username"
PASSWORD_FIELD_ID = "password"
JOB_DETAILS_DIV_ID = "job-details"
JOB_FOOTER_UL_CLASS = "job-card-list__footer-wrapper"
JOB_LI_CLASS = "jobs-search-results__list-item"
JOB_ITEM_ID_ATTRIBUTE = "data-occludable-job-id"
JOB_ITEM_TITLE_ATTRIBUTE = "aria-label"
JOB_ITEM_COMPANY_SPAN_CLASS = "job-card-container__primary-description"
JOB_ITEM_LOCATION_LI_CLASS = "job-card-container__metadata-item"


class LinkedinPostDateRange(Enum):
    LAST_WEEK = "r86400"
    LAST_MONTH = "r2592000"
