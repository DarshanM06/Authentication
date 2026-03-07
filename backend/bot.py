import time, base64, requests, re, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from districts import STATES_DISTRICTS
from matcher import is_match
from address import extract_state_city
import itertools
import random
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

load_dotenv()
API_KEY = os.getenv("CAPTCHA_API_KEY")
MAX_RETRIES = 3

def solve_captcha(path):
    with open(path,"rb") as f:
        img = base64.b64encode(f.read()).decode()
    r = requests.post("http://2captcha.com/in.php", data={
        "key":API_KEY,"method":"base64","body":img,"json":1
    }).json()
    
    if r.get("status") == 0:
        print(f"2Captcha Error: {r.get('request')}")
        return None
        
    cid = r["request"]
    time.sleep(15)
    
    for _ in range(24): # Max 2 minutes wait
        res = requests.get(
            f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={cid}&json=1"
        ).json()
        if res.get("status") == 1:
            return res.get("request")
        if res.get("request") == "ERROR_CAPTCHA_UNSOLVABLE":
            print("2Captcha could not solve this image.")
            return None
        time.sleep(5)
        
    print("2Captcha timed out.")
    return None

def extract_cnr(text):
    m = re.search(r"\b[A-Z0-9]{16}\b", text)
    return m.group(0) if m else ""

def generate_name_permutations(name):
    """Generate combinations of name up to 3 words to avoid exponential API calls."""
    words = [w for w in name.strip().split() if w]
    if len(words) <= 1:
        return [name]
    
    # Cap at 3 words to prevent excessive captchas (max 6 permutations)
    if len(words) > 3:
        words = words[:3]
        
    perms = list(itertools.permutations(words))
    return [" ".join(p) for p in perms]

def verify_person(candidate):
    state, city = extract_state_city(candidate["Address"])
    if not state:
        return {"Name": candidate["Name"], "CNR": "", "Status": "NO CASE - State Extraction Failed"}

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Generate name variations
    name_variations = generate_name_permutations(candidate["Name"])
    print(f"Checking permutations for {candidate['Name']}: {name_variations}")

    try:
        driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index")
        time.sleep(random.uniform(4, 6))

        Select(driver.find_element(By.ID,"state_code")).select_by_visible_text(state)
        time.sleep(random.uniform(2, 3))

        for district in STATES_DISTRICTS.get(state, []):
            if city and city.lower() not in district.lower():
                continue

            Select(driver.find_element(By.ID,"dist_code")).select_by_visible_text(district)
            time.sleep(random.uniform(1, 2))

            current_year = datetime.now().year
            
            for name_variant in name_variations:
                for target_year in range(current_year, current_year - 10, -1):
                    for attempt in range(MAX_RETRIES):
                        try:
                            driver.find_element(By.ID,"radParty").click()
                            time.sleep(random.uniform(0.5, 1.5))
                            
                            party_input = driver.find_element(By.ID,"partyname")
                            party_input.clear()
                            party_input.send_keys(name_variant)
                            
                            year_input = driver.find_element(By.ID,"casereg_year")
                            year_input.clear()
                            year_input.send_keys(str(target_year))
                            
                            # Select 'Both' (Pending and Disposed)
                            try:
                                both_radio = driver.find_element(By.ID, "radBoth")
                                if not both_radio.is_selected():
                                    both_radio.click()
                            except:
                                pass # Some courts might default or not have this exact ID

                            cap_img = driver.find_element(By.ID,"captcha_image")
                            cap_img.screenshot("cap.png")
                            captcha = solve_captcha("cap.png")
                            
                            if not captcha:
                                continue # Retry if captcha solved failed

                            print(f"Trying: {name_variant} | Year: {target_year} | District: {district}")
                            driver.find_element(By.ID,"captcha").clear()
                            driver.find_element(By.ID,"captcha").send_keys(captcha)
                            driver.find_element(By.ID,"submit").click()
                            time.sleep(random.uniform(4, 6))

                            rows = driver.find_elements(By.CLASS_NAME,"case_details")
                            
                            # Handle no records found or captcha error messages explicitly
                            error_msgs = driver.find_elements(By.ID, "errSpan")
                            if error_msgs and any(e.is_displayed() for e in error_msgs):
                                print(f"Error span detected, indicating captcha or search failure. Retrying...")
                                continue # Loop back up to try again

                            for r in rows:
                                txt = r.text.lower()
                                if is_match(
                                    txt,
                                    candidate["Name"].lower(), # Match against original or variant, is_match typically looks for substrings
                                    candidate.get("Father", "").lower(),
                                    candidate.get("Address", "").lower()
                                ):
                                    cnr = extract_cnr(r.text)
                                    driver.quit()
                                    return {
                                        "Name": candidate["Name"],
                                        "Matched_Name": name_variant,
                                        "Matched_Year": str(target_year),
                                        "CNR": cnr,
                                        "Status": "CASE FOUND"
                                    }
                            
                            # If we completed the search and no rows matched for THIS YEAR, proceed to next year
                            break # Break out of MAX_RETRIES loop

                        except (TimeoutException, NoSuchElementException) as e:
                            print(f"Element not found or timed out ({e}). Attempt {attempt + 1}/{MAX_RETRIES}")
                            time.sleep(3)
                        
    except Exception as e:
        print(f"Critical driver failure logic: {e}")
        driver.quit()
        return {"Name": candidate["Name"], "CNR": "", "Status": f"ERROR: {str(e)}"}
        
    driver.quit()
    return {
        "Name": candidate["Name"],
        "CNR": "",
        "Status": "NO CASE"
    }