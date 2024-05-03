# Import the neccessary packages
from xq import XQ
from snowflake.snowpark import Session
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor

import base64
import pandas as pd
import os
import random

# This SQL assumes 'ID' is a unique identifier for rows in your table. Adjust accordingly.
update_sql = """
MERGE INTO XQ_SnowFlake_Demo AS original
USING XQ_SnowFlake_Demo_Staging AS staging
ON original.ID = staging.ID
WHEN MATCHED THEN
    UPDATE SET 
    original.FirstName = staging.FirstName,
    original.LastName = staging.LastName,
    original.Address = staging.Address,
    original.PhoneNumber = staging.PhoneNumber;
"""

load_dotenv()

xq = XQ(
    api_key = os.getenv("XQ_API_KEY"),
    dashboard_api_key=os.getenv("XQ_DASHBOARD_API_KEY")
)

def snowpark_session_create():
    connection_params = {
        "account": os.getenv('ACCOUNT_ID'),
        "user": os.getenv('USERNAME'),
        "password": os.getenv('PASSWORD'),
        "role": os.getenv('ROLE'),
        "warehouse": os.getenv('WAREHOUSE'),
        "database": os.getenv('DATABASE'),
        "schema": os.getenv('SCHEMA')
    }
    session = Session.builder.configs(connection_params).create()
    return session

# Encrypt a field using the OTP algorithm
def encrypt_field_otp(field_data, key_packet, locator_token):
    try:
        encrypted_text = xq.encrypt_message(field_data.encode(), key_packet, algorithm="OTP")
        return locator_token + base64.b64encode(encrypted_text).decode()
    except Exception as e:
        print(f"Error encrypting field: {e}")
        return None

# Go through each field in the row and encrypt it
def encrypt_row(row, key_packet, xq):
    # This is an email address that will cover anyone part of my XQ team and will be utilized as the "recipients"
    email = "team@group.local"
    original_key = key_packet
    random.shuffle(original_key)
    shuffled_key = bytes(original_key)
    locator_token = xq.api.create_and_store_packet(recipients=[email],expires_hours = 144, key=shuffled_key, type=3, subject=f"SnowFlakeDemo {row.ID}")
    for col in row.index:
        if col == 'ID':
            continue
        if isinstance(row[col], str):  # Check if the value is a string to encrypt
            row[col] = encrypt_field_otp(field_data=row[col], key_packet=shuffled_key, locator_token=locator_token)
    return row

def encrypt_row_wrapper(args):
    """
    Wrapper function to unpack arguments and call `encrypt_row`.
    """
    row, key_packet, xq = args  # Unpack arguments
    return encrypt_row(pd.Series(row), key_packet, xq)

def parallel_encrypt_df(df, key_packet, xq):
    """
    Encrypts each row of the DataFrame in parallel using ProcessPoolExecutor.

    Args:
    - df: Pandas DataFrame to encrypt.
    - key_packet: The encryption key packet.
    - xq: An instance of your xq object for encryption.

    Returns:
    - A new encrypted DataFrame.
    """
    data_with_args = [(row, key_packet, xq) for index, row in df.iterrows()]
    
    with ProcessPoolExecutor() as executor:
        # Map the encrypt_row_wrapper over your data
        results = list(executor.map(encrypt_row_wrapper, data_with_args))
        
    return pd.DataFrame(results)
    

if __name__ == "__main__":
    # Create a Snowpark session
    session = snowpark_session_create()

    # Authenticate to XQ
    email = input(f"Please provide your email:")
    first_name = input(f"Please provide your first name:")
    last_name = input(f"Please provide your last name:")

    # Authorize the user - this will send a PIN to the email address
    xq.api.authorize_user(email, first_name, last_name)  # returns success boolean
    
    # 2FA
    pin = input(f"Please provide the PIN sent to the email address '{email}':")
    xq.api.code_validate(pin)

    # Exchange for Access Token - you can also include the teamID as a user parameter here if you have multiple teams
    temp = xq.api.exchange_key()

    # Select all values from the table and convert them to a Pandas DataFrame
    df = session.sql('SELECT * from XQ_SnowFlake_Demo')
    pdf = df.toPandas()

    # Generate a key utilizing a quantum entropy pool
    MYSUPERSECRETKEY = bytearray(xq.generate_key_from_entropy())

    # # Encrypt each field in the DataFrame
    encrypted_pdf = parallel_encrypt_df(pdf, MYSUPERSECRETKEY, xq)
    encrypted_pdf.reset_index(drop=True, inplace=True)

    # # Create a new SnowPark DataFrame with the encrypted values
    snowpark_df = session.create_dataframe(encrypted_pdf)

    # Upload Encrypted Data to temporary table then perform a bulk update operation
    session.sql("""CREATE OR REPLACE TABLE XQ_SnowFlake_Demo_Staging LIKE XQ_SnowFlake_Demo;""").collect()

    # Write the encrypted DataFrame to the staging table
    snowpark_df.write.mode("overwrite").saveAsTable("XQ_SnowFlake_Demo_Staging")

    # Execute the update statement
    session.sql(update_sql).collect()

    # Drop the staging table to clean up
    session.sql("DROP TABLE IF EXISTS XQ_SnowFlake_Demo_Staging").collect()

    # Close the Snowpark session
    session.close()