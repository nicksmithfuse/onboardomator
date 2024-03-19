import csv
import time
import os
from tkinter import messagebox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def get_dealer_info():
    # Read the "Dealer Name" value from the "onboarding.csv" file
    dealership_name = ""
    with open('onboarding.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0].strip() == "Dealer Name":
                dealership_name = row[1].strip()
                break

    state_map = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }

    # Read the "State" value from the "onboarding.csv" file
    dealership_state_abbr = ""
    with open('onboarding.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0].strip() == "State":
                dealership_state_abbr = row[1].strip()
                break

    # Get the full state name based on the abbreviation
    dealership_state_full = state_map.get(dealership_state_abbr, '')

    # Read the settings values from the "onboarding.csv" file
    show_lower_max_rate = ""
    include_registration_fees = ""
    zip_code = ""
    with open('onboarding.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0].strip() == "Show Programs with Lower Max Rate":
                show_lower_max_rate = row[1].strip().lower() == "yes"
                break
            if row[0].strip() == "Include Registration Fees in Payment":
                include_registration_fees = row[1].strip().lower() == "yes"
                break
            if row[0].strip() == "Zip Code":
                zip_code = row[1].strip()
                break

    return (dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
            include_registration_fees, zip_code)


def login(driver):
    # Locally stored username and password hashtag security hashtag we did it
    mscan_username = os.getenv("mscanuser")
    mscan_password = os.getenv("mscanpw")
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

        return True  # Return True if login is successful

    except Exception as e:
        print(f"An error occurred during login: {str(e)}")
        return False  # Return False if an exception occurs during login


def modify_account(driver, dealership_name, show_lower_max_rate, include_registration_fees, zip_code):
    try:
        # Find the search input box and wait for it to be interactable
        search_input = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search in the data grid']"))
        )

        # Enter the dealership name in the search input box and simulate the Enter key
        search_input.send_keys(dealership_name)
        search_input.send_keys(Keys.ENTER)

        # Wait for 2 seconds
        time.sleep(2)

        # Find the dealership name and click on it
        target_row_xpath = f"//tr[@class='dx-row dx-data-row dx-column-lines']"
        target_row = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, target_row_xpath))
        )
        time.sleep(1)
        target_row.click()

        # Display a pop-up prompt to begin settings modification
        messagebox.showinfo("Begin mScanomator Settings",
                            f"You are about to modify the settings for {dealership_name}. Click OK to proceed to "
                            f"calculation settings after this page has been adjusted and saved.")

        # Navigate to the "Calculation Settings" page
        calculation_settings_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'q-item__section') and contains(text(), 'Calculation Settings')]"))
        )
        calculation_settings_element.click()

        # Wait for the "Calculation Settings" page to load completely
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Calculation Settings')]"))
        )

        # Display a pop-up with the value of "Include Registration Fees in Payment" and instructions
        if include_registration_fees:
            messagebox.showinfo("Calculation Settings",
                                "'Include Registration Fees in Payment' = 'Yes'.\n"
                                "Turn on Calculate Reg > click Save > hit OK to proceed to Market Specific Settings.")
        else:
            messagebox.showinfo("Calculation Settings",
                                "'Include Registration Fees in Payment' = 'No'.\n"
                                "Ensure Calculate Reg is disabled > click Save > hit OK to proceed to Market Specific Settings.")

        # Navigate to the "Market Specific Settings" page
        market_specific_settings_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH,
                 "//div[contains(@class, 'q-item__section') and contains(text(), 'Market Specific Settings')]"))
        )
        market_specific_settings_element.click()

        # Find the "Search by Zip" input field and wait for it to be clickable, enter zip code into field
        search_by_zip_input = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Search by Zip']"))
        )
        search_by_zip_input.send_keys(zip_code)

        # hit enter
        search_by_zip_input.send_keys(Keys.ENTER)

        # Wait for the "Override" button to be interactable and click it
        override_button = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.ID, "btnPreview"))
        )
        override_button.click()
        print("Clicked the Override button")

        input()
        return True  # Return True if the modification process is successful

    except Exception as e:
        print(f"An error occurred during account modification: {str(e)}")
        return False  # Return False if an exception occurs during account modification




def create_account(driver, dealership_state_abbr, dealership_state_full):
    # Wait for the "Create an Account" button to be clickable, and then click it
    create_account_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.q-btn--outline.text-primary"))
    )
    create_account_button.click()

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

    # Wait for the state dropdown element to be present after selecting USA
    state_dropdown = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, "input[aria-label='State']"))
    )

    # Click on the state dropdown to open it
    state_dropdown.click()

    # Wait for the state options to be visible and interactable
    state_options = WebDriverWait(driver, 20).until(
        ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.q-item__label span"))
    )

    # Find the desired state option based on the value from the CSV file and click on it
    for option in state_options:
        if option.text == dealership_state_abbr:
            option.click()
            break

    # Find the checkbox next to the state subscription item matching the dealership's full state name
    state_subscription_checkbox = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((
            By.XPATH,
            f"//div[@class='dx-item dx-list-item']"
            f"[contains(.//div[@class='dx-item-content dx-list-item-content'], '{dealership_state_full}')]"
            f"//div[@class='dx-checkbox-container']"
        ))
    )

    # Click on the checkbox to select the state subscription
    state_subscription_checkbox.click()

    # Display a pop-up message to the user
    messagebox.showinfo("Account Creation",
                        "Please fill out the OEM field and review all information before clicking 'Save'.")

    # Keep the browser open for further adjustments
    input("Press Enter to close the browser...")


def automator(driver, dealership_state_abbr, dealership_state_full, dealership_name, show_lower_max_rate,
              include_registration_fees, zip_code):
    user_choice = messagebox.askquestion(f"Account Action", f"Are you creating a NEW account for {dealership_name}?")
    if user_choice == "yes":
        print("User selected: Create an Account")
        create_account(driver, dealership_state_abbr, dealership_state_full)
    else:
        # User selected "No" (Modify Settings)
        modify_settings = messagebox.askyesno("Modify Settings", f"Do you want to modify the account "
                                                                 f"settings for {dealership_name}?")

        if modify_settings:
            print("User selected: Modify Settings")
            modify_account(driver, dealership_name, show_lower_max_rate, include_registration_fees, zip_code)

        else:
            # User cancelled modifying the account settings
            print("User cancelled modifying the account settings")
            input()
