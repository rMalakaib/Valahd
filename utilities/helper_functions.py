import json
from utilities.config import *
import os

# reading rich rext and returning block
def Write_text(client, page_id, text, type='paragraph'):
    client.blocks.children.append(
        block_id=page_id,
        children=[{
            "object": "block",
            "type": type,
            type: {
                "rich_text": [{ "type": "text", "text": { "content": text } }]
            }
        }]
    )

def Write_dict_to_file_as_json(content, file_name):
    content_as_json_str = json.dumps(content)

    with open(file_name, 'w') as f:
        f.write(content_as_json_str)

def Read_text(client, page_id):
    response = client.blocks.children.list(block_id=page_id)
    return response['results']

def Fetch_all_rows(client, notion_database_id):
    all_results = []
    next_cursor = None
    
    while True:
        # Include the start_cursor parameter only if there is a next_cursor
        query_params = {
            "start_cursor": next_cursor
        } if next_cursor else {}

        # Query the Notion database
        db_rows = client.databases.query(
            database_id=notion_database_id,
            **query_params
        )
        
        # Append the results to all_results
        all_results.extend(db_rows['results'])

        # Get the next cursor and check if there are more rows
        next_cursor = db_rows.get('next_cursor')
        has_more = db_rows.get('has_more')

        # Break the loop if no more rows
        if not has_more:
            break
    
    return all_results


# get data from in-page database
def Safe_get(data, dot_chained_keys):
    '''
        {'a': {'b': [{'c': 1}]}}
        safe_get(data, 'a.b.0.c') -> 1
    '''
    keys = dot_chained_keys.split('.')
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data

def Querying_folders(values_UUI, service):
    
    folder_id = ''
    for folder in FOLDER_LIST:
        
        query = f"'{folder}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        query_results = service.files().list(q=query, fields="files(id, name)").execute()
        query_file_results = query_results.get('files', [])

        for row in query_file_results:
            if values_UUI == row['name'].split(',')[1].strip(): 
                folder_id = row['id']
                break

# had to add in key pair between Values UUI, and Folder UUI because I fucked up with the structure of my JSONS which I explain in calendar APP halfway down the page. 
        if folder_id != '':
                
            break

        
    return folder_id
    # explanation:

       # if file doesn't exist find its folder and place it in there:
    
    # p_query = f"'{POI_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    # p_query_results = service.files().list(q=p_query, fields="files(id, name)").execute()

    # poi_folders = p_query_results.get('files', [])

    # c_query = f"'{COMPANY_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    # c_query_results = service.files().list(q=c_query, fields="files(id, name)").execute()


    # company_folders = c_query_results.get('files', [])

    # l_query = f"'{NOTE_LIBRARY_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    # l_query_results = service.files().list(q=l_query, fields="files(id, name)").execute()

    # library_folders = l_query_results.get('files', [])




    # # print("Page Name & Block Info :", page_name, page_names_and_folder[page_name])
    # folder_id = ''
    # # have to search the company db first because it only has the UUI for the company not both the company and person. 
    # # if it doesn't find the UUI in the company folder it assumes the note goes into the person folder or library folder. 
    
    # for row in company_folders:
    #     if values_UUI == row['name'].split(',')[1].strip(): 
    #         # print("company_value_UUI", values_UUI, " row_name:", row['name'].split(',')[1].strip())
    #         folder_id = row['id']
    #         break


    #         # pretty certain i can remove the [5] block of code and or statement 
    # for row in poi_folders:
    #     if values_UUI == row['name'].split(',')[1].strip():
    #         # print("poi_value_UUI", values_UUI, " row_name:", row['name'].split(',')[1].strip())
    #         folder_id = row['id']
    #         break

    # for row in library_folders:
    #     if values_UUI == row['name'].split(',')[1].strip():
    #         # print("library_value_UUI", values_UUI, " row_name:", row['name'].split(',')[1].strip())
                
    #             # print("ROW ID:", row['id'])
    #         folder_id = row['id']
    #         break
    
    

    