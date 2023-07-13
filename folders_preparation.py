#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:04:46 2023

@author: g2oi
"""

from jacques.inference import predictor
from jacques.inference import output
import os
import pandas as pd
import shutil

# checkpoint path
# ckpt_path = 'model_checkpoint_v0.ckpt'
# ckpt_path = 'epoch=7-step=2056.ckpt'
ckpt_path = 'epoch=8-step=1412.ckpt'

# get folder list that contains images (['DCIM/100GOPRO/', 'DCIM/101GOPRO/'])
def get_subfolders(folder_path):
    subfolders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path) and 'GOPRO' in item:
            subfolder_name = f"DCIM/{os.path.basename(item_path)}/"
            subfolders.append(subfolder_name)
    return subfolders

# Delete "BEFORE" and "AFTER" folders at specified path if they exists
def delete_folders(path):
    before_path = os.path.join(path, 'BEFORE')
    after_path = os.path.join(path, 'AFTER')

    # Check if "BEFORE" folder exists and delete it
    if os.path.exists(before_path) and os.path.isdir(before_path):
        shutil.rmtree(before_path)
        print(f'Deleted folder: {before_path}')

    # Check if "AFTER" folder exists and delete it
    if os.path.exists(after_path) and os.path.isdir(after_path):
        shutil.rmtree(after_path)
        print(f'Deleted folder: {after_path}')

# return the list of sessions
def get_sessions_list(sessions):
    if(isinstance(sessions, str)): # if it's a string, it's one directory
        # list sessions automatically from one directory
        directory_of_sessions = sessions
        list_of_sessions = os.listdir(directory_of_sessions)
        list_of_sessions = [os.path.join(directory_of_sessions, session) for session in list_of_sessions]
    elif(isinstance(sessions, list)): # if it's a list, sessions are written by hand
        list_of_sessions = sessions
    
    return list_of_sessions

# move back useless images to their original folders
def move_back_images(csv_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        image_path = 'useless/' + row['dir'].split('/')[1] + '_useless_images/' + row['image']
        image_class = row['class']
        original_dir = row['dir']
    
        # Check if the image class is 'useless'
        if image_class == 'useless':
            # Create the original directory if it doesn't exist
            # os.makedirs(original_dir, exist_ok=True)
            # Move the image back to its original directory
            shutil.move(image_path, original_dir)
    
            # Display the operation for confirmation
            print(f"Moved image '{image_path}' back to '{original_dir}'.")

def classify_sessions(sessions):
    '''
    Function that uses jacques predicator classify_useless_images function to classify given sessions images.
    # Input:
        - sessions: 
            ## can be a string that refer to a single directory that contains 
            every sessions (ex: 'sessions/')
            ## can be a list of the desired sessions (ex: ['sessions/session_2017_11_05_kite_Le_Morne'])
    # Output:
        - a dataframe that contains the classification result for the selected sessions images
        
    '''
    list_of_sessions = get_sessions_list(sessions)
    
    # classification of useful and useless images of all sessions
    results_of_all_sessions = pd.DataFrame(columns = ['dir', 'image', 'class'])
    for session in list_of_sessions:
        print("----------------------------------------")
        print(session)
        print("----------------------------------------")
        list_of_dir = get_subfolders(f'{session}/DCIM/')
        for directory in list_of_dir:
            print('\n' + directory)
            results = predictor.classify_useless_images(folder_path=os.path.join(session, directory),
                                                        ckpt_path=ckpt_path)
            results_of_all_sessions = pd.concat([results_of_all_sessions, results], axis=0, ignore_index=True)
    return results_of_all_sessions

def restructure_sessions(sessions, dest_path, csv_path):
    '''
    Function to restructure sessions folders to be "Zenodo ready"
    # Input:
        - sessions:
            ## the list of sessions:
                either a single directory that contains every sessions (ex: 'sessions/')
                or a list of sessions path (ex: ['sessions/session_2017_11_19_paddle_Black_Rocks'])
        - dest_path:
            ## destination path where useless images will me moved (ex: 'useless/session_2017_11_19_paddle_Black_Rocks_useless_images/')
        - csv_path:
            ## path where classification result csv will be written (ex: 'filters/session_2017_11_19_paddle_Black_Rocks.csv')
    # Output:
        - sessions folders "Zenodo ready"
    '''
    # classification
    results_of_all_sessions = classify_sessions(sessions)
    
    # move useless images
    output.move_images(results_of_all_sessions,
               dest_path = dest_path,
               who_moves = 'useless',
               copy_or_cut = 'cut'
               )
    print(f'\nUseless images moved to {dest_path}')
    
    # export results to csv file
    suffix = f"_jacques-v0.2.1_model-{ckpt_path.split('.')[0]}" # adding jacques version and classification model version to csv filename
    csv_path = csv_path[:-4] + suffix + csv_path[-4:]
    results_of_all_sessions.to_csv(csv_path, index = False, header = True)
    print(f'\nClassification informations written at {csv_path}')
    
    # delete BEFORE and AFTER folders if they exists
    list_of_sessions = get_sessions_list(sessions)
    for session in list_of_sessions:
        deletion_path =f'{session}/DCIM/'
        delete_folders(deletion_path)
    
    # to-do:
        # renommage des repertoires en fonction args fonction (si renseigné -> renommage)
  
# sessions = 'test/'
sessions = ['sessions/session_2017_11_19_paddle_Black_Rocks']
dest_path = 'useless/session_2017_11_19_paddle_Black_Rocks_useless_images/'
csv_path = 'filters/session_2017_11_19_paddle_Black_Rocks.csv'

restructure_sessions(sessions, dest_path, csv_path)
