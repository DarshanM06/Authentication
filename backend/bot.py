import time, base64, requests, re, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from districts import STATES_DISTRICTS
from matcher import is_match
from address import extract_state_city

load_dotenv()
API_KEY = os.getenv("CAPTCHA_API_KEY")

def solve_captcha(path):
    with open(path,"rb") as f:
        img = base64.b64encode(f.read()).decode()
    r = requests.post("http://2captcha.com/in.php", data={
        "key":API_KEY,"method":"base64","body":img,"json":1
    }).json()
    cid = r["request"]
    time.sleep(15)
    while True:
        res = requests.get(
            f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={cid}&json=1"
        ).json()
        if res["status"] == 1:
            return res["request"]
        time.sleep(5)

def extract_cnr(text):
    m = re.search(r"\b[A-Z0-9]{16}\b", text)
    return m.group(0) if m else ""

def verify_person(candidate):
    state, city = extract_state_city(candidate["Address"])
    if not state:
        return {"Name": candidate["Name"], "CNR": "", "Status": "NO CASE"}

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
    time.sleep(4)

    Select(driver.find_element(By.ID,"state_code")).select_by_visible_text(state)
    time.sleep(2)

    for district in STATES_DISTRICTS[state]:
        if city and city.lower() not in district.lower():
            continue

        Select(driver.find_element(By.ID,"dist_code")).select_by_visible_text(district)
        time.sleep(1)

        driver.find_element(By.ID,"radParty").click()
        driver.find_element(By.ID,"partyname").clear()
        driver.find_element(By.ID,"partyname").send_keys(candidate["Name"])

        cap_img = driver.find_element(By.ID,"captcha_image")
        cap_img.screenshot("cap.png")
        captcha = solve_captcha("cap.png")

        driver.find_element(By.ID,"captcha").send_keys(captcha)
        driver.find_element(By.ID,"submit").click()
        time.sleep(4)

        rows = driver.find_elements(By.CLASS_NAME,"case_details")
        for r in rows:
            txt = r.text.lower()
            if is_match(
                txt,
                candidate["Name"].lower(),
                candidate["Father"].lower(),
                candidate["Address"].lower()
            ):
                cnr = extract_cnr(r.text)
                driver.quit()
                return {
                    "Name": candidate["Name"],
                    "CNR": cnr,
                    "Status": "CASE FOUND"
                }

    driver.quit()
    return {
        "Name": candidate["Name"],
        "CNR": "",
        "Status": "NO CASE"
    }