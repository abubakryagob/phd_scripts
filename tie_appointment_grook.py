from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def setup_driver():
    # Set up Chrome options
    chrome_options = Options()
    # Uncomment the next line to run headless (without opening browser window)
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def snipe_appointment():
    driver = setup_driver()
    
    try:
        # Open the website
        driver.get("https://sede.administracionespublicas.gob.es/pagina/index/directorio/icpplus")
        
        # Click "Acceder al Procedimiento"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Acceder al Procedimiento"))
        ).click()
        
        # Select Barcelona from PROVINCIAS DISPONIBLES
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "form"))
        )
        province_select = driver.find_element(By.ID, "form")
        province_select.send_keys("Barcelona")
        
        # Click first Aceptar
        driver.find_element(By.NAME, "btnAceptar").click()
        
        # Select "Cualquier oficina"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "oficina"))
        )
        office_select = driver.find_element(By.ID, "oficina")
        office_select.send_keys("Cualquier oficina")
        
        # Select the specific trámite
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tramiteGrupo[1]"))
        )
        tramite_select = driver.find_element(By.ID, "tramiteGrupo[1]")
        tramite_select.send_keys("POLICÍA-TOMA DE HUELLAS (EXPEDICIÓN DE TARJETA) INICIAL, RENOVACIÓN, DUPLICADO Y LEY 14/2013")
        
        # Click second Aceptar
        driver.find_element(By.NAME, "btnAceptar").click()
        
        # Select "Presentación sin Cl@ve"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Presentación sin Cl@ve')]"))
        ).click()
        
        # Fill in the form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtIdCitado"))
        )
        
        # Enter NIE
        driver.find_element(By.ID, "txtIdCitado").send_keys("Y8087885H")
        
        # Enter Name
        driver.find_element(By.ID, "txtDesCitado").send_keys("ABUBAKR YAGOB ABBAKAR IBRAHIM")
        
        # Select Sudan from country dropdown
        country_select = driver.find_element(By.ID, "txtPaisNac")
        country_select.send_keys("SUDAN")
        
        # Click final Aceptar
        driver.find_element(By.NAME, "btnAceptar").click()
        
        # Here you would add logic to select an available appointment
        # This part depends on how the appointment selection page looks
        print("Reached appointment selection page successfully")
        
        # Keep the browser open for 10 seconds to see the result
        time.sleep(10)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # Run continuously with a delay between attempts
    while True:
        snipe_appointment()
        time.sleep(60)  # Wait 1 minute before next attempt

'''
To use this script, you'll need to:
Install required packages:
bash
pip install selenium webdriver-manager
Download ChromeDriver that matches your Chrome browser version (the webdriver-manager can handle this automatically if you modify the script slightly)
Notes about the script:
It includes error handling and waits for elements to load
It runs continuously with a 1-minute delay between attempts
The browser window stays visible (remove the comment from --headless to run without seeing the browser)
You'll need to add logic for the final appointment selection step based on how that page looks
To make it a true "sniper" bot, you might want to:
Add logic to detect available appointments
Reduce the sleep time between attempts
Add notification when an appointment is successfully booked
Add error recovery for CAPTCHA or other anti-bot measures
Would you like me to:
Modify the delay between attempts?
Add notification functionality?
Adjust any of the selection criteria?
Add appointment selection logic (I'd need more details about that page)?
Also, note that some government websites have strict anti-bot measures, so you might need to:
Add random delays
Handle CAPTCHA if present
Use proxy rotation if needed
Add user-agent rotation
Let me know how you'd like to proceed or if you need any specific modifications!
'''
