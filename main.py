from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from functions import get_dealer_info, login, automator, select_onboarding_file, get_inventory_filename, write_filename_to_csv

# Show the initial popup and select the onboarding CSV file
select_onboarding_file()

# Get the inventory filename from the user
inventory_filename = get_inventory_filename()

# Write the inventory filename to the onboarding CSV file
write_filename_to_csv(inventory_filename)

# Get information needed from the CSV
(dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
 include_registration_fees, zip_code, street_address, city_name, phone_number) = get_dealer_info()

# Chrome driver > open up full screen to the login page
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
login_url = "https://portal.mscanapi.com/#/Partner/Login"
driver.get(login_url)

# Login to mscan using stored variables on the users machine. the script will break here if these do not exist.
login(driver)

# The automator works through the mscan account creation. using a series of pop ups, the automator informs the user
# what options to select, and auto-fills anything where it can.
# TODO: review code with people who do this for a living to see where auto-fill can be improved
# Next - the automator opens up FIA and logs in. This is where the code stops for now until the next update in FIA that
# changes the UI.
automator(driver)

# Quit the driver
driver.quit()