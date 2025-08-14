from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.support.ui import WebDriverWait 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC 
import time 

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
try:
    driver.get("https://www.youtube.com/")
    search_box = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.NAME,"search_query"))
    )
    search_box.send_keys("jhol")
    search_box.send_keys(Keys.RETURN)
    video = WebDriverWait(driver,10).until(
        EC.presence_of_all_elements_located((By.ID,"video-title"))
    )

    video[1].click()
    time.sleep(600)
finally:
    driver.quit()