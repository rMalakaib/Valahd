from Company_folder_creation import Company_Folder_Creation_Changes
from POI_folder_creation import POI_Folder_Creation_Changes
from Note_library_folder_creation import Note_Library_Folder_Creation_Changes
from network_note_delivery_service import Network_Note_Delivery_Service
from calendar_app import Calendar_app
import datetime


def timestamp_cron_tab():
    with open("/Users/malakai/Code/Notion/local/cron_test.log", "a") as log_file:
        log_file.write("Script executed at " + str(datetime.datetime.now()) + "\n")


def main():
    # run all logic to handle new companies in company DB in notion and also state changes then update local store of company DB
    print("company folders are being reviewed...")
    Company_Folder_Creation_Changes()
    print("company folders have been created and updated")

    # run all logic to handle new persons of interest in person DB in notion and also state changes then update local store of person DB
    print("poi folders are being reviewed...")
    POI_Folder_Creation_Changes()
    print("poi folders have been created and updated")


    # run all logic to handle new notes in Note Library DB (Topics is actual name) in notion and also state changes then update local store of person DB
    print("note library folders are being reviewed...")
    Note_Library_Folder_Creation_Changes()
    print("note library folders have been created and updated")
     
    # run all logic looping over note's DB then form those docx files and place them into local folder. After run note delivery service to google and then delete all docx files in local store.
    print("notes are beginning transformation process and delivery")
    Network_Note_Delivery_Service()
    print("notes have been devivered", "\n")


    print("reading your calendar and gathering notes")
    Calendar_app()
    print("emails have been sent!")

    
    timestamp_cron_tab()




main()