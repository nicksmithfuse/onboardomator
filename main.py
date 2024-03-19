from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from functions import get_dealer_info, login, automator

# get information needed from the CSV
(dealership_name, dealership_state_abbr, dealership_state_full, show_lower_max_rate,
 include_registration_fees, zip_code) = (get_dealer_info())

# chrome driver > open up full screen to the login page
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
login_url = "https://portal.mscanapi.com/#/Partner/Login"
driver.get(login_url)

# login to mscan
login(driver)

# the automator-or
automator(driver, dealership_state_abbr, dealership_state_full, dealership_name, show_lower_max_rate, include_registration_fees, zip_code)
