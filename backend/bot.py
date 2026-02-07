import os, time, base64, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from districts import STATES_DISTRICTS
from match import is_probable_match
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CAPTCHA_API_KEY")

def solve_captcha(path):
    with open(path,"rb") as f:
        img = base64.b64encode(f.read()).decode()
    r = requests.post("http://2captcha.com/in.php", data={
        "key":API_KEY,"method":"base64","body":img,"json":1
    }).json()
    captcha_id = r["request"]
    time.sleep(15)
    while True:
        res = requests.get(
            f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1"
        ).json()
        if res["status"]==1:
            return res["request"]
        time.sleep(5)

def search_candidate(candidate):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
    time.sleep(4)

    Select(driver.find_element(By.ID,"state_code")) \
        .select_by_visible_text(candidate["State"])
    time.sleep(2)

    results = []
    for district in STATES_DISTRICTS[candidate["State"]]:
        Select(driver.find_element(By.ID,"dist_code")) \
            .select_by_visible_text(district)
        time.sleep(1)

        driver.find_element(By.ID,"radParty").click()
        driver.find_element(By.ID,"partyname").clear()
        driver.find_element(By.ID,"partyname").send_keys(candidate["Name"])

        captcha_img = driver.find_element(By.ID,"captcha_image")
        captcha_img.screenshot("cap.png")
        captcha = solve_captcha("cap.png")

        driver.find_element(By.ID,"captcha").send_keys(captcha)
        driver.find_element(By.ID,"submit").click()
        time.sleep(4)

        rows = driver.find_elements(By.CLASS_NAME,"case_details")
        for r in rows:
            text = r.text.lower()
            row_data = {
                "party": text,
                "address": text,
                "raw": r.text,
                "district": district,
                "state": candidate["State"]
            }
            if is_probable_match(row_data,
                candidate["Name"].lower(),
                candidate["Father"].lower(),
                candidate["City"].lower()):
                results.append(row_data)

    driver.quit()
    return results