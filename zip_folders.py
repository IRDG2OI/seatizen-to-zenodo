#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 14:31:46 2023

@author: g2oi
"""
import os
import argparse
import time
from datetime import datetime
from folders_preparation import list_directories
import zipfile

def unzip(zip_file_index, source_folder, destination_folder):
    zip_files = [file for file in os.listdir(source_folder) if file.endswith('.zip')]
    zip_files.sort()
    zip_file = zip_files[zip_file_index]
    zip_file_path = os.path.join(source_folder, zip_file)
    session_name = zip_file[:-4]
    destination_folder = os.path.join(destination_folder, session_name)
    os.makedirs(destination_folder, exist_ok=True)
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)
        
def zip_folders(session_index, source_folder, destination_folder):
    sessions = list_directories(source_folder)
    sessions.sort()
    session = sessions[session_index]
    session_path = os.path.join(source_folder, session)
    zip_filename = session + ".zip"
    zip_path = os.path.join(destination_folder, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the folder and add each file and subfolder to the ZIP file
        for root, dirs, files in os.walk(session_path):
            for file in files:
                file_path = os.path.join(root, file)
                # The second argument of 'zipf.write' is the relative path inside the ZIP
                zipf.write(file_path, os.path.relpath(file_path, session_path))
    

def main():
    start_time = time.time()
    print("========================================================")
    print(f"Start time: {datetime.now()}")
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-index",
                        action="store",
                        type=int,
                        default=1,
                        help="Index of the session that is being processed. Default: 1")
    args = parser.parse_args()
    session_index = args.session_index - 1
    
    #source_folder = '/home3/datawork/aboyer/mauritiusSessions/'
    source_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_zipped/'
    #destination_folder = '/home3/scratch/aboyer/zipSessions/'
    destination_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_unzipped/'
    
    
    if session_index < 84:
        #zip_folders(session_index, source_folder, destination_folder)
        unzip(session_index, source_folder, destination_folder)
                    
        execution_time_seconds = time.time() - start_time
        execution_time_minutes = "{:.2f}".format(execution_time_seconds / 60)
        print(f"\n{session} unzipped in {destination_folder} successfully.")
        print(f"\nEnd time: {datetime.now()}")
        print(f"Total execution time: {execution_time_minutes} minutes")
        print("========================================================\n")
        
if __name__ == '__main__':
    main()