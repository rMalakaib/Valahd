from notion_client import Client
from utilities.config import *
from utilities.google_utilities import State_transition_check
from utilities.helper_functions import *

def note_library_retrieval(notion_token, notion_database_id):

    client = Client(auth=notion_token)

    # note_db_info = client.databases.retrieve(database_id=notion_database_id)

    # Write_dict_to_file_as_json(note_db_info, 'note_library_db_info.json')
    
    note_db_rows = Fetch_all_rows(client, notion_database_id)

    # Write_dict_to_file_as_json(note_db_rows, f'note_library_note_db_rows.json')
    
    simple_rows = []

    for row in note_db_rows:
        
        topic = Safe_get(row, 'properties.Topic.rich_text.0.plain_text')
        note_UUI = Safe_get(row, 'properties.Note_UUI.title.0.plain_text')

        simple_rows.append({
            'topic' : topic,
            'note_UUI': note_UUI
        })

    # needed the folder UUI

    State_transition_check(simple_rows, NOTE_LIBRARY_FOLDER_ID, NOTE_LIBRARY_LOCAL_STORE)

    return simple_rows


def Note_Library_Folder_Creation_Changes():
    
    potential_store = note_library_retrieval(NOTION_TOKEN, NOTE_LIBRARY_NOTION_DB)

    # overwriting the simple_rows.json to change the state from the previous store to the new store. 
    Write_dict_to_file_as_json(potential_store, f'{NOTE_LIBRARY_LOCAL_STORE}')
