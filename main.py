import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Locally stored username and password hashtag security hashtag we did it
mscan_username = os.getenv("mscanuser")
mscan_password = os.getenv("mscanpw")

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

# Navigate to the partner login page
login_url = "https://portal.mscanapi.com/#/Partner/Login"
driver.get(login_url)

try:
    # Wait for the partner ID input field to be visible
    partner_id_input = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, "input[data-v-a178893e]"))
    )
    partner_id_input.send_keys(mscan_username)

    # Wait for the password input field to be visible
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

    # Wait for the "Create an Account" button to be clickable
    create_account_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.q-btn--outline.text-primary"))
    )

    # Click the "Create an Account" button
    create_account_button.click()

    # Wait for the "Dealership Name" input field to be interactable
    dealership_name_field_interactable = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Dealership Name']"))
    )

    # Locate the remaining form fields
    street_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Street']"))
    )
    city_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='City']"))
    )

    # Open the CSV file and populate the form fields
    with open('onboarding.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Check the .csv file for the field names required to fill out the form
            if row[0].strip() == "Dealer Name":
                # Get the dealership name from the second column
                dealership_name = row[1].strip()

                # Enter the dealership name
                dealership_name_field_interactable.send_keys(dealership_name)

            elif row[0].strip() == "Street Address":
                # Get the street address from the second column
                street_address = row[1].strip()

                # Enter the street address
                street_field.send_keys(street_address)

            elif row[0].strip() == "City":
                # Get the city name from the second column
                city_name = row[1].strip()

                # Enter the city name
                city_field.send_keys(city_name)

    # Wait for the "Country" dropdown icon to be present
    country_dropdown_icon = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "i.q-icon.q-select__dropdown-icon"))
    )

    # Click the "Country" dropdown icon
    country_dropdown_icon.click()

    # Wait for the "USA" option to be present and click it
    usa_option = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'q-menu')]//div[contains(@class, 'q-item__label')]//span[text()='USA']"))
    )
    usa_option.click()

    # Wait for the user to manually close the browser window
    print("Press Enter to close the browser and exit the script.")
    input()

finally:
    # Close the browser
    driver.quit()