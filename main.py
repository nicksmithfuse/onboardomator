import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

# Locally stored username and password hashtag security hashtag we did it
mscan_username = os.getenv("mscanuser")
mscan_password = os.getenv("mscanpw")

# Create a new instance of the shiny and Chrome driver, maximized since there was an overlay issue, then navigate to
# the partner login page
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
login_url = "https://portal.mscanapi.com/#/Partner/Login"
driver.get(login_url)

# code for logging in, then going to the create an account page, and then filling everything out up until the state
# dropdown
try:
    # Wait for the partner ID input field to be CLICKABLE, and then enter the username variable
    partner_id_input = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name='Partner ID']"))
    )
    partner_id_input.send_keys(mscan_username)

    # Wait for the password input field to be CLICKABLE, and then enter the password variable
    password_input = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name='Password']"))
    )
    password_input.send_keys(mscan_password)

    # Find, wait for CLICKABLE, and click the login button
    login_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.new-login-button"))
    )
    login_button.click()

    # script is too fast add this everywhere it breaks
    WebDriverWait(driver, 10).until_not(
        ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
    )

    # Wait for the "Create an Account" button to be clickable, and then click it
    create_account_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.q-btn--outline.text-primary"))
    )
    create_account_button.click()

    # script is too fast add this everywhere it breaks
    WebDriverWait(driver, 10).until_not(
        ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
    )

    # Wait for the "Dealership Name" input field to be interactable
    dealership_name_field_interactable = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Dealership Name']"))
    )
    # LOCATE street, city, zip and phone now that the first field is interactable
    street_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Street']"))
    )
    city_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='City']"))
    )
    phone_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Phone']"))
    )

    # select usa from dropdown here as the zip field needs to generate after that field is selected
    country_dropdown_icon = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "i.q-icon.q-select__dropdown-icon"))
    )
    # finds and opens up the country drop down, finds USA and clicks on it
    country_dropdown = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Country']"))
    )
    country_dropdown.click()
    usa_option = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'q-menu')]//div[contains(@class, 'q-item__label')]//span[text()='USA']"))
    )
    usa_option.click()

    # Wait for the state dropdown element to be present after selecting USA
    # state_dropdown = WebDriverWait(driver, 20).until(
    #     ec.presence_of_element_located(
    #         (By.CSS_SELECTOR, "div.q-field.q-field--outlined.q-select.q-field--dense.q-field--float"))
    # )
    #
    # # Click on the state dropdown to open it
    # state_dropdown.click()
    #
    # # Wait for the state options to be visible and interactable
    # state_options = WebDriverWait(driver, 20).until(
    #     ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.q-item__label"))
    # )
    #
    # # Find the desired state option based on the value from the CSV file and click on it
    # desired_state = "CA"  # Replace with the actual state value from the CSV file
    # for option in state_options:
    #     if option.text == desired_state:
    #         option.click()
    #         break

    # Target the "API Status" dropdown and select "Beta"
    api_status_dropdown = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='API Status']"))
    )
    api_status_dropdown.click()
    beta_option = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable(
            (By.XPATH,
             "//div[contains(@class, 'q-menu')]//div[contains(@class, 'q-item__label')]//span[contains(text(), 'Beta')]"))
    )
    beta_option.click()

    # Wait for the calendar field to be interactable and click it, waits for the ok button to show on the calendar
    # and clicks that as well, no date adjustment needed here as it always selects the correct date
    calendar_field = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "i.q-icon.text-green.notranslate.material-icons.cursor-pointer"))
    )
    calendar_field.click()
    ok_button = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'block') and text()='OK']"))
    )
    ok_button.click()

    # used element to be clickable here as this one generates after USA selected in dropdown
    zip_field = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Zip']"))
    )

    # opens up the onboarding file, checks fields in the file against fields on the webform and fills them in
    with open('onboarding.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
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
