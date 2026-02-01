import time, base64, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os 
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("CAPCHA_API_KEY")

# Use project dir for captcha temp file (not CWD which may vary)
BOT_DIR = os.path.dirname(os.path.abspath(__file__))

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
        captcha_path = os.path.join(BOT_DIR, "captcha.png")
        captcha_img.screenshot(captcha_path)

        captcha_text = solve_captcha(captcha_path)
        if not captcha_text:
            return []

        driver.find_element(By.ID, "captcha").send_keys(captcha_text)
        driver.find_element(By.ID, "submit").click()

        # Wait for results to load (up to 10 seconds)
        time.sleep(5)
        results = []
        
        # Try multiple selectors - eCourts may use different structures
        selectors = [
            (By.CLASS_NAME, "case_details"),
            (By.CSS_SELECTOR, ".case_details"),
            (By.CSS_SELECTOR, "table.table-bordered tbody tr"),
            (By.CSS_SELECTOR, "[class*='case']"),
        ]
        
        for by, selector in selectors:
            try:
                rows = driver.find_elements(by, selector)
                for r in rows:
                    text = r.text.strip()
                    if text and len(text) > 5:
                        results.append(text)
                if results:
                    break
            except Exception:
                continue

        return results

    except Exception as e:
        print(f"Error searching case for {name}: {e}")
        return []
    
    finally:
        if driver:
            driver.quit()
        # Cleanup captcha image (check both CWD and bot dir)
        for path in ["captcha.png", os.path.join(BOT_DIR, "captcha.png")]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass