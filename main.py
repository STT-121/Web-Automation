import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import logging

# Set up logging
logging.basicConfig(filename='automation_log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def download_csv():
    try:
        logging.info("Starting CSV download process.")
        
        # Set up Selenium with Chrome headless mode for server environment
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        prefs = {"download.default_directory" : "/workspaces/Web-Automation/"}
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=options)
        driver.get("https://secure.cityofirvine.org/webreport/")
        
        time.sleep(5)
        logging.info("Webpage loaded. Searching for 'Export to Excel' button.")

        # Locate and click the export button
        export_button = driver.find_element(By.ID, "webReportGrid_ctl00_ctl02_ctl00_LinkButton3")
        export_button.click()
        logging.info("'Export to Excel' button clicked.")

        # Wait for the download to complete (adjust this time if necessary)
        time.sleep(40)
        logging.info("Download completed.")

        driver.quit()
        logging.info("Browser closed after successful CSV download.")

    except Exception as e:
        logging.error(f"An error occurred during CSV download: {str(e)}")
        raise

def append_to_google_sheets(csv_path):
    try:
        logging.info(f"Attempting to append data from CSV file at: {csv_path}")
        
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_path)
        logging.info(f"CSV loaded successfully. Number of rows: {len(df)}")

        #Sort them in ascending order by account number
        df.sort_values(by='ACCOUNT NUMBER', ascending=True, inplace=True)


        # Handle NaN values to avoid JSON errors
        df.fillna('', inplace=True)  # Replace NaNs with empty strings
        logging.info("NaN values handled successfully (replaced with empty strings).")


        # Set up the credentials for accessing Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)

        # Open the Google Spreadsheet by name or key
        spreadsheet = client.open("Full List of Businesses Licensed By The City of Irvine")
        worksheet = spreadsheet.sheet1  # or spreadsheet.worksheet("Sheet1")

        # Convert DataFrame to list of lists and append rows in batches
        rows = df.values.tolist()
        batch_size = 1000  # Adjust batch size as needed

        # Append data in batches to avoid quota limits
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            worksheet.append_rows(batch)
            logging.info(f"Appended batch {i//batch_size + 1}: {len(batch)} rows")
        
        logging.info(f"Successfully appended {len(rows)} rows to Google Sheets.")

    except Exception as e:
        logging.error(f"An error occurred while appending to Google Sheets: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        logging.info("Script started.")
        
        # Start the CSV download process
        # download_csv()
        
        # Define the path to the downloaded CSV file
        csv_file_path = "/workspaces/Web-Automation/Report.csv"
        
        # Check if the file exists before proceeding to append
        if os.path.exists(csv_file_path):
            logging.info("CSV file found. Proceeding to append to Google Sheets.")
            append_to_google_sheets(csv_file_path)
        else:
            logging.error(f"CSV file not found at path: {csv_file_path}")
            print("File not found!")

    except Exception as e:
        logging.critical(f"Critical error in main script: {str(e)}")
        raise
