import functions

# Step 1: User selects the onboarding CSV file from their computer
functions.select_onboarding_file()

# Step 2: user types in the inventory filename, and this gets stored in the csv
# TODO: implement a file upload  similar to the onboarding file so that everything is 100% accurate, but only
#  read the filename, don't open the file
inventory_filename = functions.get_inventory_filename()
functions.write_filename_to_csv(inventory_filename)

# Step 3: Initialize the Selenium driver in fullscreen mode
driver = functions.initialize_driver()

# Step 4: Login to mScan using os variables on the users machine
if functions.login(driver):
    # Step 5: Run the automator (create account)
    functions.automator(driver)

    # Step 6: Modify account settings
    (dealership_name, _, _, show_lower_max_rate,
     include_registration_fees, zip_code, _, _, _) = functions.get_dealer_info()
    if functions.modify_account(driver, dealership_name, show_lower_max_rate, include_registration_fees, zip_code):
        # Step 7: Login to FIA
        functions.fia_login(driver)
else:
    print("Failed to login to mScan.")
