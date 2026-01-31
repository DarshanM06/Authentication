import time, base64, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os 
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("CAPCHA_API_KEY")

def solve_captcha(image_path):
    try:
        with open(image_path, "rb") as f:
            img = base64.b64encode(f.read()).decode()

        r = requests.post("http://2captcha.com/in.php", data={
            "key": API_KEY,
            "method": "base64",
            "body": img,
            "json": 1
        }).json()

        if "error" in r or r.get("status") == 0:
            raise Exception(f"Captcha API error: {r}")

        captcha_id = r["request"]
        time.sleep(15)

        while True:
            res = requests.get(
                f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1"
            ).json()

            if res["status"] == 1:
                return res["request"]
            time.sleep(5)
    except Exception as e:
        print(f"Captcha solving failed: {e}")
        return None

def search_case(name):
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
        time.sleep(5)

        driver.find_element(By.ID, "radParty").click()
        driver.find_element(By.ID, "partyname").send_keys(name)

        captcha_img = driver.find_element(By.ID, "captcha_image")
        captcha_img.screenshot("captcha.png")

        captcha_text = solve_captcha("captcha.png")
        if not captcha_text:
            return []

        driver.find_element(By.ID, "captcha").send_keys(captcha_text)
        driver.find_element(By.ID, "submit").click()

        time.sleep(6)

        results = []
        rows = driver.find_elements(By.CLASS_NAME, "case_details")
        for r in rows:
            results.append(r.text)

        return results

    except Exception as e:
        print(f"Error searching case for {name}: {e}")
        return []
    
    finally:
        if driver:
            driver.quit()
        # Cleanup captcha image
        if os.path.exists("captcha.png"):
            os.remove("captcha.png")