# Import the neccessary packages
from xq import XQ
from snowflake.snowpark import Session
from dotenv import load_dotenv

import base64
import pandas as pd
import os

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

def decrypt_field_aes(field_data, locator_token, nonce):
    key_packet = xq.api.get_packet(locator_token)
    try:
        decrypted_text = xq.decrypt_message(base64.b64decode(field_data), key=key_packet, algorithm="AES", nonce=base64.b64decode(nonce))
        return decrypted_text
    except Exception as e:
        print(f"Error decrypting field: {e}")
        return None

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

    df = session.sql('SELECT * from XQ_SnowFlake_Demo')
    pdf = df.toPandas()

    for row in pdf.itertuples(index=True):
        decrypted_values = [decrypt_field_aes(getattr(row, col)[67:], getattr(row, col)[0:43], getattr(row, col)[43:67]) for col in pdf.columns if col != 'ID']
        print(decrypted_values)
  
    session.close()
