import csv
import time
import os
import shutil
import tkinter as tk

from tkinter import messagebox, filedialog, simpledialog

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def select_onboarding_file():
    while True:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Automated Onboarding Process", "Welcome to the onboarding process. "
                                                            "Click OK to select the onboarding CSV file.")

        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        if file_path:
            # sets the required fields, checks the field values and asks the user to verify file and try again if
            # the required info is not found to work through the process
            required_fields = ["Dealer Name", "Street Address", "City", "State", "Zip Code", "Contact Phone Number (Contact 1)"]
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                data = {row[0]: row[1] for row in reader}

                missing_fields = [field for field in required_fields if field not in data or not data[field].strip()]

                if missing_fields:
                    message = "The selected file is missing the following required fields or values:\n\n"
                    message += "\n".join(missing_fields)
                    messagebox.showinfo("Invalid File", message + "\n\nPlease check the file and try again.")
                    continue

            # utilizing whatever shutil is so that we copy the file from the users computer, previous version just
            # moved it so the user could not actually open the file anymore to look at it
            shutil.copy2(file_path, "onboarding.csv")
            messagebox.showinfo("File Selected", "Onboarding CSV file has been selected.")
            break
        else:
            messagebox.showinfo("No File Selected", "No file was selected. The automated process will now exit.")
            exit()


def get_inventory_filename():
    # pop up that asks the user for the filename.
    # TODO: make this a csv uploader and just strip the filename so that the user is forced to provide a real filename
    root = tk.Tk()
    root.withdraw()
    filename = simpledialog.askstring("Inventory Filename", "Enter the inventory filename:", parent=root)

    if not filename:
        messagebox.showinfo("No Filename Entered", "No filename was entered. The automated process will now exit.")
        exit()

    return filename


# I don't think this is actually working or necessary. filename can just be saved as a variable to be used during FIA
def write_filename_to_csv(filename):
    with open("onboarding.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Filename", filename])


def get_dealer_info():
    # establishes variables for data from the file, assigns from onboarding.csv and returned for other functions
    # TODO: add anything here that is needed for FIA or DP so that there isn't just csv readers everywhere
    dealership_name = ""
    dealership_state_abbr = ""
    dealership_state_full = ""
    show_lower_max_rate = False
    include_registration_fees = False
    zip_code = ""
    street_address = ""
    city_name = ""
    phone_number = ""
    # this is necessary for the dealership abbreviation to state fullname conversion later in the code to work
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
    # reads file and assigns the values to variables
    with open('onboarding.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0].strip() == "Dealer Name":
                dealership_name = row[1].strip()
            elif row[0].strip() == "State":
                dealership_state_abbr = row[1].strip()
                dealership_state_full = state_map.get(dealership_state_abbr, '')
            elif row[0].strip() == "Show Programs with Lower Max Rate":
                show_lower_max_rate = row[1].strip().lower() == "yes"
            elif row[0].strip() == "Include Registration Fees in Payment":
                include_registration_fees = row[1].strip().lower() == "yes"
            elif row[0].strip() == "Zip Code":
                zip_code = row[1].strip()
            elif row[0].strip() == "Street Address":
                street_address = row[1].strip()
            elif row[0].strip() == "City":
                city_name = row[1].strip()
            elif row[0].strip() == "Contact Phone Number (Contact 1)":
                phone_number = row[1].strip()

    return (dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
            include_registration_fees, zip_code, street_address, city_name, phone_number)


def initialize_driver():
    # Chrome driver > open up full screen to the login page
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    login_url = "https://portal.mscanapi.com/#/Partner/Login"
    driver.get(login_url)

    # Wait for the page to finish loading
    wait = WebDriverWait(driver, 10)
    page_loaded = wait.until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[name='Partner ID']"))
    )

    return driver


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


