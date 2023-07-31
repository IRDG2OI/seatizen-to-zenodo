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
import torch
import argparse
import time
from datetime import datetime
import glob

# checkpoint path
# jacques_ckpt_path = 'model_checkpoint_v0.ckpt'
# jacques_ckpt_path = 'epoch=8-step=1412.ckpt'
#jacques_ckpt_path = 'epoch=7-step=2056.ckpt'
jacques_ckpt_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/models/epoch=7-step=2056.ckpt'
#multilabel_ckpt_path = 'multilabel_with_sable.pth'
multilabel_ckpt_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/models/multilabel_with_sable.pth'

# get folder list that contains images (['DCIM/100GOPRO/', 'DCIM/101GOPRO/'])
def get_subfolders(folder_path):
    subfolders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path) and 'GOPRO' in item:
            subfolder_name = f"DCIM/{os.path.basename(item_path)}"
            subfolders.append(subfolder_name)
    return subfolders

# List ONLY directories
def list_directories(path):
    directories = [entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))]
    return directories

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
def get_sessions_list(sessions, session_index):
    if(isinstance(sessions, str)): # if it's a string, it's one directory
        # list sessions automatically from one directory
        directory_of_sessions = sessions
        list_of_sessions = list_directories(directory_of_sessions)
        list_of_sessions = [os.path.join(directory_of_sessions, session) for session in list_of_sessions]
        list_of_sessions.sort()
        list_of_sessions = [list_of_sessions[session_index]]
    elif(isinstance(sessions, list)): # if it's a list, sessions are written by hand
        list_of_sessions = [sessions[session_index]]
    
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

# merge multilabel annotations csv with GPS metadata (latitude, longitude and date)
def join_GPS_metadata(annotation_csv_path, gps_info_csv_path, merged_csv_path):
    annot_df = pd.read_csv(annotation_csv_path)
    gps_df = pd.read_csv(gps_info_csv_path)
    
    # Extract image names from the file paths
    annot_df['Image_name'] = annot_df['Image_path'].str.split('/').str[-1]
    gps_df['Image_name'] = gps_df['photo_relative_file_path'].str.split('/').str[-1]
    
    # Merge the DataFrames based on the image names
    merged_df = annot_df.merge(gps_df[['Image_name', 'decimalLatitude', 'decimalLongitude', 'GPSDateTime']],
                               on='Image_name', how='left')
    
    # Drop the 'Image_name' column from merged_df
    merged_df.drop(columns='Image_name', inplace=True)
    
    # Swapping latitude and longitude
    merged_df = merged_df.rename(columns = {'decimalLatitude':'decimalLongitude', 'decimalLongitude':'decimalLatitude'})
    
    merged_df.to_csv(merged_csv_path, index=False, header=True)

# apply probabilities thresholds to the values of multilabel annotations
def apply_thresholds(merged_csv_path, thresholds_csv_path, final_csv_path):
    df_1 = pd.read_csv(merged_csv_path)
    df_2 = pd.read_csv(thresholds_csv_path)
    
    for column in df_1.columns:
        if column in df_2.columns:
            threshold_value = df_2[column][0]
            df_1[column] = df_1[column].apply(lambda x: 1 if x > threshold_value else 0)
            
    df_1.to_csv(final_csv_path, index=False, header=True)
    
# filter out useless images in the final csv based on jacques classification csv
def filter_useless_images(classification_csv, final_csv_path):
    df_1 = pd.read_csv(classification_csv)
    df_2 = pd.read_csv(final_csv_path)
    
    # Extract image name from image path
    df_2['image'] = df_2['Image_path'].str.split('/').str[-1]
    
    # Filter out the 'useless' images from the df_1
    df1_useful = df_1[df_1['class'] == 'useful']
    
    # Merge the two DF on the 'image' column and keep only rows that exist in both DF
    final_df = pd.merge(df_2, df1_useful, on='image', how='inner')
    
    # Removing useless columns
    final_df = final_df.drop(columns=['dir', 'class', 'image'])
    
    final_csv_path = final_csv_path[:-4] + '_filtered' + final_csv_path[-4:]
    
    final_df.to_csv(final_csv_path, index=False, header=True)

# merge all final csv files ending with 'filtered' located at csv_path in one csv file
def merge_all_final_csv(csv_path):
    directory_path = os.path.dirname(csv_path)
    wildcard_pattern = os.path.join(directory_path, '*filtered.csv')
    file_list = glob.glob(wildcard_pattern)
    
    dfs = []
    
    for file in file_list:
        df = pd.read_csv(file)
        dfs.append(df)
    
    merged_df = pd.concat(dfs, ignore_index=True)
    
    merged_df.sort_values(by='Image_path', inplace=True)
    
    merged_csv_path = os.path.join(directory_path, 'all_sessions_data.csv')
    
    merged_df.to_csv(merged_csv_path, index=False, header=True)
    

def classify_sessions(sessions, session_index):
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
    list_of_sessions = get_sessions_list(sessions, session_index)
    
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

