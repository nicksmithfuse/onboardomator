import os
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from functions import get_dealer_info, modify_account, create_account, login

# Locally stored username and password hashtag security hashtag we did it
mscan_username = os.getenv("mscanuser")
mscan_password = os.getenv("mscanpw")

# get information from the CSV
dealership_name, dealership_state_abbr, dealership_state_full = get_dealer_info()

# chrome driver > open up full screen to the login page
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
login_url = "https://portal.mscanapi.com/#/Partner/Login"
driver.get(login_url)

# login to mscan
login(driver, mscan_username, mscan_password)

# Display a pop-up window to ask the user if they want to modify an existing account or create a new account
user_choice = messagebox.askquestion("Account Action", "Do you want to create a new account?")

if user_choice == "yes":
    create_account(driver, dealership_state_abbr, dealership_state_full)
else:
    modify_account(driver, dealership_name)