# this is probably redundant, but it was my first idea on how to run through the process.
def automator(driver):
    # get the dealership information from the CSV file
    (dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
     include_registration_fees, zip_code, street_address, city_name, phone_number) = get_dealer_info()

    # creates an account
    create_account(driver, dealership_state_abbr, dealership_state_full, dealership_name,
                   zip_code, street_address, city_name, phone_number)


def create_account(driver, dealership_state_abbr, dealership_state_full, dealership_name,
                   zip_code, street_address, city_name, phone_number):
    # wait for the "Create an Account" button to be clickable, and then click it
    create_account_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.q-btn--outline.text-primary"))
    )
    create_account_button.click()

    # waits for loading screen to go away - SORRY YUVAL :(
    WebDriverWait(driver, 10).until_not(
        ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
    )

    # there doesnt seem to be any rhyme or reason on what works with locateable and what works with clickable
    # below code works through the input form on the page, filling in information from the CSV and searching in
    # dropdowns to make the connections on what to click.
    # DO NOT MAKE ANY ADJUSTMENTS BELOW THIS POINT OR CREATE ACCOUNT WILL EXPLODE
    dealership_name_field = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Dealership Name']"))
    )
    dealership_name_field.send_keys(dealership_name)

    street_field = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Street']"))
    )
    street_field.send_keys(street_address)

    city_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='City']"))
    )
    city_field.send_keys(city_name)

    phone_field = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Phone']"))
    )
    phone_field.send_keys(phone_number)

    # select usa from dropdown here as the zip field needs to GENERATE on screen after that country is selected
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
    # through the list to 'find' the state (if it is not immediately visible on the page) but i don't have any
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
                        "Please fill out the Subscribed Makes field and review all information before clicking"
                        " 'Save' Click ok to return to the homepage.")

    # send the user back to the homepage
    homepage_url = "https://portal.mscanapi.com/#"
    driver.get(homepage_url)
    print("Navigated to the homepage")


def modify_account(driver, dealership_name, show_lower_max_rate, include_registration_fees, zip_code):
    # this is the part of the script where we adjust the settings through user prompts.
    try:

        # Wait for any loading screen to disappear
        WebDriverWait(driver, 10).until_not(
            ec.presence_of_element_located((By.CSS_SELECTOR, "div.q-loading__backdrop"))
        )

        # find the search input box and wait for it to be interactable, enter the dealership name variable and simulate
        # the enter key being pressed. then, because reasons, wait 2 seconds otherwise it breaks.
        search_input = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search in the data grid']"))
        )

        # TODO: figure out a better solution than time.sleep()
        # there's not a loading screen here to check against
        # several errors at this point in the script, time.sleep(2) is working for now
        search_input.send_keys(dealership_name)
        time.sleep(2)
        search_input.send_keys(Keys.ENTER)
        time.sleep(2)

        # code breaks here without time.sleep() idk what im doing

        # entering the dealership name changes data table to only show dealership, targets this as <tr>, and clicks
        # on it.
        target_row_xpath = f"//tr[@class='dx-row dx-data-row dx-column-lines']"
        target_row = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.XPATH, target_row_xpath))
        )
        time.sleep(1)
        target_row.click()

        # pop-up prompt to begin settings modification
        messagebox.showinfo("Begin mScanomator",
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

        # goes to the market specific settings page
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

        # TODO: make the if statement here make sense.
        # previous version allowed the user to loop back through to create more than one account, but that's stupid.
        user_choice = messagebox.showinfo("Continue", "Continue to FIA")

        if user_choice == 'yes':
            fia_login(driver)
        else:
            fia_login(driver)

        return True  # Return True if the modification process is successful

    except Exception as e:
        print(f"An error occurred during account modification: {str(e)}")
        return False  # Return False if an exception occurs during account modification


def fia_login(driver):
    # takes the user to the FIA login page - this will be adjusted to the staging URL until next release
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

    # Wait for the login button to be clickable and click
    login_button = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary")))
    login_button.click()

    # keeps browser open
    input()
    # unreachable but it's here just in case chrome driver becomes self aware
    driver.quit()
