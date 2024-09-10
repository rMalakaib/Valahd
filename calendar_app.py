import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from utilities.config import *
import re
from collections import Counter
import json
from utilities.google_utilities import Get_file_link
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the calendar IDs
CALENDAR_IDS = [
    'robertburkhart08@gmail.com'
]

MAX_RESULTS = 10

YOUR_COMPANY_EMAIL = 'robertburkhart08@gmail.com'

YOUR_COMPANIES_EMAIL_DOMAIN = 'huttcapital.com'

IGNORED_DOMAINS = ["aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com", "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com", "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk", "email.com", "fastmail.fm", "games.com", "gmx.net", "hush.com", "hushmail.com", "icloud.com", "iname.com", "inbox.com", "lavabit.com", "love.com", "outlook.com", "pobox.com", "protonmail.ch", "protonmail.com", "tutanota.de", "tutanota.com", "tutamail.com", "tuta.io", "keemail.me", "rocketmail.com", "safe-mail.net", "wow.com", "ygm.com", "ymail.com", "zoho.com", "yandex.com", "bellsouth.net", "charter.net", "cox.net", "earthlink.net", "juno.com", "btinternet.com", "virginmedia.com", "blueyonder.co.uk", "freeserve.co.uk", "live.co.uk", "ntlworld.com", "o2.co.uk", "orange.net", "sky.com", "talktalk.co.uk", "tiscali.co.uk", "virgin.net", "wanadoo.co.uk", "bt.com", "sina.com", "sina.cn", "qq.com", "naver.com", "hanmail.net", "daum.net", "nate.com", "yahoo.co.jp", "yahoo.co.kr", "yahoo.co.id", "yahoo.co.in", "yahoo.com.sg", "yahoo.com.ph", "163.com", "yeah.net", "126.com", "21cn.com", "aliyun.com", "foxmail.com", "hotmail.fr", "live.fr", "laposte.net", "yahoo.fr", "wanadoo.fr", "orange.fr", "gmx.fr", "sfr.fr", "neuf.fr", "free.fr", "gmx.de", "hotmail.de", "live.de", "online.de", "t-online.de", "web.de", "yahoo.de", "libero.it", "virgilio.it", "hotmail.it", "aol.it", "tiscali.it", "alice.it", "live.it", "yahoo.it", "email.it", "tin.it", "poste.it", "teletu.it", "mail.ru", "rambler.ru", "yandex.ru", "ya.ru", "list.ru", "hotmail.be", "live.be", "skynet.be", "voo.be", "tvcablenet.be", "telenet.be", "hotmail.com.ar", "live.com.ar", "yahoo.com.ar", "fibertel.com.ar", "speedy.com.ar", "arnet.com.ar", "yahoo.com.mx", "live.com.mx", "hotmail.es", "hotmail.com.mx", "prodigy.net.mx", "yahoo.ca", "hotmail.ca", "bell.net", "shaw.ca", "sympatico.ca", "rogers.com", "yahoo.com.br", "hotmail.com.br", "outlook.com.br", "uol.com.br", "bol.com.br", "terra.com.br", "ig.com.br", "itelefonica.com.br", "r7.com", "zipmail.com.br", "globo.com", "globomail.com", "oi.com.br"]

TOKEN_PATH = 'token.json'

CLIENT_SECRET_FILE = 'client_secrets.json'

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None

    # Load existing credentials from token.json if available
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            creds = None  # Force reauthentication if credentials can't be loaded

    # If no valid credentials are available or they are expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Try to refresh the token
            try:
                creds.refresh(Request())
                print("Token successfully refreshed!")
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None  # Force reauthentication if refresh fails
        else:
            # No valid credentials available, proceed with reauthentication
            print("No valid credentials, starting reauthentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Start a local server for Google OAuth

    # Save the refreshed or newly authenticated credentials back to token.json
    if creds:
        try:
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
                print("Credentials successfully saved to token.json")
        except Exception as e:
            print(f"Error saving credentials to token.json: {e}")
    
    return creds

def application():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    time_max = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
    
    event_list = []

    for calendar_id in CALENDAR_IDS:
        try:
            events_result = service.events().list(
                calendarId=calendar_id, 
                timeMin=now, 
                timeMax=time_max,
                maxResults=MAX_RESULTS, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])

            if not events:
                continue
            else:
                for event in events:
                    event_info = {
                        'title': event.get('summary', 'No Title'),  # The event summary is the title in Google Calendar API
                        'attendees': [attendee['email'] for attendee in event.get('attendees', [])]
                    }
                    event_list.append(event_info)

        except Exception as e:
            print(f'An error occurred while fetching events for calendar ID {calendar_id}: {e}')
    # print(event_list)
    return event_list

