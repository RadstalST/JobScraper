from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import json

def handle_field(label, field_group,answer_path = "out/answers.json",quick_apply=False):
    ret = {"value": None,"options": None}

    
    def get_answer(label):
        try:
            answers = json.load(open(answer_path))

            label = label.strip()
            try:
                optionlen = len(answers[answers["field_name"] == label]["options"][0])
            except:
                optionlen = 0
            return  {
                "answer": answers[answers["field_name"]==label]["value"].values[0],
                "type": "input" if optionlen == 0 else "select"
            }
        except:
            return None

                

    answer = get_answer(label)

    if answer and  quick_apply:
        match answer["type"]:
            case "select":
                elem = field_group.find_element(By.CSS_SELECTOR, "select")
                select = Select(elem)
                try:
                    select.select_by_value(answer["answer"])
                except:
                    select.select_by_index(1)
                ret["value"] = elem.get_attribute("value")

            case "input":
                elem = field_group.find_element(By.CSS_SELECTOR, "input")
                elem.clear()
                elem.send_keys(answer["answer"])
                ret["value"] = elem.get_attribute("value")

    else:
        try:
            elem = field_group.find_element(By.CSS_SELECTOR, "input")
            elem.clear()
            elem.send_keys("2")
            ret["value"] = elem.get_attribute("value")
        except:
            pass

        try:
            elem = field_group.find_element(By.CSS_SELECTOR, "select")
            select = Select(elem)
            select.select_by_index(1)
            ret["value"] = elem.get_attribute("value")
            ret["options"]= [option.text for option in select.options[:5]]
        except:
            pass

        try:
            elem = field_group.find_element(By.CSS_SELECTOR, "textarea")
            elem.clear()
            elem.send_keys("N/A")
            ret["value"] = elem.get_attribute("value")
        except:
            pass

        try:
            elem = field_group.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            elem.click()
            ret["value"] = elem.get_attribute("value")
        except:
            pass
            

    return ret

def fillin_modal(modal,driver,quick_apply=False):
    logging.info("fillin_modal")
    try:
        fields = []
        while True:

            # wait for modal to load
            field_groups = modal.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")
            for i in range(len(field_groups)):
                field_groups = modal.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")
                field_group = field_groups[i]
                label = field_group.find_element(By.CSS_SELECTOR, "label")
                label_text = label.text.split("\n")[0].strip()
                fields.append({
                    "field_name": label_text,
                    **handle_field(label_text, field_group,answer_path = "out/answers.json",quick_apply=quick_apply)
                    })
           
            try:
                next_button = WebDriverWait(modal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Continue to next step']")))
                next_button.click()
            except:
                review_button = WebDriverWait(modal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Review your application']")))
                review_button.click()
                if not quick_apply:
                    dismiss_button = WebDriverWait(modal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Dismiss']")))
                    dismiss_button.click()
                    discard_button = modal.find_element(By.XPATH, "//span[text()='Discard']")
                    discard_button.click()
                    return fields
               
                submit_button = WebDriverWait(modal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Submit application']")))
                submit_button.click()

                modal_overlay = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-modal-container]")))
                modal_overlay.click()
                return fields

        return fields
    except Exception as e:
        raise(e)
        pass


def extractAnswers(path="out/ouput.json"):

    data = json.load(open('out/ouput.json'))
    fields_df = pd.json_normalize(data,record_path=["fields"])
    # select first for each field 
    fields_df = fields_df.groupby("field_name").agg({
        "field_name": "count",
        "value": "first",
        "options": "first",
    })
    fields_df.rename(columns={"field_name": "count"}, inplace=True)
    fields_df

    fields_df.to_json("out/answers.json",index=False,orient="records",indent=2)