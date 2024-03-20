import csv
import time
import os
import tkinter as tk

from tkinter import messagebox, filedialog, simpledialog
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver


def select_onboarding_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    sheet_url = simpledialog.askstring("Google Sheet URL", "Enter the Google Sheet URL:", parent=root)

    if not sheet_url:
        messagebox.showinfo("No URL Entered", "No Google Sheet URL was entered. The automated process will now exit.")
        exit()

    return sheet_url

def get_inventory_filename():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    filename = simpledialog.askstring("Inventory Filename", "Enter the inventory filename:", parent=root)

    if not filename:
        messagebox.showinfo("No Filename Entered", "No filename was entered. The automated process will now exit.")
        exit()

    return filename

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def access_google_sheet(sheet_url):
    # Create a new Chrome driver instance for the Google Sheet
    sheet_driver = webdriver.Chrome()

    # Navigate to the Google login page
    sheet_driver.get("https://accounts.google.com/signin")

    # Enter the email and click the "Next" button
    email_field = sheet_driver.find_element(By.XPATH, "//input[@type='email']")
    email_field.send_keys(os.environ.get("GMAIL"))
    sheet_driver.find_element(By.XPATH, "//span[text()='Next']").click()
    time.sleep(10)
    # Wait for the password field to be visible and enter the password
    password_field = WebDriverWait(sheet_driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
    )
    password_field.send_keys(os.environ.get("GMAIL_PASSWORD"))
    sheet_driver.find_element(By.XPATH, "//span[text()='Next']").click()

    # Navigate to the Google Sheet URL
    sheet_driver.get(sheet_url)

    return sheet_driver

def get_dealer_info(sheet_driver):
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

    dealership_name = sheet_driver.find_element_by_xpath("//span[text()='Dealer Name']/following-sibling::span").text
    dealership_state_abbr = sheet_driver.find_element_by_xpath("//span[text()='State']/following-sibling::span").text
    dealership_state_full = state_map.get(dealership_state_abbr, '')
    show_lower_max_rate = sheet_driver.find_element_by_xpath(
        "//span[text()='Show Programs with Lower Max Rate']/following-sibling::span").text.lower() == "yes"
    include_registration_fees = sheet_driver.find_element_by_xpath(
        "//span[text()='Include Registration Fees in Payment']/following-sibling::span").text.lower() == "yes"
    zip_code = sheet_driver.find_element_by_xpath("//span[text()='Zip Code']/following-sibling::span").text
    street_address = sheet_driver.find_element_by_xpath("//span[text()='Street Address']/following-sibling::span").text
    city_name = sheet_driver.find_element_by_xpath("//span[text()='City']/following-sibling::span").text
    phone_number = sheet_driver.find_element_by_xpath(
        "//span[text()='Contact Phone Number (Contact 1)']/following-sibling::span").text

    return (dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
            include_registration_fees, zip_code, street_address, city_name, phone_number)

def login(driver):
    # logs into mscan
    # locally stored username and password hashtag security hashtag we did it
    mscan_username = os.getenv("mscanuser")
    mscan_password = os.getenv("mscanpw")
    try:
        # wait for the partner ID input field to be CLICKABLE, and then enter the username variable
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

        # this waits for the loading screen to go away, issues kept happening here and this worked
        WebDriverWait(driver, 10).until_not(
            ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
        )

        return True  # Return True if login is successful

    except Exception as e:
        print(f"An error occurred during login: {str(e)}")
        return False  # Return False if an exception occurs during login


def automator(driver):
    # Get the dealership information from the CSV file
    (dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
     include_registration_fees, zip_code, street_address, city_name, phone_number) = get_dealer_info()

    user_choice = messagebox.askquestion(f"Account Action", f"Are you creating a NEW account for {dealership_name}?")
    if user_choice == "yes":
        print("User selected: Create an Account")
        create_account(driver, dealership_state_abbr, dealership_state_full, dealership_name, show_lower_max_rate,
                       include_registration_fees, zip_code, street_address, city_name, phone_number)
    else:
        modify_settings = messagebox.askyesno("Modify Settings", f"Do you want to modify the account "
                                                                 f"settings for {dealership_name}?")
        if modify_settings:
            print("User selected: Modify Settings")
            modify_account(driver, dealership_name, show_lower_max_rate, include_registration_fees, zip_code)
            input()
        else:
            print("User cancelled modifying the account settings")
            input()

def create_account(driver, dealership_state_abbr, dealership_state_full, dealership_name, show_lower_max_rate,
                   include_registration_fees, zip_code, street_address, city_name, phone_number):
    # wait for the "Create an Account" button to be clickable, and then click it
    create_account_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.q-btn--outline.text-primary"))
    )
    create_account_button.click()

    # waits for loading screen to go away - script kept breaking and this works
    WebDriverWait(driver, 10).until_not(
        ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
    )

    # "Dealership Name" input field to be interactable
    dealership_name_field = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Dealership Name']"))
    )
    # changed every field to interactable since random breaks
    street_field = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Street']"))
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

    # find the "API Status" dropdown and select "Beta"
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
                dealership_name_field.send_keys(dealership_name)

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

    # wait for the state dropdown element to be present after selecting USA, click and open it
    state_dropdown = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, "input[aria-label='State']"))
    )
    state_dropdown.click()

    # wait for the state dropdown options to be locatable
    state_options = WebDriverWait(driver, 20).until(
        ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.q-item__label span"))
    )

    # find the desired state option based on the value pulled from the CSV file and click on it
    for option in state_options:
        if option.text == dealership_state_abbr:
            option.click()
            break

    # down below, finds the full state name based on the state abbreviation. currently the user needs to scroll
    # through the list to 'find' the state (if it is not immediately visibile on the page) but i don't have any
    # more ideas here
    state_subscription_checkbox = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((
            By.XPATH,
            f"//div[@class='dx-item dx-list-item']"
            f"[contains(.//div[@class='dx-item-content dx-list-item-content'], '{dealership_state_full}')]"
            f"//div[@class='dx-checkbox-container']"
        ))
    )
    state_subscription_checkbox.click()

    # you did it pop up
    messagebox.showinfo("Account Creation",
                        "Please fill out the OEM field and review all information before clicking 'Save' Click ok to "
                        "return to the homepage.")

    # send the user back to the homepage
    homepage_url = "https://portal.mscanapi.com/#"
    driver.get(homepage_url)
    print("Navigated to the homepage")

    # Call the automator function to repeat the process
    automator(driver)

