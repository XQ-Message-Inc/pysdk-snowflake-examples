# @xqmsg/pysdk-snowflake-examples

An Example Python Implementation of XQ Message Python SDK (V.2) into SnowFlake's SnowPark environment to encrypt & decrypt data stored within a database table. This implementation utilizes XQ Message's Python SDK (V.2) which provides convenient access to the XQ Messsage API. [Full Package Documentation](https://xq-message-inc.github.io/pysdk-core/).

## What is XQ Message?

XQ Message is an encryption-as-a-service (EaaS) platform which gives you the tools to encrypt and decrypt data directly on "edge" devices. The XQ platform is a lightweight and highly secure cybersecurity solution that enables self protecting data for perimeterless [zero trust] (https://en.wikipedia.org/wiki/Zero_trust_security_model) data protection, even to devices and apps that have no ability to do so natively. XQ protects, controls, and tracks all the interactions with the data. XQ monitors what entities attempt access, where they are located and when the interaction occurs.

## Prerequisites

**The supported Python versions are 3.8 | 3.9 | 3.10 | 3.11**

**The examples require Conda - Conda is a powerful command line tool for package and environment management that runs on Windows, MacOS, and Linux.**

### Installing & Setting up Conda

Windows: Please follow this guide to installing and setting up Conda on [Windows](https://conda.io/projects/conda/en/latest/user-guide/install/windows.html).

MacOS: Please follow this guide to installing and setting up Conda on [MacOS](https://conda.io/projects/conda/en/latest/user-guide/install/macos.html).

Linux: Please follow this guide to installing and setting up Conda on [Linux](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html).

### Signing up and accessing SnowFlake

In order to utilize SnowPark you will need to setup a SnowFlake account as well as create a Warehouse, Database, and Schema.

If you do not already have a SnowFlake account set up you can navigate to the [SignUp](https://signup.snowflake.com/) URL and create an account. Snowflake provides a 30-day free Snowflake trial which includes $400 worth of free usage. (At the time of publishing this repository)

In order to create a Warehouse, Database, and Schema you can initialize a new worksheet under Projects and Worksheets followed by clicking on the + icon in the top right hand side of the page. Once you have done so in the drop-down menu select the SQL Worksheet option.

In the worksheet you can create the Warehouse, Database, and Schema by utilizing the following SQL code. Change the naming of the values accordingly.

```sql
CREATE WAREHOUSE DWH_EXAMPLE;
CREATE DATABASE DB_Example;
CREATE SCHEMA DB_Example.Example;
```

Additionally you will also need the ACCOUNT_ID, USERNAME, PASSWORD, and ROLE for the specific role you are utilizing within SnowPark. The USERNAME, PASSWORD, and ROLE are self-explanatory but the ACCOUNT_ID can be identified by clicking on the bottom left corner of the screen where it will show your account, followed by hovering over your specific account, lastly hover over your account one more time in pop-out menu and the ACCOUNT_ID will be your Locator within that pop-out menu.

### Initializing the XQ SDK

In order to utilize the XQ SDK and interact with XQ servers you will need both the **`General`** and **`Dashboard`** API keys. To generate these keys, follow these steps:

1. Go to your [XQ management portal](https://manage.xqmsg.com/applications).
2. Select or Create an application by clicking on the "ADD NEW" button.
3. Create a **`General`** key for the XQ framework API.
4. Create a **`Dashboard`** key for the XQ dashboard API.

### Inputting information into a environment variables file

These values can now be set in a .env file within the examples directory as such:

```plaintext
#SnowFlake Connection Parameters
ACCOUNT_ID=
USERNAME=''
PASSWORD=''
ROLE=''
DATABASE=''
WAREHOUSE=''
SCHEMA=''

# XQ API Key Parameters
XQ_API_KEY=''
XQ_DASHBOARD_API_KEY=''
```

## Installation

Open a terminal window for your specific environment, navigate to the directory of your choice and run the following command in your terminal.

```
git clone git@github.com:XQ-Message-Inc/pysdk-snowflake-examples.git
conda env create -f environment.yml
conda activate xq-snowflake-examples
```

## Examples

- [Generate Example Table with Sample Data](examples/create_example.py)
- [Encrypt RAW data within a database table with OTP](examples/encryption_otp.py)
- [Encrypt RAW data within a database table with AES256](examples/encryption_aes.py)
- [Decrypting OTP Encrypted data within a database table](examples/decryption_otp.py)
- [Decrypting AES Encrypted data within a database table](examples/decryption_aes.py)

### Step 1: Generate Example Table with Sample Data

In order to generate an example table with sample data you can simply run the following example.

```
python create_example.py
```

This will create an example table with ID, FirstName, LastName, Address, PhoneNumber. By default it will populate the table with 10 random entries - the number of entries can be altered by altering line 48. These values will be raw data within a database table initially which we will encrypt utilizing XQ.

### Step 2: Encrypt Individual Rows within the Example Table

In order to encrypt individual rows within the example table we can either utilize OTP or AES256. An example of how this can be done is within the [encryption_otp.py](examples/encryption_otp.py) or if you prefer AES256 utilize the example in the [encryption_aes.py](examples/encryption_aes.py).

One-Time-Pad:

```
python encryption_otp.py
```

AES:

```
python encryption_aes.py
```

This will handle the authentication and authorization to XQ through the user input of email, first name, and last name. In turn this will send a pin to the email provided and wait for input of that pin. It will then handle the exchange of an access token to XQ's backend based on the credentials provided. It then generates a pool of quantum entropy through XQ's through XQ and utilize that to generate unique encryption keys for each row. Then it will process each row within the DataFrame and encrypt each value within that row with the unique encryption key. These values will get written to a temporary table which is utilized to update the plain-text values stored within the main table with the encrypted data. Lastly it will drop the temporary table and handle the clean up as well as close the Snowpark session.

Note: AES-GCM also requires a Nonce which is added to the table entry along with the locator token.

### Step 3: Decrypt Individual Rows within the Example Table

In order to decrypt individual rows within the example table we can either utilize OTP or AES256 depending on which algorithm we utilized to encrypt the values. An example of how this can be done is within the [decryption_otp.py](examples/decryption_otp.py) or if you utilized AES256 you can use the example in the [decryption_aes.py](examples/decryption_aes.py).

One-Time-Pad:

```
python decryption_otp.py
```

AES:

```
python decryption_aes.py
```

Very similarly to the encryption example this will handle the authentication and authorization to XQ through the user input of email, first name, and last name. In turn this will send a pin to the email provided and wait for input of that pin. It will then handle the exchange of an access token to XQ's backend based on the credentials provided. Data will then be retrieved from the Snowflake table we created previously, and convert it to a Pandas DataFrame as well as print the encrypted table. For each row in the DataFrame, except for the 'ID' column it seperate the first 43 bytes and the remaining bytes as this is how we stored the locator token in the encryption step. Each iteration will request the specific key utilizing the locator token and decrypt the encrypted row. The decrypted rows are then printed to display the decrypted values.

Note: AES-GCM also requires a Nonce which in our previous example we added this after the locator token therefore in the decryption_aes.py example it also seperates those bytes.
