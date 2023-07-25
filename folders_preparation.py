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
from test_multilabel import write_csv

# checkpoint path
# jacques_ckpt_path = 'model_checkpoint_v0.ckpt'
# jacques_ckpt_path = 'epoch=8-step=1412.ckpt'
jacques_ckpt_path = 'epoch=7-step=2056.ckpt'
# jacques_ckpt_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/models/epoch=7-step=2056.ckpt'
multilabel_ckpt_path = 'multilabel_with_sable.pth'
# multilabel_ckpt_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/models/multilabel_with_sable.pth'

# get folder list that contains images (['DCIM/100GOPRO/', 'DCIM/101GOPRO/'])
def get_subfolders(folder_path):
    subfolders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path) and 'GOPRO' in item:
            subfolder_name = f"DCIM/{os.path.basename(item_path)}"
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
        print("-----------------------------------------------")
        print(session)
        print("-----------------------------------------------")
        list_of_dir = get_subfolders(f'{session}/DCIM/')
        for directory in list_of_dir:
            print('\n' + directory)
            results = predictor.classify_useless_images(folder_path=os.path.join(session, directory), ckpt_path=jacques_ckpt_path)
            results_of_all_sessions = pd.concat([results_of_all_sessions, results], axis=0, ignore_index=True)
    return results_of_all_sessions

def restructure_sessions(sessions, dest_path, class_path, annot_path, output_txt_path):
    '''
    Function to restructure sessions folders to be "Zenodo ready"
    # Input:
        - sessions:
            ## the list of sessions:
                either a single directory that contains every sessions. (ex: 'sessions/')
                or a list of sessions path (ex: ['sessions/session_2017_11_19_paddle_Black_Rocks'])
        - dest_path:
            ## destination path where useless images will me moved. (ex: 'useless/session_2017_11_19_paddle_Black_Rocks_useless_images/')
        - class_path:
            ## path where classification result csv will be written. (ex: 'results_csv/classifications_results.csv')
        - annot_path:
            ## path where multilabel annotations csv will be created. (ex: 'results_csv/annotations_.csv')
        - output_txt_path:
            ## folder path where a txt file will be created to monitor multilabel annotations progression. (ex: 'results_txt/output_.txt')
    # Output:
        - sessions folders "Zenodo ready"
    '''
    # classification
    results_of_all_sessions = classify_sessions(sessions)
    
    # move useless images
    #output.move_images(results_of_all_sessions,
    #           dest_path = dest_path,
    #           who_moves = 'useless',
    #           copy_or_cut = 'cut'
    #           )
    #print(f'\nUseless images moved to {dest_path}')
    
    # export results to csv file
    suffix = f"_jacques-v0.2.1_model-{jacques_ckpt_path.split('.')[0]}" # adding jacques version and classification model version to csv filename
    class_path = class_path[:-4] + suffix + class_path[-4:]
    results_of_all_sessions.to_csv(class_path, index = False, header = True)
    print(f'\nClassification informations written at {class_path}\n')
    
    list_of_sessions = get_sessions_list(sessions)
    # operations on each session
    for session in list_of_sessions: 
        df = pd.DataFrame(columns=['Image_path',"Acropore_branched", "Acropore_digitised", "Acropore_tabular", "Algae_assembly", 
                   "Algae_limestone", "Algae_sodding", "Dead_coral", "Fish", "Human_object",
                   "Living_coral", "Millepore", "No_acropore_encrusting", "No_acropore_massive",
                  "No_acropore_sub_massive",  "Rock", "Sand",
                   "Scrap", "Sea_cucumber", "Syringodium_isoetifolium",
                   "Thalassodendron_ciliatum",  "Useless"])
        
        path =f'{session}/DCIM/'
        
        # delete BEFORE and AFTER folders if they exists
        #delete_folders(path)
        
        session_name = session.split('/')[-1]
        output_txt_path = output_txt_path[:-4] + session_name + output_txt_path[-4:]
        
        # adding multilabel annotations
        list_of_dir = get_subfolders(path)
        for directory in list_of_dir:
            print(f"\nMultilabel annotations of images located in {directory}...")
            images_path = os.path.join(session, directory)
            df = write_csv(df, images_path, multilabel_ckpt_path, output_txt_path)
        
        annot_path = annot_path[:-4] + session_name + annot_path[-4:]
        df.to_csv(annot_path, index = False, header = True)
        print(f'\nAnnotations CSV of {session} successfully created at {annot_path}\n')
            
            
    
    # to-do:
        # renommage des repertoires en fonction args fonction (si renseigné -> renommage)


# sessions = ['/home/datawork-iot-nos/Seatizen/mauritius_use_case/Mauritius/162.38.140.205/Deep_mapping/backup/validated/session_2017_11_18_paddle_Prairie']
# dest_path = ''
# class_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_csv/session_2017_11_18_paddle_Prairie.csv'
# annot_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_csv/annotations_.csv'
# output_txt_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_txt/output_.txt'

sessions = ['sessions/session_2017_11_18_paddle_Prairie']
dest_path = ''
class_path = 'results_csv/session_2017_11_18_paddle_Prairie.csv'
annot_path = 'results_csv/annotations_.csv'
output_txt_path = 'results_txt/output_.txt'

restructure_sessions(sessions, dest_path, class_path, annot_path, output_txt_path)
