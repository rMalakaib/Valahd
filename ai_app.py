# prompt: return me all the notes on company x
# prompt: return me all the notes on person y

import json

# Temporary solution to long term problem

# read all data from company simple rows and extract company name and UUI
# read all data from person simple rows and extract person name and UUI
# pass all data.

# prompt: if {prompt} is "return all the notes on company x" where x is the companies name or "return all the notes on person y" where y is the persons name, then search the below data bases to find company x's or person y's corresponding UUI. Once found return only the UUI of company x or person y. There should only be one UUI.
# if not {prompt} then return only the text "None"

# sort through actual notes and return the links to the files.
from googleapiclient.discovery import build
from google.oauth2 import service_account
from utilities.google_utilities import Get_file_link
from utilities.config import *
import openai

openai.api_key = 'sk-proj-AxzbiWdmBtltxZYAqa9CT3BlbkFJ0Dbx6MSBK6MdeHt39zah'
# MODEL="gpt-4o"
# MODEL="gpt-4-turbo"
MODEL="gpt-3.5-turbo"


def read_company_table():

    extracted_company_table = []

    with open(COMPANY_LOCAL_STORE, 'r') as company_table:
        for row in json.load(company_table):

            data = {
                'company_name' : row.get("company"),
                'company_UUI' : row.get("company_UUI")
            }

            extracted_company_table.append(data)
    
    
    return json.dumps(extracted_company_table)

# context lenth, and generalized versus specific AI. 

def read_person_table():

    extracted_person_table = []

    with open(POI_LOCAL_STORE, 'r') as person_table:
        for row in json.load(person_table):

            data = {
                'person_name' : row.get("name"),
                'person_UUI' : row.get("poi_UUI")
            }

            extracted_person_table.append(data)
    
    
    return json.dumps(extracted_person_table)

def read_studying_table():

    extracted_studying_table = []

    with open(NOTE_LIBRARY_LOCAL_STORE, 'r') as studying_table:
        for row in json.load(studying_table):

            data = {
                'topic_name' : row.get("topic"),
                'studying_UUI' : row.get("note_UUI")
            }

            extracted_studying_table.append(data)
    
    
    return json.dumps(extracted_studying_table)


def prompt_handling(user_prompt, company_data, person_data, studying_data):
            
    system_prompt_1 = f'''if user_prompt is "return all the notes on company x" where x is the companies name or "return all the notes on person y" where y is the persons name, then search the below data bases to find company x's or person y's corresponding UUI. Once found return only the UUI of company x or person y. There should only be one UUI returned.
    
    if not then return only the text "None
    
    Company Data: {company_data}
    '''

# had to break up search because of context length requirements
    system_prompt_2 = f'''if user_prompt is "return all the notes on person y" where y is the persons name, then search the below data base to find person y's corresponding UUI. Once found, return only the UUI of person y. There should only be one UUI returned.
    
    if not then return only the text "None"
    
    Person Data: {person_data}
    '''

# had to break up search because of context length requirements
    system_prompt_3 = f'''if user_prompt is "return all the notes on topic z" where z is the notes name, then search the below data base to find notes z's corresponding UUI. Once found, return only the UUI of notes z. There should only be one UUI returned.
    
    if not then return only the text "None"
    
    Studying Data: {studying_data}
    '''

    # for segment in data:
        # Call the ChatGPT API

    system_prompts = [system_prompt_1, system_prompt_2, system_prompt_3]
    
    message_response = "None"

    while message_response == "None":

        for system_prompt in system_prompts:



            response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            local_message_response = response.choices[0].message.content

            if local_message_response != "None":
                message_response = response.choices[0].message.content

            if system_prompts.index(system_prompt) == len(system_prompts)-1:
                return message_response

    return message_response

def retrieving_file_data(files_uui):

    link_credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive.readonly'])
    
    link_service = build('drive', 'v3', credentials=link_credentials)

    retrieved_data = []

    with open(FILE_NAME_FOLDER_AND_ID_LOCAL_STORE, 'r') as notes:
        
        for row in json.load(notes):
            
            if files_uui in row["database_id"]:
                
                file_link = Get_file_link(row.get("file_id"),link_service)
                

                data = {
                'page_name' : row.get("page_name"),
                'file_link' : file_link
                }

                retrieved_data.append(data)
                
                



    return retrieved_data

# if has uui 
# get name
# query for file link
# return dict of name and file link


def main():
    user_prompt = input("please return ask to \"return all the notes on company x\" where x is the companies name \n or \"return all the notes on person y\" where y is the person's name \n or \"return all the notes on topic z\" where z is the notes name: ")
    company_data = read_company_table()
    person_data = read_person_table()
    studying_data = read_studying_table()

    uui = prompt_handling(user_prompt, company_data, person_data, studying_data)

    retrieved_data = retrieving_file_data(uui)

    for row in retrieved_data:
        print(f"{row} \n")

main()