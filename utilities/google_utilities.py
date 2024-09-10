from googleapiclient.discovery import build
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utilities.config import *
from utilities.helper_functions import Querying_folders
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# storing creds

# def Calendar_google_credentials():
#     creds = None
#     # The file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = Credentials.from_authorized_user_info(pickle.load(token), ['https://www.googleapis.com/auth/calendar.readonly'])
#             service = build('calendar', 'v3', credentials=creds)
#             return service
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', ['https://www.googleapis.com/auth/calendar.readonly'])
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds.to_json(), token)
#             service = build('calendar', 'v3', credentials=creds)
#             return service
    

# Google Specific Logic

def Note_delivery_to_google(page_names_and_folder, page_ids):
    creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])

    # Build the service
    service = build('drive', 'v3', credentials=creds)

    # Define the file metadata

    # if file exists directly overwrite file in google drive
    # print("all page/values",page_names_and_folder)
    for key in page_names_and_folder.keys():

        with open('local/actual_notes_DB.json', 'r') as actual_notes_file:
            actual_notes_file_data = json.load(actual_notes_file)
            # print([item.get('page_name') == key for item in actual_notes_file_data])
            # right now I can't change any of the names of the pages but can add that in later. 
            # print(key)

            if True in [item.get('page_name') == key for item in actual_notes_file_data]:

                for item in actual_notes_file_data:
                    if item.get('page_name') == key:

                        media = MediaFileUpload(f'local/{item.get('page_name')}.docx', mimetype='application/octet-stream')

                        # Update the file
                        updated_file = service.files().update(
                            fileId=item.get('file_id'),
                            media_body=media
                        ).execute()

                        print(f"File ID: {updated_file.get('id')} updated successfully.")

            # if file doesn't exist save to folder.  
            else:
                sub_Note_delivery_to_google(key, page_names_and_folder[key], service, actual_notes_file_data)
        
        os.remove(f'local/{key}.docx')

                

def sub_Note_delivery_to_google(page_name, values_UUI, service, data):

    folder_id = Querying_folders(values_UUI, service)
    page_simple_blocks = []
 
    if folder_id != '':
    # flow control on where to send the file to.
        file_metadata = {
            'name': f'{page_name}.docx',  # Replace with your file name
            'parents': [f'{folder_id}']  # saving to Local Store in google drive
        }
        
        # print("###",file_metadata)
        # ### {'name': 'Eigen Layer Restaking Basics Note - 08|01|24 .docx', 'parents': ['']}

        # Path to the file on your local system
        file_path = f'local/{page_name}.docx'

        # Create a media upload object
        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        # Upload the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f'File ID Uploaded: {file.get("id")}, to folder: {folder_id}')

        simple_block = {
            'page_name' : page_name,
            'folder_id' : folder_id,
            'file_id' : file.get("id"),
            'database_id' : values_UUI
        }

        page_simple_blocks.append(simple_block)

    # open local store and append to json file data. 
    if page_simple_blocks != []:

        for item in page_simple_blocks: 
            data.append(item)

        with open(FILE_NAME_FOLDER_AND_ID_LOCAL_STORE, 'w') as file:    
            json.dump(data,file,indent=4)

def file_State_transition_check(potential_store, parent_folder_location, local_store_folder):
    creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])

    # Build the service
    service = build('drive', 'v3', credentials=creds)

    # print("Current working directory:", os.getcwd())

    with open(f'{local_store_folder}', 'r') as file:
        actual_store = json.load(file)
            

        for i in range(len(potential_store)):
            # print("HIT") 

            try:
                if actual_store[i] != potential_store[i]:
                    # print("SHOOT")
                    # changing folder name based off POI DB changes

                    actual_folder_name = ", ".join(actual_store[i].values())
                    potential_folder_name = ", ".join(potential_store[i].values())

                    change_folder_google(actual_folder_name, potential_folder_name, service, parent_folder_location)
            except IndexError:
                # means there is a new file. but I have sub_Note_delivery_to_google handling new files. 
                None

def State_transition_check(potential_store, parent_folder_location, local_store_folder):
    creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])

    # Build the service
    service = build('drive', 'v3', credentials=creds)

    # print("Current working directory:", os.getcwd())

    with open(f'{local_store_folder}', 'r') as file:
        actual_store = json.load(file)


        for data in potential_store:
            flag = 0
            for i, value in enumerate(data.values()):
                try: 
                    if i == 1 and True in [list(item.values())[1] == value for item in actual_store]:
                        # print([list(item.values())[1] == value for item in actual_store])
                # print("HIT")
                        # print("SHOOT")
                        # changing folder name based off POI DB changes
                        for item in actual_store: 
                            if list(item.values())[1] == value:
                                
                                actual_folder_name = ", ".join(str(value) for value in item.values() if value is not None)
                                # print(potential_ordered_store[i])
                                potential_folder_name = ", ".join(str(value) for value in data.values() if value is not None)

                                if potential_folder_name != actual_folder_name:

                                    # print("State Change" potential_folder_name, actual_folder_name)

                                    change_folder_google(actual_folder_name, potential_folder_name, service, parent_folder_location)
                                else:
                                    print("No State Change Needed")
                    elif flag == 0 and True not in [list(item.values())[1] == list(data.values())[1] for item in actual_store]:
                    
                        folder_name = ", ".join(str(value) for value in data.values() if value is not None)
                        create_folder_google(folder_name, service, parent_folder_location)
                        flag += 1
                except IndexError:   
                    # if i out of range of the actual store that means a new person has been added and the potential store is correct
                    print("BOOM")
                    folder_name = ", ".join(str(value) for value in data.values() if value is not None)
                    create_folder_google(folder_name, service, parent_folder_location)

def change_folder_google(actual_folder_name, potential_folder_name, service, parent_folder_location):


    # Search for the folder by name within the specified parent folder\
    # find the actual folder using its actual_folder_name in google drive under a set parent ID and then return to a variable the folder ID
    query = f"name='{actual_folder_name}' and '{parent_folder_location}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        return None
    else:
        folder_id = items[0]['id']
        

        # using the folder ID change actual folder's name with to the potential_folder_name
        # Update the folder's name to the new name
        file_metadata = {
            'name': potential_folder_name
        }
        updated_folder = service.files().update(
            fileId=folder_id,
            body=file_metadata,
            fields='id, name'
        ).execute()


        print(f"Updated Folder Name: {potential_folder_name} from '{actual_folder_name}'")
        return updated_folder['id']


def create_folder_google(folder_name, service, parent_folder_location):

    # Define the folder metadata
    folder_metadata = {
        'name': folder_name,  
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [f'{parent_folder_location}']
    }

    # Create the folder
    folder = service.files().create(body=folder_metadata, fields='id').execute()

    # print(f'Folder ID: {folder.get("id")}')
    print(f'Created New Folder: {folder_name} with Folder ID: {folder.get("id")}')
    return(folder.get("id"))
    
def Get_file_link(file_id, service):
    try:
        # Get the file metadata
        file = service.files().get(fileId=file_id, fields='webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        print(f'An error occurred: {e}')
        return None