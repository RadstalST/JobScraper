# from config import Config
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import logging
# import urllib.parse
# from functools import wraps

# from typing import Optional
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
# from time import sleep

# from src import linkedin

# import json
# import os

# def retries_decorator(retries=10, quit=False):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             for _ in range(retries):
#                 try:
#                     return func(*args, **kwargs)
#                 except Exception as e:
#                     logging.warning(f"{func.__name__} error: {str(e)}")
#                     continue

#             if quit:
#                 quit()
#             raise Exception(f"{func.__name__} failed after {retries} retries")
#         return wrapper
#     return decorator

# def my_decorator(quit=False,confirm=False):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             while True:
#                 if not confirm:
#                     break
#                 _in = input(f"{func.__name__}:  \"Y\" to continue :\n")
#                 if _in == "Y":
#                     break
#                 elif _in == "N":
#                     quit()
#             try:
#                 return func(*args, **kwargs)
#             except Exception as e:
#                 logging.warning(f"{func.__name__} error: {str(e)}")
#                 if quit:
#                     quit()
#                 return None
#         return wrapper
#     return decorator

# class App:
#     USER_ID = 0
#     LIMIT = 20
#     RETRIES = 10
#     STORAGE = "./out/ouput.json"
#     def __init__(self):
#         self.name = Config.APP_NAME
#         self.jobs = Config.JOBS
#         logging.basicConfig(level=logging.INFO)
#         logging.info("App initialized")
        
        
#     def __call__(self):
#         platforms = self.jobs.keys()
        

#         if "linkedin" in platforms:
#             logging.info("LinkedIn jobs found :")
#             for job in self.jobs["linkedin"]:
#                 print(f" - {job}")

#             params = [{
#             'keywords': 'data analyst',
#             "location": "Melbourne, Victoria, Australia",
#             "f_AL": "true",
#             "distance":"10"
#             }]

#             for param in params:
#                 self.handle_linkedin(param)

#     def handle_linkedin(self,param):

#         try:
#             driver = self.handle_init_driver()
#             driver.get("https://www.linkedin.com")
#             driver.implicitly_wait(Config.IMPLICIT_WAIT)

            
#             logging.info("Opening LinkedIn jobs page")
#             self.handle_linkedinSearch(param)


#             # find iterable on linkedin job info
#             job_cards = self.handle_extract_jobIterable()
#             logging.info(f"job_cards length {len(job_cards)}")
#             # iterate over job_cards and then extract

#             iteration = 0

#             while True:
#                 iteration += 1
#                 if iteration > self.LIMIT:
#                     break
#                 try:
#                     # click job_cards and then extract
#                     jobs_info = self.handle_extractJobInfo(job_cards[iteration])


#                     # find iterable on linkedin job info
#                     job_cards = self.handle_extract_jobIterable()
#                     logging.info(f"job_cards length {len(job_cards)}")
                    
                    
#                 except Exception as e:
#                     logging.warn(f"error {str(e)}")
#                     break

        
#         except Exception as e:
#             raise e
#             # return
        
#         finally:
#             self.driver.quit()

#         pass

#     def handle_init_driver(self,options: Optional[webdriver.ChromeOptions] = None)-> webdriver.Chrome:

#         logging.info("Initializing Chrome driver")
#         if options== None:
#             options = webdriver.ChromeOptions()
#             options.add_argument("--start-maximized")
#             options.add_argument(f"user-data-dir={Config.CHROME_PROFILE_PATH}")


#         self.driver = webdriver.Chrome(options=options)
#         logging.info("Chrome driver initialized")
#         self.driver.implicitly_wait(Config.IMPLICIT_WAIT)

#         return self.driver
    
#     @my_decorator(confirm=True)
#     def handle_linkedinSearch(self, param:dict):

#         self.driver.get("https://www.linkedin.com/jobs/search/?"+urllib.parse.urlencode(param))
#         self.driver.implicitly_wait(Config.IMPLICIT_WAIT)


#     @my_decorator(confirm=False)
#     def handle_extract_jobIterable(self):
        
#         return self.driver.find_elements(by=By.XPATH, value="//div[contains(@class, 'artdeco-entity-lockup__title')]/../..")



#     @my_decorator(confirm = False)
#     def handle_extractJobInfo(self,card):
#         job_info =dict( )
#         try:
#             # center on element
#             self.driver.execute_script("arguments[0].scrollIntoView();", card)
#             # click on element
#             self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
#             card.click()
#             self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
#             sleep(Config.SLEEP_TIME)


#             title = card.find_elements(by=By.XPATH, value="./child::div/div[contains(@class, 'artdeco-entity-lockup__title')]")
#             company = card.find_elements(by=By.XPATH, value="./child::div/div[contains(@class, 'artdeco-entity-lockup__subtitle')]")
#             location = card.find_elements(by=By.XPATH, value="./child::div/div[contains(@class, 'artdeco-entity-lockup__caption')]")
#             job_info = {
#                 "title":title[0].text if title[0] else None,
#                 "company": company[0].text if company[0] else None,
#                 "location":location[0].text if location[0] else None,
#             }
        
#             #click easy apply
#             self.handle_clickEasyApply()

#             # go trough easy apply modal
#             modal = self.handle_easyApplyModal()

#             # fill in easy apply modal
#             try:
#                 fields = linkedin.fillin_modal(modal,self.driver,quick_apply=Config.QUICK_APPLY)
#                 job_info = {**job_info, "fields":fields}
#             except Exception as e:
#                 raise e
                
            
            
            
#         except Exception as e:
#             raise e
#             job_info = {
#                 **job_info,
#                 "error": str(e)
#             }
#         finally:
#             print(job_info)
#             self.handle_storeJobInfo(job_info)
#             return job_info
#     def handle_autoApply(self):

#         pass
#     def handle_storeJobInfo(self,data):
#         logging.debug(f"handle_storeJobInf storing {data}")

#         #if file does not exist, create it
#         if not os.path.exists(self.STORAGE):
#             open(self.STORAGE, "w").write("[]")

#         #append data to file
#         with open(self.STORAGE, "r") as f:
#             content = json.load(f)
#             content.append(data)
#             json.dump(content, open(self.STORAGE, "w"), indent=4)


        

#     @retries_decorator(quit=True)
#     def handle_clickEasyApply(self):
#         self.driver.implicitly_wait(1)
#         easy_apply_button = self.driver.find_element(By.CLASS_NAME, "jobs-apply-button")
#         easy_apply_button.click()
#         return True
    

#     @retries_decorator(quit=True)
#     def handle_easyApplyModal(self):
#         modal = self.driver.find_element(By.CLASS_NAME, "jobs-easy-apply-modal")
#         self.driver.implicitly_wait(1)
#         return modal