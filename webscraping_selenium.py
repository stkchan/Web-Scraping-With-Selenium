from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re
import time
from datetime import datetime

# Define driver path
driver_path = r"C:\MyProject\Python_test\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Function for scraping data
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

# Function for deleting row
def clean_sku_column(df):
    df_cleaned = df[df['sku'].str.contains('sku', case=False, na=False)]
    return df_cleaned

def clean_discount_price_column(df):
    pattern    = re.compile(r'sku|%|[a-zA-Z]|\(\d+\)', re.IGNORECASE)
    df_cleaned = df[~df['discount_price'].str.contains(pattern, na=False)]
    return df_cleaned


# Function to remove "SKU:" prefix
def remove_sku_prefix(df):
    df['sku'] = df['sku'].str.replace(r'^SKU:', '', case=False, regex=True)
    return df

# Function to keep only numbers in discount_price column
def clean_discount_price_numbers(df):
    # df['discount_price'] = df['discount_price'].str.replace(r'[^\d,]', '', regex=True).str.replace(',', '')
    df['discount_price'] = df['discount_price'].str.replace(r'[^\d,\.]', '', regex=True).str.replace(',', '')
    return df



# Function to extract numbers and percentage from full_price column
def clean_full_price_column(df):
    df['percent_discount'] = df['full_price'].str.extract(r'(\d+%)', expand=False)
    df['full_price']       = df['full_price'].str.extract(r'(\d+(?:,\d+)*)', expand=False).str.replace(',', '')
    return df


def clean_review_rating_column(df):
    df['total_review']  = df['review_rating'].str.extract(r'\((\d+)\)', expand=False)
    df['review_rating'] = df['review_rating'].str.extract(r'(\d+\.\d+|\d+)', expand=False)
    return df


#Change type column
def change_type_to_float(df):
    df["full_price"]     = df["full_price"].astype(float)
    df["discount_price"] = df["discount_price"].astype(float)
    return df


#Create total discount column
def create_total_discount(df):
    df['total_discount'] = df['full_price'] - df['discount_price']
    return df


def create_sorted_column(df):
     #Add the new columns
    df["scrape_date"]         = datetime.today().strftime('%Y-%m-%d')
    df["retailer"]            = "homepro"
    df["shipping_detail"]     = None
    df["shipping_detail_2"]   = None
    df["is_discount_product"] = df["percent_discount"].notna()


    # Reorder columns
    df = df[
        [
            "scrape_date", "retailer", "category", "sku", "brand", "model", 
            "full_price", "discount_price", "total_discount", "percent_discount", "is_discount_product",
            "review_rating", "total_review", "shipping_detail", "shipping_detail_2", "url"
        ]
    ]
    return df


# Clean the data using the cleaning functions
df_cleaned = clean_sku_column(df)
df_cleaned = clean_discount_price_column(df_cleaned)
df_cleaned = remove_sku_prefix(df_cleaned)
df_cleaned = clean_discount_price_numbers(df_cleaned)
df_cleaned = clean_full_price_column(df_cleaned)
df_cleaned = clean_review_rating_column(df_cleaned)
df_cleaned = change_type_to_float(df_cleaned)
df_cleaned = create_total_discount(df_cleaned)
df_cleaned = create_sorted_column(df_cleaned)

# Save the cleaned data to another CSV file
df_cleaned.to_csv("clean_data.csv", index=False, encoding="utf-8-sig")
print("Cleaned data saved to clean_data.csv")



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
