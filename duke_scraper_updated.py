import time
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

# Set up a headless browser using Selenium
options = webdriver.FirefoxOptions()
options.add_argument('--headless')



# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

options.set_preference("browser.download.folderList", 2)  # Use custom directory
options.set_preference("browser.download.dir", script_dir)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv,text/csv")  # Specify MIME types to automatically save

# Load the Firefox browser with specified options
driver = webdriver.Firefox(options=options)



# Join the script directory with the file name
file_path = os.path.join(script_dir, 'filtered_plant_list.txt')

with open(file_path, 'r') as file:
    plant_names = file.read().splitlines()

for plant_searched in plant_names:
    print(f"searching",plant_searched)
    # Load the page using the headless browser
    base_url = 'https://phytochem.nal.usda.gov/'
    driver.get(base_url)
    # Wait for the page to load
    time.sleep(5)
    # Selecting an option from the dropdown
    plants_optgroup = driver.find_element(By.XPATH, "/html/body/div/div[2]/div/section/main/div/div[1]/form/div/div[2]/div[1]/select/optgroup[1]/option[3]")
    plants_optgroup.click()

    # Finding the input field and entering the plant name
    search_input = driver.find_element(By.XPATH, "/html/body/div/div[2]/div/section/main/div/div[1]/form/div/div[2]/div[2]/input")
    search_input.send_keys(plant_searched)

    # Finding and clicking the search button
    search_button = driver.find_element(By.XPATH, "/html/body/div/div[2]/div/section/main/div/div[1]/form/div/div[2]/div[3]/button")
    search_button.click()

    # Wait for the search results to load
    time.sleep(5)

    # Extracting and printing the results
    results_parent = driver.find_element(By.XPATH, '//*[@id="main-content"]/div/div[1]/div/div[2]')
    results = results_parent.find_elements(By.XPATH, './/div[@class="entity etP"]')

    found_plant = False
    for entry in results:
        if plant_searched.lower() in entry.text.lower():
            found_plant = True
            plant_link = entry.find_element(By.XPATH, './a').get_attribute("href")
            print(f"Found: {plant_searched}")
            print(f"Plant Link: {plant_link}")
            break

    if found_plant:
        driver.quit()
        driver = webdriver.Firefox(options=options)
        driver.get(plant_link)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Print the title of the new page
        new_page_title = soup.title.string.strip()
        print(f"New Page Title: {new_page_title}")

        # Find and click the "Download data as CSV" link on the new page
        try:
            download_link = driver.find_element(By.XPATH, '//*[@id="chemTotal"]/div/a[1]')
            download_link.click()
            time.sleep(5)  # Add a wait for the download to complete (adjust as needed)
            print("Downloading file")
        except NoSuchElementException:
            print("Download link not found on the new page")
    else:
        print(f"{plant_searched} not found")

# Close the browser window after processing all plants
driver.quit()
