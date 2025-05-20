from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os


# Liste von URLs
repo_urls = [
    "https://github.com/mattbtr/HackingMitPython.git",
    "https://github.com/mattbtr/flutter_empty_application_1.git",
    "https://github.com/mattbtr/MobSys_u_Cloud-A3-notesApp_devOps.git",
    "https://github.com/mattbtr/Supreme-Elements.git"  
]


# Zielverzeichnis lokal 
download_dir = os.path.abspath("downloads")

# Chrome Optionen für automatisches Herunterladen
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download,dircetory_upgrade": True,
    "safebrwosing.enabled": True
})
chrome_options.add_argument("--headless")       # Ohne GUI starten
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Brownser starten
driver = webdriver.Chrome(options=chrome_options)

# Repos durchgehen
for url in repo_urls:
    print(f"Lade gerade Repo von {url} herunter ...")
    driver.get(url)
    time.sleep(2)       # Warten bis Seite geladen ist

    try:
        # Code Button auf Github klicken
        code_button = driver.find_element(By.XPATH, "//summary[contains(text(), 'Code')]")
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