def restructure_sessions(sessions, session_index, dest_path, class_path, annot_path, output_txt_path, merged_csv_path, thresholds_csv_path, final_csv_path):
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
            ## path where a txt file will be created to monitor multilabel annotations progression. (ex: 'results_txt/output_.txt')
        - merged_csv_path:
            ## path where annotation csv will be merged with gps infos to create a new csv (ex: 'results_csv/merged_.csv')
        - thresholds_csv_path:
            ## path where the csv with thresholds values is located
        - final_csv_path:
            ## path of the final csv
    # Output:
        - sessions folders "Zenodo ready"
    '''
    temp_path = output_txt_path[:-4] + sessions[0].split('/')[-1] + output_txt_path[-4:]
    file = open(temp_path, "a+")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    file.write("Jacques classification started on %s \r\n" %device)
    file.close()
    
    # classification
    results_of_all_sessions = classify_sessions(sessions, session_index)
    
    # move useless images
    #output.move_images(results_of_all_sessions,
    #           dest_path = dest_path,
    #           who_moves = 'useless',
    #           copy_or_cut = 'cut'
    #           )
    #print(f'\nUseless images moved to {dest_path}')
    
    list_of_sessions = get_sessions_list(sessions, session_index)
    
    # operations on each session
    for session in list_of_sessions: 
        # export results to csv file
        model = jacques_ckpt_path.split('/')[-1]
        session_name = session.split('/')[-1]
        # adding session name, jacques version and classification model version to csv filename
        suffix = f"{session_name}_jacques-v0.1.0_model-{model.split('.')[0]}"
        class_path = class_path[:-4] + suffix + class_path[-4:]
        results_of_all_sessions.to_csv(class_path, index = False, header = True)
        print(f'\nClassification informations written at {class_path}\n')
        
        df = pd.DataFrame(columns=['Image_path',"Acropore_branched", "Acropore_digitised", "Acropore_tabular", "Algae_assembly", 
                   "Algae_limestone", "Algae_sodding", "Dead_coral", "Fish", "Human_object",
                   "Living_coral", "Millepore", "No_acropore_encrusting", "No_acropore_massive",
                  "No_acropore_sub_massive",  "Rock", "Sand",
                   "Scrap", "Sea_cucumber", "Syringodium_isoetifolium",
                   "Thalassodendron_ciliatum",  "Useless"])
        
        path =f'{session}/DCIM/'
        
        # delete BEFORE and AFTER folders if they exists
        #delete_folders(path)
        
        output_txt_path = output_txt_path[:-4] + session_name + output_txt_path[-4:]
        final_csv_path = final_csv_path[:-4] + session_name + final_csv_path[-4:]
        
        # adding multilabel annotations
        list_of_dir = get_subfolders(path)
        for directory in list_of_dir:
            print(f"\nMultilabel annotations of images located in {directory}...")
            images_path = os.path.join(session, directory)
            df = write_csv(df, images_path, multilabel_ckpt_path, output_txt_path)
        
        annot_path = annot_path[:-4] + session_name + annot_path[-4:]
        df.to_csv(annot_path, index = False, header = True)
        print(f'\nAnnotations CSV of {session} successfully created at {annot_path}\n')
        
        # join GPS metadata to annotation file
        gps_info_csv_path = f'{session}/GPS/photos_location_{session_name}.csv'
        merged_csv_path = merged_csv_path[:-4] + session_name + merged_csv_path[-4:]
        join_GPS_metadata(annot_path, gps_info_csv_path, merged_csv_path)
        print(f'Merged GPS metadata with multilabel annotations at {merged_csv_path}\n')
        
        # apply thresholds
        apply_thresholds(merged_csv_path, thresholds_csv_path, final_csv_path)
        print(f'Applied thresholds to {merged_csv_path}.\nFinal CSV created at {final_csv_path}\n')
        
        # filtering out useless images
        filter_useless_images(class_path, final_csv_path)
        print(f'Filtered out useless images from {final_csv_path}\n')
            
        
def main():
    start_time = time.time()
    print(f"Start time: {datetime.now()}")
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-index",
                        action="store",
                        type=int,
                        default=1,
                        help="Index of the session that is being processed. Default: 1")
    args = parser.parse_args()
    session_index = args.session_index - 1
    print(f"In main, session_index = {session_index}")
    
    sessions = '/home/datawork-iot-nos/Seatizen/mauritius_use_case/Mauritius/162.38.140.205/Deep_mapping/backup/validated/'
    dest_path = ''
    class_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_csv/.csv'
    annot_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_csv/annotations_.csv'
    output_txt_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_txt/output_.txt'
    merged_csv_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_csv/merged_.csv'
    thresholds_csv_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/multilabel_annotation_thresholds.csv'
    final_csv_path = '/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_csv/final_.csv'

    #sessions = ['sessions/session_2017_11_18_paddle_Prairie']
    #dest_path = ''
    #class_path = 'results_csv/session_2017_11_18_paddle_Prairie.csv'
    #annot_path = 'results_csv/annotations_.csv'
    #output_txt_path = 'results_txt/output_.txt'
    #merged_csv_path = 'results_csv/merged_.csv'
    #thresholds_csv_path = 'multilabel_annotation_thresholds.csv'
    #final_csv_path = 'results_csv/final_.csv'
    
    if session_index < 10:
        restructure_sessions(sessions, session_index, dest_path, class_path, annot_path, output_txt_path, merged_csv_path, thresholds_csv_path, final_csv_path)
        execution_time = "{:.2f}".format(time.time() - start_time)
        print("\n========================================================")
        print(f"\nEnd time: {datetime.now()}")
        print(f"Total execution time: {execution_time}s")

if __name__ == '__main__':
    main()