#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 14:48:10 2023

@author: g2oi
"""

'''
Use this script in copy_folders.pbs to parallelize the copy of the sessions you want to process.
Fill source_folder and destination_folder in the main() function with the path to the original sessions and the path to where you want to copy them. 
'''

import os
import shutil
import argparse
import time
from datetime import datetime
from folders_preparation import list_directories
import pandas as pd

def copy_folder_to_folder(source_folder, destination_folder, session_index):
    '''
    Function to copy a full folder (subfolders included) to another folder.
    '''
    start_time = time.time()
    print("========================================================")
    print(f"Start time: {datetime.now()}")
    sessions = list_directories(source_folder)
    # sessions = [file for file in os.listdir(source_folder) if file.endswith('.zip')]
    sessions.sort()
    session = sessions[session_index]
    destination_folder = os.path.join(destination_folder, session)
    session_path = os.path.join(source_folder, session)

    if os.path.exists(destination_folder):
        print(f"{session} already copied.\n")
        print("========================================================\n")
    else:
        shutil.copytree(session_path, destination_folder)
        # shutil.copy(session_path, destination_folder) # zip copy
        execution_time_seconds = time.time() - start_time
        execution_time_minutes = "{:.2f}".format(execution_time_seconds / 60)
        print(f"\n{session} copy in {destination_folder} successfull.")
        print(f"\nEnd time: {datetime.now()}")
        print(f"Total execution time: {execution_time_minutes} minutes")
        print("========================================================\n")

def copy_path_to_folder(csv_path, image_folder, destination_folder):
    '''
    Function to resize and copy images listed in a column "Image_path" of a CSV file to a destination folder.
    ### Input: 
        - csv file
    ### Output:
        - images copied to destination folder
    '''
    df = pd.read_csv(csv_path)
    # os.makedirs(destination_folder, exist_ok=True)

    # [Retraining of grass kelly] Selection of images that starts with G0 and class is useful
    df = df[(df['image'].str.startswith('G0')) & (df['class'] == 'useful')]
    df = df.reset_index(drop=True)

    for index, row in df.iterrows():
        # image_path = row['Image_path']
        image_name = row['image']
        image_path = os.path.join(image_folder, image_name)
        # image_name = os.path.basename(image_path)
        destination_path = os.path.join(destination_folder, image_name)

        try:
            shutil.copy(image_path, destination_path)
            print(f"Copied {image_path} to {destination_path}")
        except Exception as e:
            print(f"Failed to copy {image_path}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-index",
                        action="store",
                        type=int,
                        default=1,
                        help="Index of the session that is being processed. Default: 1")
    args = parser.parse_args()
    session_index = args.session_index - 1

    source_folder = '' # original sessions
    destination_folder = '' # copy destination

    copy_folder_to_folder(source_folder, destination_folder, session_index)


if __name__ == '__main__':
    main()