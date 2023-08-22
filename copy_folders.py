#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 14:48:10 2023

@author: g2oi
"""

import os
import shutil
import argparse
import time
from datetime import datetime
from folders_preparation import list_directories

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
    
    #source_folder = '/home/datawork-iot-nos/Seatizen/mauritius_use_case/Mauritius/162.38.140.205/Deep_mapping/backup/validated'
    # source_folder = '/home3/scratch/aboyer/zipSessions'
    source_folder = '/home3/datawork/aboyer/mauritiusSessionsOutput/useless_images'
    sessions = list_directories(source_folder)
    # sessions = [file for file in os.listdir(source_folder) if file.endswith('.zip')]
    sessions.sort()
    session = sessions[session_index]
    #destination_folder = os.path.join('/home3/datawork/aboyer/mauritiusSessions', session)
    # destination_folder = os.path.join('/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/zipped_sessions', session)
    destination_folder = os.path.join('/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_processing_output/useless_images', session)
    session_path = os.path.join(source_folder, session)

    if session_index < 84:
        if os.path.exists(destination_folder):
            print(f"{session} already copied.\n")
            print("========================================================\n")
        else:
            shutil.copytree(session_path, destination_folder)
            # shutil.copy(session_path, destination_folder)
            execution_time_seconds = time.time() - start_time
            execution_time_minutes = "{:.2f}".format(execution_time_seconds / 60)
            print(f"\n{session} copy in {destination_folder} successfull.")
            print(f"\nEnd time: {datetime.now()}")
            print(f"Total execution time: {execution_time_minutes} minutes")
            print("========================================================\n")

if __name__ == '__main__':
    main()