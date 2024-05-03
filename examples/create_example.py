# Import the neccessary packages
from snowflake.snowpark import Session
from snowflake.snowpark.functions import *
from faker import Faker
from dotenv import load_dotenv

import pandas as pd
import os

# Initialize data that is in your .env file
load_dotenv()

# Initialize the Faker library
fake = Faker()

# Define your connection options
connection_parameters = {
    "account": os.getenv('ACCOUNT_ID'),
    "user": os.getenv('USERNAME'),
    "password": os.getenv('PASSWORD'),
    "role": os.getenv('ROLE'),
    "warehouse": os.getenv('WAREHOUSE'),
    "database": os.getenv('DATABASE'),
    "schema": os.getenv('SCHEMA')
}

# Create a session object to connect to Snowflake
session = Session.builder.configs(connection_parameters).create()

# SQL command to create the table
create_table_sql = """
CREATE OR REPLACE TABLE XQ_SnowFlake_Demo (
    ID INT,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Address VARCHAR(255),
    PhoneNumber VARCHAR(255)
)
"""

# Execute the SQL command
session.sql(create_table_sql).collect()

# Create a sequence
session.sql("CREATE OR REPLACE SEQUENCE xqdemo_sequence START WITH 1 INCREMENT BY 1").collect()

# Generate and insert 10 random entries
for _ in range(10):
    first_name = fake.first_name()
    last_name = fake.last_name()
    address = fake.address().replace('\n', ', ')
    phone_number = fake.phone_number()

    # Note: Directly integrating xqdemo_sequence.NEXTVAL into the statement, not as a string
    insert_sql = f"""
    INSERT INTO XQ_SnowFlake_Demo (ID, FirstName, LastName, Address, PhoneNumber)
    VALUES (xqdemo_sequence.NEXTVAL, '{first_name}', '{last_name}', '{address}', '{phone_number}')
    """

    session.sql(insert_sql).collect()

# Execute the query
result_set = session.sql("SELECT FirstName, LastName, Address, PhoneNumber FROM XQ_SnowFlake_Demo").collect()

# Convert the results into a Pandas DataFrame
df = pd.DataFrame(result_set, columns=['FirstName', 'LastName', 'Address', 'PhoneNumber'])

# Display the DataFrame
print(df)