def modify_account(driver, dealership_name, show_lower_max_rate, include_registration_fees, zip_code):
    # this is the part of the script where we adjust the settings through user propmpts.
    try:
        # find the search input box and wait for it to be interactable, enter the dealership name variable and simulate
        # the enter key being pressed. then, because reasons, wait 2 seconds otherwise it breaks.
        search_input = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search in the data grid']"))
        )
        search_input.send_keys(dealership_name)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)

        # entering the dealership name changes data table to only show dealership, targets this as <tr>, and clicks
        # on it.
        target_row_xpath = f"//tr[@class='dx-row dx-data-row dx-column-lines']"
        target_row = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, target_row_xpath))
        )
        time.sleep(1)
        target_row.click()

        # pop-up prompt to begin settings modification
        messagebox.showinfo("Begin mScanomator Settings",
                            f"You are about to modify the settings for {dealership_name}. Click OK to proceed to "
                            f"rate markup settings.")

        # navigate to rate markup settings page
        rate_markup_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'q-item__section') and contains(text(), 'Rate Markup')]"))
        )
        rate_markup_element.click()

        # pop-up with the value of "Lower Max Rate" and instructions on completing page
        if show_lower_max_rate:
            messagebox.showinfo("Rate Markup Settings",
                                "'Lower Max Rate' = 'Yes'.\n"
                                "Check the boxes and click Save > hit OK to proceed to Calculation Settings.")
        else:
            messagebox.showinfo("Rate Markup Settings",
                                "'Lower Max Rate' = 'No'.\n"
                                "Ensure boxes aren't checked and click Save > hit OK to proceed to Calculation Settings.")

        # navigate to calculation settings page
        calculation_settings_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'q-item__section') and contains(text(), 'Calculation Settings')]"))
        )
        calculation_settings_element.click()

        # pop-up with the value of "Include Registration Fees in Payment" and instructions on completing page
        if include_registration_fees:
            messagebox.showinfo("Calculation Settings",
                                "'Include Registration Fees in Payment' = 'Yes'.\n"
                                "Turn on Calculate Reg > click Save > hit OK to proceed to Market Specific Settings.")
        else:
            messagebox.showinfo("Calculation Settings",
                                "'Include Registration Fees in Payment' = 'No'.\n"
                                "Ensure Calculate Reg is disabled > click Save > hit OK to proceed to Market Specific Settings.")

        # goes to the market specific settings
        market_specific_settings_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH,
                 "//div[contains(@class, 'q-item__section') and contains(text(), 'Market Specific Settings')]"))
        )
        market_specific_settings_element.click()

        # find the "Search by Zip" input field on the page and wait for it to be clickable, enter zip code into field,
        # hit enter
        search_by_zip_input = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Search by Zip']"))
        )
        search_by_zip_input.send_keys(zip_code)
        search_by_zip_input.send_keys(Keys.ENTER)

        # Wait for any loading screen to disappear
        WebDriverWait(driver, 10).until_not(
            ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
        )

        # Display a pop-up with the value of "Calculate Registration Fee" and instructions
        if include_registration_fees:
            messagebox.showinfo("Calculate Registration Fee",
                                "'Calculate Registration Fee' = 'Yes'.\n"
                                "Turn on the Calculate Registration Fee setting and click Save Settings.")
        else:
            messagebox.showinfo("Calculate Registration Fee",
                                "'Calculate Registration Fee' = 'No'.\n"
                                "Disable the Calculate Registration Fee setting and click Save Settings.")

        # Ask the user if they want to create another account or continue to FIA
        user_choice = messagebox.askquestion("Next Step", "Are you ready to continue to FIA?")

        if user_choice == 'yes':
            fia_login(driver)
        else:
            homepage_url = "https://portal.mscanapi.com/#"
            driver.get(homepage_url)
            print("Navigated to the homepage for creating another account")

        return True  # Return True if the modification process is successful

    except Exception as e:
        print(f"An error occurred during account modification: {str(e)}")
        return False  # Return False if an exception occurs during account modification

def fia_login(driver):
    # Navigate to the login page
    login_url = "https://finance-intelligence-admin.fuseautotech.com/Identity/Account/Login"
    driver.get(login_url)

    # Get the email and password environment variables
    fia_email = os.environ.get("fia_email")
    fia_password = os.environ.get("fia_password")

    # Wait for the email and password fields to be interactable
    wait = WebDriverWait(driver, 10)
    email_field = wait.until(ec.element_to_be_clickable((By.ID, "Input_Email")))
    password_field = wait.until(ec.element_to_be_clickable((By.ID, "Input_Password")))

    # Enter the email and password
    email_field.send_keys(fia_email)
    password_field.send_keys(fia_password)

    # Wait for the login button to be clickable
    login_button = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary")))

    # Click the login button
    login_button.click()

    input("Press Enter to continue...")
    # Close the browser
    driver.quit()