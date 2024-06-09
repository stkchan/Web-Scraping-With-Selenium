# Web-Scraping-With-Selenium

## Table of Contents
* [Project Objective](#Project-Objective)
* [Setting up Selenium](#Setting-up-Selenium)
   - [Selenium Package](#Selenium-Package)
* [Scraping Process](#DScraping-Process)
   - [Import libraries](#Import-libraries)
   - [Define driver path](#Define-driver-path)
   - [Create function for scraping data](#Create-function-for-scraping-data)
   - [Create DataFrame and save to CSV file](#Create-DataFrame-and-save-to-CSV-file)
* [Upload Data to BigQuery](#Upload-data-to-BigQuery)
   - [Prerequisite](#Prerequisite)
   - [Example of script for uploading data to BigQuery](#Example-of-script-for-uploading-data-to-BigQuery)

  

## Project Objective
In this project, we aim to scrape data from the webpage [https://www.homepro.co.th/c/FUR](https://www.homepro.co.th/c/FUR), transform it into table format using [Pandas](https://pypi.org/project/pandas/), and store the data in [BigQuery](https://cloud.google.com/bigquery?hl=en).

## Setting up Selenium
Selenium is an open-source tool that automates web browsers. It provides a suite of tools and libraries that enable testing of web applications, automating repetitive web-based tasks, and scraping web content. Selenium supports multiple programming languages such as Java, C#, Python, and Ruby, allowing developers to write tests in their preferred language. 

### Selenium Package

```shell Tab A
pip install selenium
```
link to download the selenium drivers for Firefox, Chrome, and Edge [here](https://pypi.org/project/selenium/#drivers)

To see Selenium in action, type in these lines in your favorite code editor and run it as a Python script. You can also run these statements from the Python console.

```python
from selenium.webdriver import Chrome
driver = Chrome(executable_path='C:/WebDrivers/chromedriver.exe')
driver.get("https://www.homepro.co.th/")
```
This will launch Chrome and load the web page.  There will be notice below the address bar:

```shell
Chrome is being controlled by automated test software.
```

To close this browser, simply run this line:

```python
driver.quit()
```

## Scraping Process
### Import libraries
To begin with, I have imported the necessary libraries for this project.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re
import time
from datetime import datetim
```

### Define driver path
```python
driver_path = r"C:\MyProject\Python_test\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
```

### Create function for scraping data
```python
def scrape_prices(base_url, category, pages=5):
    data = {
        "category"            : [],
        "brand"               : [],
        "model"               : [],
        "sku"                 : [],
        "review_rating"       : [],
        "discount_price"      : [],
        "full_price"          : [],
        "url"                 : []
    }

    # Loop for scraping data in multiple pages
    for page in range(1, pages + 1):
        current_url = f"{base_url}&page={page}#plist"
        driver.get(current_url)
        time.sleep(10)

        # Find Element of Data
        product_list = driver.find_elements(By.CLASS_NAME, "product-plp-card")

        for p in product_list:
            listcheck = p.text.split("\n")
            print("DEBUG: listcheck =", listcheck)

            # Ensure the list has sufficient length before accessing elements
            if len(listcheck) < 3:
                continue

            # Get URL
            try:
                links  = p.find_element(By.CLASS_NAME, "plp-card-top")
                alltag = links.find_elements(By.TAG_NAME, "a")
                url    = alltag[-1].get_attribute("href")
            except NoSuchElementException:
                url    = None

            # Regular expression to match patterns
            pattern = re.compile(r'\(\d+\)')

            # Extract data based on the conditions
            brand = model = sku = review_rating = discount_price = full_price = free_option = seller_detail = None

            # Checking if the review_rating contains parentheses with numbers
            if any(pattern.search(line) for line in listcheck):
                review_rating = next((line for line in listcheck if pattern.search(line)), None)

            # Overall conditions to extract the rest of the data
            if review_rating and listcheck[-1] == "เปรียบเทียบ":
                brand           = listcheck[0]
                model           = listcheck[1]
                sku             = listcheck[2]
                discount_price  = listcheck[-5]
                full_price      = listcheck[-4]
                

            elif review_rating and listcheck[-1] == "จำหน่ายโดย: โฮมโปร":
                brand           = listcheck[0]
                model           = listcheck[1]
                sku             = listcheck[2]
                discount_price  = listcheck[-4]
                full_price      = listcheck[-3]
                

            elif listcheck[0] == "ใหม่ล่าสุด!":
                brand           = listcheck[1]
                model           = listcheck[2]
                sku             = listcheck[3]
                discount_price  = listcheck[-5]
                full_price      = listcheck[-4]
                

            elif listcheck[-3] == "ฟรีประกอบ":
                brand           = listcheck[0]
                model           = listcheck[1]
                sku             = listcheck[2]
                discount_price  = listcheck[-5]
                full_price      = listcheck[-4]
 

            else:
                brand           = listcheck[0]
                model           = listcheck[1]
                sku             = listcheck[2]
                discount_price  = listcheck[-4]
                full_price      = listcheck[-3]
               

            # Append data into list
            data["category"].append(category)
            data["brand"].append(brand)
            data["model"].append(model)
            data["sku"].append(sku)
            data["review_rating"].append(review_rating)
            data["discount_price"].append(discount_price)
            data["full_price"].append(full_price)
            data["url"].append(url)

            print("========================================================================================================")

    return pd.DataFrame(data)


def desk_price():
    base_url = "https://www.homepro.co.th/c/FUR1005?s=12&size=200&cst=0&pmin=&pmax=&q=โต๊ะทำงาน"
    return scrape_prices(base_url, "desk")

def chair_price():
    base_url = "https://www.homepro.co.th/c/FUR1004?s=12&size=200&cst=0&pmin=&pmax=&q=เก้าอี้สำนักงาน"
    return scrape_prices(base_url, "chair")

def sofa_price():
    base_url = "https://www.homepro.co.th/c/FUR0805?s=12&size=200&cst=0&pmin=&pmax=&q=โซฟา"
    return scrape_prices(base_url, "sofa")

def bed_price():
    base_url = "https://www.homepro.co.th/c/FUR0102?s=12&size=200&cst=0&pmin=&pmax=&q=เตียงนอน"
    return scrape_prices(base_url, "bed")

def bedroom_price():
    base_url = "https://www.homepro.co.th/c/FUR0101?s=12&size=200&cst=0&pmin=&pmax=&q=ชุดห้องนอน"
    return scrape_prices(base_url, "bed_set")
```


### Create DataFrame and save to CSV file
```python
# Combine data
def combine_furniture_prices():
    desk_df    = desk_price()
    chair_df   = chair_price()
    sofa_df    = sofa_price()
    bed_df     = bed_price()
    bedset_df  = bedroom_price()


    combined_df = pd.concat([desk_df, chair_df, sofa_df, bed_df, bedset_df], ignore_index=True)


    # Save to CSV File
    combined_df.to_csv("combined_furniture_prices_version2.csv", index=False, encoding="utf-8-sig")
    
    return combined_df


# Call the function
try:
    combined_df = combine_furniture_prices()
    print("Data saved to combined_furniture_prices_version2.csv")
finally:
    driver.quit()
```

## Upload Data to BigQuery

### Prerequisite
Before we export our data to BigQuery, we need to complete these steps (assuming we already have a Google Cloud account).
  - Create a Google credential to obtain an access token [here](https://developers.google.com/workspace/guides/create-credentials)
  - Create a table in BigQuery [here](https://cloud.google.com/bigquery/docs/tables)
  - Install Google Cloud BigQuery library
    ```python
       pip install google-cloud-bigquery
    ```

    
### Example of script for uploading data to BigQuery

```python
    from google.oauth2 import service_account
    from google.cloud import bigquery
    from pandas.io import gbq
    from pandas_gbq import to_gbq
    import googleapiclient.discovery
    from load_credentials import load_credentials 
    import os
    import pandas_gbq
    
    
    # Load credentials from credentials.txt file
    credentials = load_credentials('credential.txt')
    
    # Verify the loaded credentials
    print("GOOGLE_APPLICATION_CREDENTIALS:", credentials['GOOGLE_APPLICATION_CREDENTIALS'])
    print("BIGQUERY_TABLE_ID:", credentials['BIGQUERY_TABLE_ID'])
    
    # Get the environment variables from the loaded credentials
    credentials_file = credentials['GOOGLE_APPLICATION_CREDENTIALS']
    table_id = credentials['BIGQUERY_TABLE_ID']
    
    
    # Export to BigQuery
    def export_to_bigquery(df, table_id, credentials_file):
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        to_gbq(df, table_id, project_id=credentials.project_id, credentials=credentials)
        print("Export data to BigQuery successfully.")
    
    
    export_to_bigquery(df_cleaned, table_id, credentials_file)
```

**Note:** You can find the table_id, project_id, and credentials in your JSON file after creating credentials in Google Cloud Platform. The table_id is located in BigQuery, which you created.
