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
    
    source_folder = '/home3/datawork/aboyer/mauritiusSessions/'
    destination_folder = '/home3/scratch/aboyer/zipSessions/'
    
    sessions = list_directories(source_folder)
    sessions.sort()
    session = sessions[session_index]
    session_path = os.path.join(source_folder, session)
    zip_filename = session + ".zip"
    zip_path = os.path.join(destination_folder, zip_filename)
    
    
    if session_index < 42:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the folder and add each file and subfolder to the ZIP file
            for root, dirs, files in os.walk(session_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # The second argument of 'zipf.write' is the relative path inside the ZIP
                    zipf.write(file_path, os.path.relpath(file_path, session_path))
                    
        execution_time_seconds = time.time() - start_time
        execution_time_minutes = "{:.2f}".format(execution_time_seconds / 60)
        print(f"\n{session} zipped in {destination_folder} successfully.")
        print(f"\nEnd time: {datetime.now()}")
        print(f"Total execution time: {execution_time_minutes} minutes")
        print("========================================================\n")
        
if __name__ == '__main__':
    main()