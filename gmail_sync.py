import imaplib
import ssl
import re

def connect_to_imap_server(server, username, password):
    try:
        # Create SSL context
        context = ssl.create_default_context()
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        
        # Establish a connection to the IMAP server
        imap = imaplib.IMAP4_SSL(server, 993)
        imap.ssl_context = context
        
        # Login to the server
        imap.login(username, password)
        
        # Print success message
        print(f"Successfully connected to {server} as {username}")
        
        return imap
        
    except imaplib.IMAP4.error as e:
        # Print error message if connection fails
        print(f"Failed to connect to {server}: {e}")
        return None

def create_folder(imap, folder_name):
    # Remove leading and trailing whitespaces
    folder_name = folder_name.strip()

    # Check if folder exists
    typ, data = imap.list()
    for line in data:
        if folder_name in str(line):
            print(f"Folder '{folder_name}' already exists")
            return

    # Attempt to create the folder
    try:
        print(f"Attempting to create folder '{folder_name}'")
        typ, response = imap.create(folder_name)
        print(f"Response from server: {typ}, {response}")
        if typ == "OK":
            print(f"Folder '{folder_name}' created successfully")
        else:
            print(f"Failed to create folder '{folder_name}': {response}")
    except Exception as e:
        print(f"Error occurred while creating folder '{folder_name}': {e}")



def convert_gmail_labels_to_folders(imap_gmail, imap_standard):
    # Fetch Gmail labels
    typ, data = imap_gmail.list()
    if typ == "OK":
        for line in data:
            print(f"Fetched Gmail label: {line.decode()}")  # Debugging line

            # Extract label name using regular expressions
            label_match = re.match(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)', line.decode())
            if label_match:
                label_name = label_match.group('name').strip('"')

                # Skip "HasChildren" and "HasNoChildren" flags
                if label_name.startswith("[Gmail]"):
                    continue

                print(f"Processing Gmail label: {label_name}")

                # Construct folder hierarchy
                label_parts = label_name.split("/")
                folder_path = ""
                for part in label_parts:
                    folder_path += part + "/"
                    print(f"Attempting to create folder on server #2: {folder_path}")

                    # Create folder
                    create_folder(imap_standard, folder_path[:-1])  # Remove trailing slash

    else:
        print("Failed to fetch Gmail labels")


# Server 1 (Gmail)
server_gmail = "imap.gmail.com"
username_gmail = "username@gmail.com"
password_gmail = "app password"

# Server 2 (Standard IMAP)
server_standard = "imap.server.tld"
username_standard = "username"
password_standard = "password"

# Connect to server 1 (Gmail)
imap_gmail = connect_to_imap_server(server_gmail, username_gmail, password_gmail)

# Connect to server 2 (Standard IMAP)
imap_standard = connect_to_imap_server(server_standard, username_standard, password_standard)

# Convert Gmail labels to standard IMAP folders
if imap_gmail and imap_standard:
    convert_gmail_labels_to_folders(imap_gmail, imap_standard)

# Logout from servers
if imap_gmail:
    imap_gmail.logout()
if imap_standard:
    imap_standard.logout()
