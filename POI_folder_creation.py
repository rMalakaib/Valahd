from notion_client import Client
from utilities.config import *
from utilities.google_utilities import State_transition_check
from utilities.helper_functions import *


def poi_retrieval(notion_token, notion_database_id):

    client = Client(auth=notion_token)

    # person_db_info = client.databases.retrieve(database_id=notion_database_id)

    # Write_dict_to_file_as_json(person_db_info, 'db_info.json')
    
    person_db_rows = Fetch_all_rows(client, notion_database_id)

    # Write_dict_to_file_as_json(person_db_rows, f'db_rows.json')
    
    simple_rows = []
    # block_companies = []

    for row in person_db_rows:

        
        company_block_ID = Safe_get(row, 'properties.Company_DB.relation.0.id')

        # have to execute a sub-query to get the actual company UUI
        block_info = client.blocks.retrieve(block_id=company_block_ID)
        # block_companies.append(block_info)
        
        company_UUI = Safe_get(block_info, 'child_page.title')
        name = Safe_get(row, 'properties.First_Last.rich_text.0.plain_text')
        email = Safe_get(row, 'properties.Email.rich_text.0.plain_text')
        telegram = Safe_get(row, 'properties.Telegram.rich_text.0.plain_text')
        other = Safe_get(row, 'properties.Other.rich_text.0.plain_text')
        poi_UUI = Safe_get(row, 'properties.POI_UUI.title.0.plain_text')
        
        

        simple_rows.append({
            'name' : name,
            'poi_UUI': poi_UUI,
            'email' : email,
            'telegram' : telegram,
            'other' : other,
            'company_UUI' : company_UUI
        })

    # needed the folder UUI

    # Write_dict_to_file_as_json(block_companies, 'person_company_block_info.json')
    State_transition_check(simple_rows,POI_FOLDER_ID, POI_LOCAL_STORE)

    return simple_rows

def POI_Folder_Creation_Changes():
    potential_store = poi_retrieval(NOTION_TOKEN, POI_NOTION_DB)

    # overwriting the simple_rows.json to change the state from the previous store to the new store. 
    Write_dict_to_file_as_json(potential_store, f'{POI_LOCAL_STORE}')