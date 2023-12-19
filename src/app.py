from config import Config
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
import urllib.parse
from functools import wraps

from typing import Any, Optional
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from time import sleep
import random
from src import linkedin
from selenium.common.exceptions import StaleElementReferenceException
import json
import os
def retries_decorator(retries=10, quit=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"{func.__name__} error: {str(e)}")
                    continue

            if quit:
                quit()
            raise Exception(f"{func.__name__} failed after {retries} retries")
        return wrapper
    return decorator

def my_decorator(quit=False,confirm=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                if not confirm:
                    break
                _in = input(f"{func.__name__}:  \"Y\" to continue :\n")
                if _in == "Y":
                    break
                elif _in == "N":
                    quit()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.warning(f"{func.__name__} error: {str(e)}")
                if quit:
                    quit()
                return None
        return wrapper
    return decorator

class App:

    def __init__(self,config=Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={self.config.CHROME_PROFILE_PATH}")
        options.add_argument("--no-sandbox")
        
        self.driver = webdriver.Chrome( options=options)
    def __call__(self, *args: Any, **kwds: Any) -> Any:

        params = [{
        'keywords': 'data specialist',
        "location": "Melbourne, Victoria, Australia",
        "f_AL": "true",
        "distance":"10"
        }]
         
        self.driver.get("https://www.linkedin.com/jobs/search/?"+urllib.parse.urlencode(params[0]))
        self.implicitly_wait()
        # 3 get all job cards

        job_cards = self.driver.find_elements(By.XPATH, "//div[@data-job-id]")
        print(f"job_cards length {len(job_cards)}")

        # 4 for each job card
        iteration = -1
        while True:
            iteration += 1
            if iteration > self.config.LIMIT:
                break

            try:
                job_cards = self.handle_navigateJobCard(job_cards,iteration)
                if not job_cards:
                    break
            except:
                # update job cards
                job_cards = self.driver.find_elements(By.XPATH, "//div[@data-job-id]")



            # get job details
            job_details = self.handle_getJobDetail()
            if not job_details:
                break

                
            # click apply to open modal
            try:
                apply_button = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.jobs-apply-button")))
                apply_button.click()
            except:
                continue

            # open modal
            #find fields
            try:
                modal = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-easy-apply-modal")))
                
            except:
                break


            # fillin modal

            field_values = []
            while True:
                self.implicitly_wait()
                self.implicitly_wait()

                field_groups = modal.find_elements(By.XPATH, ".//div[contains(@class, 'jobs-easy-apply-form-section__grouping')]")
                label_elems = modal.find_elements(By.XPATH, ".//label|.//legend")
                labels = [label.text.split("\n")[0] for label in label_elems]
                for label,field_group in zip(labels,field_groups):
                    value = self.handle_navigateFields(field_group)
                    if value:
                        field_values.append({"label":label,"value":value})

                self.logger.info(f"fields length {len(field_groups)}")

                # click next until dismiss or apply
                if not self.handle_nextUntilDismiss(modal):
                    # end of modal
                    break

            

            job_details = {**job_details,"field_values":field_values}
            self.handle_appendData(job_details)
    
    def implicitly_wait(self):
        time = self.config.IMPLICIT_WAIT*(1+random.random())/2
        self.logger.info(f"implicitly_wait {time}")
        self.driver.implicitly_wait(time)
        sleep(2)

        
    def isLoggedin(self):

        self.driver.get("https://www.linkedin.com/jobs/search/?f_LF=f_AL&geoId=103644278&keywords=software%20engineer&location=United%20States")
        pass

    def handle_navigateJobCard(self,job_cards,iteration):
        try:
            # focus on job card
            self.driver.execute_script("arguments[0].scrollIntoView();", job_cards[iteration])
            # click on job card
            job_cards[iteration].click()
        except IndexError or StaleElementReferenceException:
            job_cards = self.driver.find_elements(By.XPATH, "//div[@data-job-id]")
        finally:    
            sleep(self.config.SLEEP_TIME)

        return job_cards
    
    def handle_getJobDetail(self):
        try:
            job_panel = WebDriverWait(self.driver,5).until(
                EC.presence_of_all_elements_located((
                    By.XPATH,
                    "//div[@class='job-details-jobs-unified-top-card__content--two-pane']"
                ))
            )[0]
            job_title = WebDriverWait(job_panel,5).until(
                EC.presence_of_all_elements_located((
                    By.XPATH,
                    ".//span[@class='job-details-jobs-unified-top-card__job-title-link']"
                ))
            )[0].text

            job_details = WebDriverWait(job_panel,1).until(
                EC.presence_of_all_elements_located((
                    By.XPATH,
                    ".//div[@class='job-details-jobs-unified-top-card__primary-description-without-tagline mb2']"
                ))
            )[0].text
            job_details_dict= {
                "title": job_title, 
                "details":job_details
                }

            return job_details_dict

        except Exception as e:
            raise e
    def handle_navigateFields(self,field_group):
        field_input = field_group.find_elements(By.XPATH, ".//input|.//select")[0]
        match field_input.tag_name:
            case "input":
                # if input is not empty
                if not field_input.get_attribute("value"):
                    field_input.send_keys("3")
                value = field_input.get_attribute("value")                    
            case "select":
                select = Select(field_input)
                select.select_by_index(1)
                value = field_input.get_attribute("value")

            case _:
                value = None
        return value
    
    def handle_nextUntilDismiss(self,modal):
        try:
            next_button = WebDriverWait(modal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Continue to next step']")))
            next_button.click()
            return True

        except:
            # click review
            review_button = WebDriverWait(modal, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Review your application']")))
            review_button.click()

            # click submit
            
            if self.config.APPLY:
                submit_button = WebDriverWait(modal, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Submit application']")))
                submit_button.click()
                self.implicitly_wait()

                # click blank space on modal data-test-modal-id="easy-apply-modal"
                dismiss_button = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Dismiss']")))
                dismiss_button.click()
                self.implicitly_wait()
            else:
                dismiss_button = WebDriverWait(modal, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Dismiss']")))
                dismiss_button.click()
                self.implicitly_wait()
                discard_button = modal.find_element(By.XPATH, "//span[text()='Discard']")
                discard_button.click()
                self.implicitly_wait()
            return False

    def handle_appendData(self,data):
        
        # if file does not exist create json
        if not os.path.exists(self.config.STORAGE):
            open(self.config.STORAGE, "w").write("[]")

        # append data to file
        with open(self.config.STORAGE, "r") as f:
            content = json.load(f)
            content.append(data)
            json.dump(content, open(self.config.STORAGE, "w"), indent=4)
            