# if more than one similar company email domain's (that are not your own company) (ignore common tags like @gmail.com, comcast.net) then search company email domain in Company_DB and use correlated folder UUI to scan actual_notes and query to retrieve all links to each file. returns a list of the file names and ID's to be handled in email_delivery service
def email_domain_matching(event, service):
    # use regex to get everything after the @ symbol.
    # would be better if we can execute the action atomically rather than for looping (wonder what coding language would help us do that)
    regex_matches = [
        match.group(1) for attendee in event['attendees']
        if (match := re.search(r'@(.+)', attendee)) and match.group(1) not in IGNORED_DOMAINS
    ]
                
    # count how many of one domain there is, if more than one of similar domains append to master list 
    email_domain_keys = []
    counted = Counter(regex_matches)
    # print("counted: ", counted)
    # print("counted items: ", counted.items())
    # filtering for the (that are not your own company)
    for key,value in counted.items():
        if value > 1 and key not in YOUR_COMPANY_EMAIL and key != YOUR_COMPANIES_EMAIL_DOMAIN:
            email_domain_keys.append(key)
    
    pages_link = {}
    # search company_DB local json for match. 
    with open(COMPANY_LOCAL_STORE, 'r') as company_DB_data: 
        with open(FILE_NAME_FOLDER_AND_ID_LOCAL_STORE, 'r') as file_location: 
            for company_row in json.load(company_DB_data):
                if company_row['email_domain'] in email_domain_keys:
                    for file_row in json.load(file_location):
                        if company_row['company_UUI'] == file_row['database_id']:
                            link = Get_file_link(file_row['file_id'], service) 
                            pages_link[file_row['page_name']] = link

    return pages_link

# if more than one person (that are not your own company) (ignore common domains like @gmail.com, @comcast.net) but don't share email domains then search person emails for exact match in POI_DB and use correlated folder UUI to scan actual_notes and query to retrieve all links to each file. Then send an email with all the information.  returns a list of the file names and ID's to be handled in email_delivery service
def full_email_matching(event, service):
    # Extract domains while excluding company email and ignored domains
    regex_matches = [
        match.group(1) for attendee in event['attendees']
        if (match := re.search(r'@(.+)', attendee)) and YOUR_COMPANY_EMAIL not in attendee
    ]

    # Remove company email from attendees if present
    if YOUR_COMPANY_EMAIL in event['attendees']:
        event['attendees'].pop(event['attendees'].index(YOUR_COMPANY_EMAIL))

    # print(event['attendees'])
    # print(regex_matches)
    
    counted = Counter(regex_matches)
    # print(counted)

    master = []

    # Create a domain-to-email map
    domain_to_emails = {}
    for attendee in event['attendees']:
        match = re.search(r'@(.+)', attendee)
        if match:
            domain = match.group(1)
            if domain not in domain_to_emails:
                domain_to_emails[domain] = []
            domain_to_emails[domain].append(attendee)

    for key, value in counted.items():
        if value > 1:
            if key in IGNORED_DOMAINS:
                # Append the full emails that correspond to the domain
                master.extend(domain_to_emails[key])
        elif value == 1:
            # Append the full email that corresponds to the domain
            master.extend(domain_to_emails[key])

    pages_link = {}

    with open(POI_LOCAL_STORE, "r") as poi_file:
        with open(FILE_NAME_FOLDER_AND_ID_LOCAL_STORE, 'r') as file_location:
            for poi_data in json.load(poi_file):
                if poi_data['email'] in master:
                    for file_row in json.load(file_location):
                        if poi_data['poi_UUI'] == file_row['database_id']:
                            link = Get_file_link(file_row['file_id'], service)
                            pages_link[file_row['page_name']] = link

    return pages_link

# if company name or person name (that are not your own company) (ignore common tags like @gmail.com, comcast.net) from COMPANY_DB or POI_DB in title then use the correlated folder UUI to scan actual_notes and query to retrieve all links to each file. Then send an email with all the information.  returns a list of the file names and ID's to be handled in email_delivery service
def title_matching(event):
    # could read title and match to database items if wanted to, for this use case its not needed as of present.
    return

# for debugging
# def list_calendars():
#     try:
#         print("Loading credentials...")
#         creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/calendar.readonly'])
#         service = build('calendar', 'v3', credentials=creds)

#         print("Retrieving calendar list...")
#         calendar_list = service.calendarList().list().execute()
#         print("Response received from calendar list API:", calendar_list)
        
#         calendars = calendar_list.get('items', [])
        
#         if not calendars:
#             print('No calendars found.')
#         else:
#             for calendar in calendars:
#                 print(f"Calendar Name: {calendar['summary']}")
#                 print(f"Calendar ID: {calendar['id']}\n")

#     except Exception as e:
#         print(f"An error occurred: {e}")

# list_calendars()

def email_delivery_service(event_list):
    link_credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.readonly'])
    
    link_service = build('drive', 'v3', credentials=link_credentials)
    
    creds = get_credentials()
    gmail_service = build('gmail', 'v1', credentials=creds)

    for event in event_list:
        company_data = email_domain_matching(event, link_service)
        poi_data = full_email_matching(event, link_service)

        if company_data or poi_data:
            email_body = ""
            if company_data:
                email_body += "Company Data:\n" + format_data(company_data) + "\n\n"
            if poi_data:
                email_body += "POI Data:\n" + format_data(poi_data)

            send_email(event['title'], email_body, "robertburkhart08@gmail.com", gmail_service)

def format_data(data):
    formatted_data = ""
    for key, value in data.items():
        formatted_data += f"'{key}':\n'{value}',\n\n"
    return formatted_data.strip()

def send_email(subject, body, to_email, gmail_service):
    try:
        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        message_body = {'raw': raw_message}

        sent_message = gmail_service.users().messages().send(userId="me", body=message_body).execute()
        print(f"Message Id: {sent_message['id']}")

    except HttpError as error:
        print(f"An error occurred: {error}")
        sent_message = None

    return sent_message

def Calendar_app():
    event_list = application()
    print(event_list)
    email_delivery_service(event_list)

