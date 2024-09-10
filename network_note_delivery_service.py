from notion_client import Client
from utilities.config import *
from utilities.helper_functions import *
from utilities.docx_utilities import *
from utilities.google_utilities import Note_delivery_to_google


# reading notion page and making it into a dict that will then be read by form_doc function and made into a docx then saved in "local" storage.
def create_simple_blocks_from_content(client, content):
    page_simple_blocks = []

    for block in content:
        block_id = block['id']
        block_type = block['type']
        has_children = block.get('has_children', False)
        rich_text = block.get(block_type, {}).get('rich_text')

        if block_type == 'table':
            # Handle table block by getting the children (rows)
            table_rows = Read_text(client, block_id)
            table_data = []

            for row in table_rows:
                if row['type'] == 'table_row':
                    
                    cells = row['table_row'].get('cells', [])
                    cell_texts = [cell[0]['text']['content'] for cell in cells if cell]  # Extract text from cells
                    table_data.append(cell_texts)
            
            simple_block = {
                'id': block_id,
                'type': block_type,
                'table_data': table_data
            }
        elif block_type == 'child_database':
            db_rows = client.databases.query(block_id)
            # idk if I need to query again here, but the child database is not in the "content.json" file.

            simple_rows = []

            for row in db_rows['results']:

                name = Safe_get(row, 'properties.Name.title.0.plain_text')
                tags = Safe_get(row, 'properties.Tags.select.name')
                date = Safe_get(row, 'properties.Date.date.start')
    
                simple_rows.append({
                    'name': name,
                    'tags': tags,
                    'date': date
                })
            # elif Safe_get(db_rows['results'][0], 'properties.Research.title.0.plain_text') == "Research":
            #     for row in db_rows['results']:
            #         name = Safe_get(row, 'properties.Research.title.0.plain_text')

            #         research_sources_block_ID = Safe_get(row, 'properties.Research_Sources_DB.relation.0.id')
            #         print("####",research_sources_block_ID)
            #         studying_block_ID = Safe_get(row, 'properties.Studying.relation.0.id')
                    
            #         # handling sub-query dependent on whether for relation within a note inline database for sources
            #         research_sources_block_info = client.blocks.retrieve(block_id=research_sources_block_ID)
            #         research_sources_block_info = Safe_get(research_sources_block_info, 'child_page.title')

            #         studying_block_info = client.blocks.retrieve(block_id=studying_block_ID)
            #         studying_block_info = Safe_get(studying_block_info, 'child_page.title')

        
            #         simple_rows.append({
            #             'name': name,
            #             'reasearch_sources': research_sources_block_info,
            #             'notes_sources': studying_block_info
            #         })

            simple_block = {
                'id': block_id,
                'type': block_type,
                'database_data': simple_rows
            }
        elif rich_text:
            # Handle regular text block
            plain_texts = [item['plain_text'] for item in rich_text]

            # Combine all plain_text values into a single string, separated by a comma
            combined_plain_text = ''.join(plain_texts)

            simple_block = {
                'id': block_id,
                'type': block_type,
                'text': combined_plain_text
            }
        elif block_type == 'image':
            if Safe_get(block,'image.type') == "file":
                simple_block = {
                'id': block_id,
                'type': block_type,
                'image_url': Safe_get(block,'image.file.url')
                }
            else:
                simple_block = {
                'id': block_id,
                'type': block_type,
                'image_url': Safe_get(block,'image.external.url')
                }                
                
        else:
            continue  # Skip blocks without rich_text, images, databases, or tables 

        # recursively call over children
        if has_children:
            nested_children = Read_text(client, block_id)  
            simple_block['children'] = create_simple_blocks_from_content(client, nested_children)

        page_simple_blocks.append(simple_block)

    return page_simple_blocks

# making the page names and location to save key value pairs to then pass the Note_delivery_to_google function, because that function will read the local store of files find the file by name and then save that file to the corresponding folder ID in the dict.  
def page_Transformation_Saving(notion_token, notion_database_id):

    client = Client(auth=notion_token)
    
    db_rows = client.databases.query(database_id=notion_database_id)

    page_ids = []
    page_names_and_folder = {}

    # want the page names to be keys and the value to be either the company or person UUI. 

    # finding all the pages
    # this part of the code needs to be refactored into helper functions.

    for row in db_rows['results']:

        page_ids.append(row['id'])

        if Safe_get(row,'properties.Meetings.title.0.plain_text') != None:

            page_name = Safe_get(row,'properties.Meetings.title.0.plain_text')

            poi_block_ID = Safe_get(row, 'properties.Person_Of_Interest_DB.relation.0.id')
            company_block_ID = Safe_get(row, 'properties.Company_DB.relation.0.id')

            # handling sub-query dependent on whether the note is a company note or a person note. If it is a company note then the person UUI will be None and vice versa. 
            if poi_block_ID != None:
                poi_block_info = client.blocks.retrieve(block_id=poi_block_ID)
                poi_block_info_UUI = Safe_get(poi_block_info, 'child_page.title')
                # print(poi_block_info_UUI)
                page_names_and_folder[page_name] = poi_block_info_UUI
                
            elif company_block_ID != None:
                company_block_info = client.blocks.retrieve(block_id=company_block_ID)
                company_block_info_UUI = Safe_get(company_block_info, 'child_page.title')
                # print(company_block_info_UUI)
                page_names_and_folder[page_name] = company_block_info_UUI

            else:
                continue
        elif Safe_get(row,'properties.Notes.title.0.plain_text') != None:

            page_name = Safe_get(row,'properties.Notes.title.0.plain_text')

            topics_block_ID = Safe_get(row, 'properties.Topics.relation.0.id')

            topics_block_info = client.blocks.retrieve(block_id=topics_block_ID)
            topics_block_info_UUI = Safe_get(topics_block_info, 'child_page.title')
            # print(poi_block_info_UUI)
            page_names_and_folder[page_name] = topics_block_info_UUI

        # have to execute a sub-query to get the actual company UUI
        

    # creating all the pages 
        
    for i in range(len(page_names_and_folder)):    
        notion_page_id = page_ids[i]
        doc_name = ''

        for index, key in enumerate(page_names_and_folder):
            if index == i:
                doc_name += key
                break

        content = Read_text(client, notion_page_id)

        # Write_dict_to_file_as_json(content, f'_notes_content{doc_name}.json')
        simple_blocks = create_simple_blocks_from_content(client, content)
        # Write_dict_to_file_as_json(simple_blocks, f'_notes_simple_blocks{doc_name}.json')

        Form_doc(simple_blocks,doc_name)


    return page_names_and_folder, page_ids

def Network_Note_Delivery_Service():

    print("sub-process running over company & POI notes DB")
    networking_page_names_and_folder, networking_page_ids = page_Transformation_Saving(NOTION_TOKEN, COMPANY_POI_NOTE_DB)
    Note_delivery_to_google(networking_page_names_and_folder, networking_page_ids)
    print("sub-process completed for company & POI notes DB")
    # print("####",networking_page_names_and_folder)

    # # run a second function for Note Library / studying DB
    print("sub-process running over note library for studying DB")
    library_page_names_and_folder, library_page_ids = page_Transformation_Saving(NOTION_TOKEN, NOTE_LIBRARY_NOTE_DB)
    Note_delivery_to_google(library_page_names_and_folder, library_page_ids)
    # print("####",library_page_names_and_folder)

    print("sub-process completed for note library in studying DB")
