from dotenv import load_dotenv
import imaplib  # Library for connecting to email using IMAP
import email  # Library for processing email content
from tqdm import tqdm  # For showing a progress bar
from bs4 import BeautifulSoup  # For parsing HTML content
import requests  # For sending HTTP requests
import os 

# Load environment variables (e.g., email credentials) from a .env file
load_dotenv()

# Function to connect to your email account
def connect_to_email():
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    # Check if the credentials are provided
    if not email_address or not email_password:
        raise ValueError("Email or password is not set. Check your .env file.")

    try:
        # Show progress while connecting to the email server
        with tqdm(total=3, desc="Connecting to email") as pbar:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")  # Connect to Gmail's IMAP server
            pbar.update(1)

            # Log in using your email address and password
            mail.login(email_address, email_password)
            pbar.update(1)

            mail.select("inbox", readonly=False)  # Select the inbox to access email messages and use readonly=False to allow message deletion if needed
            pbar.update(1)

        print("Connected to email successfully!")
        return mail
    except imaplib.IMAP4.error as e:
        print(f"Failed to connect: {e}")
        raise

# Function to extract unsubscribe links from HTML content in emails
def extract_emails_from_html(html_content):
    # Debugging: Show the first 200 characters of the email content to understand the input
    print("HTML Content to Parse:", html_content[:200])
    # Check if the email content is valid HTML (it should start with "<")
    if not html_content.strip().startswith("<"):
        print("Skipped non-HTML content.")
        return []  # return an empty list if the content is not HTML
    soup = BeautifulSoup(html_content, "html.parser")  # Parse the HTML content using BeautifulSoup
    # Find all links in the HTML that contain the word "unsubscribe"
    links = [a["href"] for a in soup.find_all("a", href=True) if "unsubscribe" in a["href"]]

    return links

def click_unsubscribe_link(link):
    try:
        response = requests.get(link)  # Send a GET request to the unsubscribe link
        if response.status_code == 200:
            print(f"Unsubscribed successfully from: {link}")
        else:
            print(f"Failed to unsubscribe from: {link}, error code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to the link: {link}")
        print(e)

# Function to search for emails and extract unsubscribe links
def search_for_emails():
    mail = connect_to_email() # Connect to your email account using the function.

    # Search for emails that contain the word "unsubscribe" in their body
    _, search_data = mail.search(None, '(BODY "unsubscribe")')
    data = search_data[0].split()  # Get a list of email IDs that match the search

    # List to store all unsubscribe links found
    links = []

    # Loop through each email ID
    for number in data:
        _, message_data = mail.fetch(number, "(RFC822)")
        message = email.message_from_bytes(message_data[0][1])

        # Check if the email has multiple parts (e.g., plain text and HTML)
        if message.is_multipart():
            for part in message.walk():
                # Process plain text and HTML parts
                if part.get_content_type() in ["text/plain", "text/html"]:
                    body = part.get_payload(decode=True).decode()
                    links.extend(extract_emails_from_html(body))
        else:
            # If the email is not multipart, process it directly
            body = message.get_payload(decode=True).decode()
            links.extend(extract_emails_from_html(body))
            
    mail.logout()

    return links

#Fucntion to sava the links to a file
def save_links_to_file(links):
    with open("unsubscribe_links.txt", "w") as file:
        for link in links:
            file.write(link + "\n")

# Testing the functions
result = search_for_emails()

# Check if any unsubscribe links were found and display them
if result:
    print("Unsubscribe Links Found:")
    for link in result:
        # print(link)
        click_unsubscribe_link(link)
else:
    print("No unsubscribe links found.")
    
# Save the unsubscribe links to a file
save_links_to_file(result)
