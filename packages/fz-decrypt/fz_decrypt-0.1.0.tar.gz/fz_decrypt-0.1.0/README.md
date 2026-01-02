FileZilla Decryptor Lib (fz-decrypt)

A lightweight, robust Python library for decrypting FileZilla Server passwords protected by a master password (sitemanager.xml).

This library implements FileZilla's cryptography logic (PBKDF2, X25519 Key Exchange, AES-GCM) in pure Python.

Prerequisites

Python 3.7 or higher

cryptography library

Installation

Via PyPI (Recommended)

You can easily install the library from the Python Package Index (PyPI):

pip install fz-decrypt

From Source (Development)

If you want to modify the code or install a local version:

Clone the repository or download the source.

Navigate to the directory containing pyproject.toml.

Run:

pip install .


For development (changes are reflected immediately):

pip install -e .


Usage

The library provides a main class FileZillaDecryptor. It requires no instantiation; the decrypt method is a static/class method.

Simple Example

from fz_decrypt import FileZillaDecryptor, DecryptionError, InvalidDataError

# 1. Data from FileZilla sitemanager.xml
# These strings can be found in the <PubKey> and <Pass> tags
xml_pubkey = "..."  # Base64 String
xml_pass_blob = "..."  # Base64 String

# 2. The user's master password
master_password = "MySecretMasterPassword"

try:
    # Attempt decryption
    cleartext_password = FileZillaDecryptor.decrypt(
        master_password,
        xml_pubkey,
        xml_pass_blob
    )
    print(f"The decrypted password is: {cleartext_password}")

except DecryptionError:
    print("Error: The master password is incorrect or the data is corrupt.")

except InvalidDataError as e:
    print(f"Error: Invalid data format (Base64 error, etc.): {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")


API Reference

FileZillaDecryptor.decrypt(master_password, xml_pubkey, xml_pass)

Decrypts a password.

Parameters:

master_password (str): The master password entered when starting FileZilla.

xml_pubkey (str): The content of the <PubKey> tag from the XML file (Base64 encoded).

xml_pass (str): The content of the <Pass> tag from the XML file (Base64 encoded).

Returns:

str: The decrypted password in cleartext.

Exceptions:

DecryptionError: Raised if the master password is incorrect (AES-GCM Tag Mismatch).

InvalidDataError: Raised if the Base64 strings are invalid or the blobs have an incorrect length.

Security Note

This tool is intended for recovering your own passwords. Please handle decrypted credentials responsibly. Never store passwords unencrypted in text files if it can be avoided.

License

This project is licensed under the MIT License.
