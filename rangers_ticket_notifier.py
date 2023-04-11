import requests
from bs4 import BeautifulSoup
import time
import imaplib
import email
from email.message import EmailMessage
import logging
import os
from datetime import datetime, timedelta
import env

# Replace these with your email credentials
EMAIL_ADDRESS = env.EMAIL_ADDRESS
EMAIL_PASSWORD = env.EMAIL_PASSWORD
FOLDER_NAME = env.FOLDER_NAME
YOUR_PERSONAL_EMAIL = env.YOUR_PERSONAL_EMAIL

# Set up logging
log_filename = 'ticket_notifier.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_email(to_address):
    msg = EmailMessage()
    msg.set_content('Rangers Chase Lounge tickets are now available!\n\nCheck them out here: https://chasegetsyoucloser.com/lounges/madison-square-garden')
    msg['Subject'] = 'Rangers Chase Lounge Tickets Available'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_address
    return msg

def send_email(to_address):
    msg = create_email(to_address)
    with imaplib.IMAP4_SSL('imap.gmail.com', 993) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.select(FOLDER_NAME)
        server.append(FOLDER_NAME, '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        server.logout()

def check_tickets():
    url = 'https://chasegetsyoucloser.com/lounges/madison-square-garden'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    event_list = soup.find_all('div', class_='event-info')

    for event in event_list:
        if 'Rangers' in event.find('h4', class_='event-name').text:
            status = event.find('a', class_='event-link').text
            if 'Reserve' in status:
                # Send email to the specified folder and your personal email
                send_email(EMAIL_ADDRESS)
                send_email(YOUR_PERSONAL_EMAIL)
                return True
    return False

def cleanup_logs():
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    if os.path.exists(log_filename) and datetime.fromtimestamp(os.path.getmtime(log_filename)) < week_ago:
        os.remove(log_filename)
        logging.info('Log file cleaned up')

if __name__ == '__main__':
    cleanup_logs()
    logging.info('Script started')
    if check_tickets():
        logging.info('Email sent to IMAP folder and personal email')
    else:
        logging.info('Tickets not available yet')
