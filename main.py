import os
import csv
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from functions import get_dealer_info, login, automator

def select_onboarding_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    messagebox.showinfo("Automated Onboarding Process", "This is the automated onboarding process. Click OK to select the onboarding CSV file.")

    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

    if file_path:
        # Copy the selected file to the onboarding.csv file
        shutil.copy2(file_path, "onboarding.csv")
        messagebox.showinfo("File Selected", "Onboarding CSV file has been selected.")
    else:
        messagebox.showinfo("No File Selected", "No file was selected. The automated process will now exit.")
        exit()

def get_inventory_filename():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    filename = simpledialog.askstring("Inventory Filename", "Enter the inventory filename:", parent=root)

    if not filename:
        messagebox.showinfo("No Filename Entered", "No filename was entered. The automated process will now exit.")
        exit()

    return filename

def write_filename_to_csv(filename):
    with open("onboarding.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Filename", filename])

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

# Login to mscan
login(driver)

# The automator
automator(driver)

# Quit the driver
driver.quit()