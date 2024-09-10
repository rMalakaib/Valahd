from notion_client import Client
from utilities.config import *
from utilities.google_utilities import State_transition_check
from utilities.helper_functions import *

def company_retrieval(notion_token, notion_database_id):

    client = Client(auth=notion_token)

    # company_db_info = client.databases.retrieve(database_id=notion_database_id)

    
    
    company_db_rows = Fetch_all_rows(client, notion_database_id)
    
    simple_rows = []

    for row in company_db_rows:
        
        company = Safe_get(row, 'properties.Company.rich_text.0.plain_text')
        company_UUI = Safe_get(row, 'properties.Company_UUI.title.0.plain_text')
        email_domain = Safe_get(row, 'properties.Email_Domain.rich_text.0.plain_text')

        simple_rows.append({
            'company' : company,
            'company_UUI': company_UUI,
            'email_domain' : email_domain
        })

        # needed the folder UUI

    State_transition_check(simple_rows, COMPANY_FOLDER_ID, COMPANY_LOCAL_STORE)


    return simple_rows


def Company_Folder_Creation_Changes():
    
    potential_store = company_retrieval(NOTION_TOKEN, COMPANY_NOTION_DB)

    # overwriting the simple_rows.json to change the state from the previous store to the new store. 
    Write_dict_to_file_as_json(potential_store, f'{COMPANY_LOCAL_STORE}')


