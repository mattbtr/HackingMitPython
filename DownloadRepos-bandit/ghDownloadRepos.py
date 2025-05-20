from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


# Liste von URLs
repo_urls = [
    "https://github.com/mattbtr/flutter_empty_application_1"
]
# keine Github-Repo-Url sondern die richtige URL-Adresse der Website
#"https://github.com/mattbtr/flutter_empty_application_1.git",
#"https://github.com/mattbtr/HackingMitPython.git",
#"https://github.com/mattbtr/MobSys_u_Cloud-A3-notesApp_devOps.git",
#"https://github.com/mattbtr/Supreme-Elements.git"  


# Zielverzeichnis lokal 
download_dir = os.path.abspath("downloads")

# Chrome Optionen für automatisches Herunterladen
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.dircetory_upgrade": True,
    "safebrowsing.enabled": True
})

chrome_options.add_argument("--headless=new")       # Ohne GUI starten
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Brownser starten mit webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Repos durchgehen
for url in repo_urls:
    print(f"Lade gerade Repo von {url} herunter ...")
    driver.get(url)
    time.sleep(2)       # Warten bis Seite geladen ist

    try:
        # Code Button auf Github klicken
        wait = WebDriverWait(driver, 10)    # Warte, bis „Code“-Button sichtbar ist
        code_button = wait.until(EC.presence_of_element_located((By.XPATH, "//summary[contains(text(), 'Code')]")))
        code_button.click()
        time.sleep(1)

        # Download Zip Link klicken
        zip_link = driver.find_element(By.XPATH, "//a[contains(@href, '/zipball/')]")
        zip_url = zip_link.get_attribute("href")
        print(f"Zip link der heruntergeladen wird: {zip_url}")
        driver.get(zip_url)

        # Warten bis Download abgeschlossen ist (ungefähr)
        time.sleep(5)

    except Exception as e:
        print(f"Fehler bei {url}: {e}")

# Browser schließen
driver.quit()
print("Alle zips heruntergeladen")
