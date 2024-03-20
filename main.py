from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from functions import get_dealer_info, login, automator, select_onboarding_file, access_google_sheet, get_inventory_filename

# Show the initial popup and get the Google Sheet URL
sheet_url = select_onboarding_file()

# Access the Google Sheet
sheet_driver = access_google_sheet(sheet_url)

# Get the inventory filename from the user
inventory_filename = get_inventory_filename()

# Write the inventory filename to the Google Sheet
# write_filename_to_sheet(sheet_driver, inventory_filename)

# Get information needed from the Google Sheet
(dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
 include_registration_fees, zip_code, street_address, city_name, phone_number) = get_dealer_info(sheet_driver)

# Chrome driver > open up full screen to the login page
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
login_url = "https://portal.mscanapi.com/#/Partner/Login"
driver.get(login_url)

# Login to mscan
login(driver)

# The automator
automator(driver)

# Quit the driver
driver.quit()