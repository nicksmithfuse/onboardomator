from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from functions import get_dealer_info, login, automator

# Get information needed from the CSV
(dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
 include_registration_fees, zip_code, street_address, city_name, phone_number) = get_dealer_info()

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