import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Locally stored username and password hashtag security hashtag we did it
mscan_username = os.getenv("mscanuser")
mscan_password = os.getenv("mscanpw")

# Create a new instance of the shiny and Chrome driver
driver = webdriver.Chrome()

# Navigate to the partner login page in chrome driver
login_url = "https://portal.mscanapi.com/#/Partner/Login"
driver.get(login_url)

try:
    # Wait for the partner ID input field to be visible, and then enter the username variable
    partner_id_input = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, "input[data-v-a178893e]"))
    )
    partner_id_input.send_keys(mscan_username)

    # Wait for the password input field to be visible, and then enter the password variable
    password_input = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )
    password_input.send_keys(mscan_password)

    # Find and click the login button
    login_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.new-login-button"))
    )
    login_button.click()

    # Wait for the loading backdrop to disappear
    WebDriverWait(driver, 10).until_not(
        ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
    )

    # Wait for the "Create an Account" button to be clickable, and then click it
    create_account_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.q-btn--outline.text-primary"))
    )
    create_account_button.click()

    # Wait for the "Dealership Name" input field to be interactable
    dealership_name_field_interactable = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Dealership Name']"))
    )
    # locate street, city, zip and phone now that the first one is interactable
    street_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Street']"))
    )
    city_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='City']"))
    )
    phone_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Phone']"))
    )
    # select usa from dropdown here as the zip field needs to generate
    country_dropdown_icon = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "i.q-icon.q-select__dropdown-icon"))
    )
    # Click the "Country" dropdown icon
    country_dropdown_icon.click()
    # Wait for the "USA" option (set by finding it in inspect element but this isn't great) to be present and click it
    usa_option = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'q-menu')]//div[contains(@class, 'q-item__label')]//span[text()='USA']"))
    )
    usa_option.click()

    # used element to be clickable here as this one generates after USA selected in dropdown
    zip_field = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Zip']"))
    )

    # opens up the onboarding file, checks fields in the file against fields on the webform and fills them out
    with open('onboarding.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Check the .csv file for the field names required to fill out the form
            if row[0].strip() == "Dealer Name":
                dealership_name = row[1].strip()
                dealership_name_field_interactable.send_keys(dealership_name)

            elif row[0].strip() == "Street Address":
                street_address = row[1].strip()
                street_field.send_keys(street_address)

            elif row[0].strip() == "City":
                city_name = row[1].strip()
                city_field.send_keys(city_name)

            elif row[0].strip() == "Contact Phone Number (Contact 1)":
                phone_number = row[1].strip()
                phone_field.send_keys(phone_number)

            elif row[0].strip() == "Zip Code":
                zip_code = row[1].strip()
                zip_field.send_keys(zip_code)


    # input keeps script from closing out browser. user continues manually from this point.
    print("press enter to close even though you can't")
    input()

finally:
    # Close the browser
    driver.quit()
