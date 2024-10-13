import os
import base64
import re
from datetime import datetime
from dateutil import parser  # For flexible date parsing
import mysql.connector
from mysql.connector import Error
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import spacy
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

class PurchaseItem:
    def __init__(self, product_name, amount, date):
        self.product_name = product_name
        self.amount = amount
        self.date = date

def authenticate_gmail():
    creds = None
    # Check if token.json already exists (stores user access and refresh tokens).
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials available, request login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text

def get_email_body(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            mimeType = part.get('mimeType')
            if mimeType == 'text/plain' or mimeType == 'text/html':
                data = part['body'].get('data')
                if data:
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    if mimeType == 'text/html':
                        text = html_to_text(text)
                    body += text + '\n'
            elif 'parts' in part:
                # Recursively get parts
                body += get_email_body(part)
    else:
        mimeType = payload.get('mimeType')
        if mimeType == 'text/plain' or mimeType == 'text/html':
            data = payload['body'].get('data')
            if data:
                text = base64.urlsafe_b64decode(data).decode('utf-8')
                if mimeType == 'text/html':
                    text = html_to_text(text)
                body += text + '\n'
    return body

def extract_purchase_info(msg):
    snippet = msg.get('snippet', '')
    payload = msg.get('payload', {})
    headers = payload.get('headers', [])
    amount = None
    date = None
    product_name = None  # Set to None initially

    # Extract the subject
    subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), '')

    # Print the subject and snippet for debugging
    print(f"\nDEBUG: Email Subject: {subject}")
    print(f"DEBUG: Email Snippet: {snippet}")

    # Extract email body content
    body = get_email_body(payload)

    # Print the body for debugging
    print(f"DEBUG: Email Body: {body[:500]}")  # Limiting to first 500 characters for readability

    # Split the body into lines
    lines = body.split('\n')

    # Initialize variables to store extracted info
    product_names = []
    amounts = []
    dates = []

    # Regex patterns for months
    month_regex = r'(January|February|March|April|May|June|July|August|September|October|November|December|\b[0-1]?[0-9]\b)'
    date_regex = r'\b(' + month_regex + r')[\s\-./,]*(\d{1,2})?'

    # Iterate over the lines to find product names, amounts, and dates
    for line in lines:
        # Remove leading/trailing whitespace
        line = line.strip()

        # Improved: Look for product name near images (based on screenshot observation)
        if '<img' in line or 'Qty' in line:
            next_line = line
            product_match = re.search(r'Qty\s*:\s*\d+\s*(.+)', next_line, re.IGNORECASE)
            if product_match:
                product = product_match.group(1).strip()
                product_names.append(product)
                print(f"DEBUG: Found product name near 'Qty': {product}")

        # Check for amounts
        amount_match = re.search(r'(Total|Amount|Order Total|Charged|Price|Subtotal)\s*[:\-]?\s*\$?([0-9,]+\.?[0-9]*)', line, re.IGNORECASE)
        if amount_match:
            amount = amount_match.group(2)
            amounts.append(amount)
            print(f"DEBUG: Found amount: {amount}")

        # Check for dates
        date_match = re.search(r'(Order Date|Purchased on|Date|Order Placed)\s*[:\-]?\s*(.+)', line, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(2).strip()
            # Parse the date and ensure month is valid
            parsed_date = parse_date(date_str)
            if parsed_date:
                dates.append(parsed_date)
                print(f"DEBUG: Found date: {parsed_date}")

        # Additional checks for product names in list items or bullet points
        bullet_match = re.match(r'^\s*•\s*(.+)', line)
        if bullet_match:
            bullet_product = bullet_match.group(1).strip()
            product_names.append(bullet_product)
            print(f"DEBUG: Found product name in bullet point: {bullet_product}")

    # If no product names found, try using NER (Natural Entity Recognition)
    if not product_names:
        # Process the email content with spaCy to extract entities
        doc = nlp(subject + " " + body)
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG"]:  # Look for product or organization entities
                product_names.append(ent.text)
                print(f"DEBUG: Found product name via NER: {ent.text}")

    # Similarly for amounts
    if not amounts:
        doc = nlp(body)
        for ent in doc.ents:
            if ent.label_ == "MONEY":
                # Extract numeric value from MONEY entity
                amount_value = ''.join(re.findall(r'\d+\.?\d*', ent.text))
                amounts.append(amount_value)
                print(f"DEBUG: Found amount via NER: {amount_value}")

    # Similarly for dates
    if not dates:
        doc = nlp(body)
        for ent in doc.ents:
            if ent.label_ == "DATE":
                # Parse the date and ensure month is valid
                parsed_date = parse_date(ent.text)
                if parsed_date:
                    dates.append(parsed_date)
                    print(f"DEBUG: Found date via NER: {parsed_date}")

    # Choose the first product name, amount, date if available
    product_name = product_names[0] if product_names else "Unknown Purchase"
    amount = amounts[0] if amounts else None
    date = dates[0] if dates else None

    # Return the extracted purchase information
    return PurchaseItem(product_name, amount, date) if product_name != "Unknown Purchase" else None


def parse_date(date_str):
    try:
        # Try parsing the date string
        parsed_date = parser.parse(date_str, fuzzy=True)
        # Check if month is between January and December
        if 1 <= parsed_date.month <= 12:
            # Return date in MM/DD format
            formatted_date = parsed_date.strftime('%m/%d')
            return formatted_date
    except (ValueError, OverflowError):
        pass
    return None  # Return None if parsing fails or month is invalid

def store_purchases_in_db(purchase_items):
    # Database connection settings
      db_config = {
        'user': 'admin',
        'password': 'yourpassword',
        'host': 'yourhost',
        'database': 'trackingprice_db',
        'raise_on_warnings': True
      }

    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()

            # Insert purchase items into the database
            for item in purchase_items:
                cursor.execute('''
                    INSERT INTO purchases (product_name, amount, purchase_date)
                    VALUES (%s, %s, %s)
                ''', (item.product_name, item.amount, item.date))

            connection.commit()
            print('Purchase items have been stored in the database.')

    except Error as err:
        print(f"Error: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def track_prices(purchase_items):
    # Mock price database
    mock_price_db = {
        "Laptop": 1000,
        "Apple Product": 800,
        "Bike Ride Payment": 5.5,
        "DraftKings Purchase": 25
    }

    print('\nPrice Check Results:')
    for item in purchase_items:
        current_price = mock_price_db.get(item.product_name, None)
        if current_price:
            print(f"The current price for {item.product_name} is ${current_price}")
            if item.amount:
                print(f"Your purchase amount was {item.amount}")
            if item.date:
                print(f"Purchase date: {item.date}")
        else:
            print(f"No price data available for {item.product_name}")

def get_purchase_emails():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API to get the list of messages.
    results = service.users().messages().list(userId='me', q='subject:order', maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No purchase emails found.')
    else:
        print('Purchase emails:')
        purchase_items = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            purchase_item = extract_purchase_info(msg)
            if purchase_item:
                purchase_items.append(purchase_item)

        # Store purchase items in database
        store_purchases_in_db(purchase_items)

        # Print the purchase items
        print("\nExtracted Purchase Items:")
        for item in purchase_items:
            print(f"Product Name: {item.product_name}")
            print(f"Amount: {item.amount}")
            print(f"Date: {item.date}")
            print("-" * 40)

        # Mock price tracking
        track_prices(purchase_items)

if __name__ == '__main__':
    get_purchase_emails()
