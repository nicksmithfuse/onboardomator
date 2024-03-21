import functions

# this became hard to read, code moved to functions.py

# Step 1: uploads the CSV file to be used for this account creation process. checks the file for the correct info
# and rejects files that are missing any information, asking the user to upload a new file.
functions.select_onboarding_file()

# Step 2: user types in the inventory filename, and this gets stored in the csv
# TODO: implement a file upload  similar to the onboarding file so that everything is 100% accurate, but only
#  read the filename, don't open the file
inventory_filename = functions.get_inventory_filename()
functions.write_filename_to_csv(inventory_filename)

# Step 3: opens up chrome
driver = functions.initialize_driver()

# Step 4: logs into mscan using os variables on the users machine
if functions.login(driver):
    # Step 5: initialize automator-or - utilizes the get_dealer_info() to pull all of the info out of the uploaded .csv
    # and then runs through the create_account()
    functions.automator(driver)

    # Step 6: loops user back to mscan homepage after account creation, searches for that account, and then prompts
    # the user with pop ups to adjust the settings. pop ups provide the value from the file and instructions on what
    # to do on the page before continuing.
    # TODO: get real devs to automate whatever else can be automated, keeping in mind that MSCAN could change their UI
    #  causing this all to explode in the future
    (dealership_name, _, _, show_lower_max_rate,
     include_registration_fees, zip_code, _, _, _) = functions.get_dealer_info()
    if functions.modify_account(driver, dealership_name, show_lower_max_rate, include_registration_fees, zip_code):
        # Step 7: Login to FIA if the modify account has successfully navigated through everything
        functions.fia_login(driver)
else:
    print("Failed to login to mScan.")
