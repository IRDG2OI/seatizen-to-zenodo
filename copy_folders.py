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
import pandas as pd
from PIL import Image

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
            # image = Image.open(image_path)
            # # Resize the images where shortest side is 256 pixels, keeping aspect ratio. 
            # if image.width > image.height: 
            #     factor = image.width/image.height
            #     image = image.resize(size=(int(round(factor*256,0)),256))
            # else:
            #     factor = image.height/image.width
            #     image = image.resize(size=(256, int(round(factor*256,0))))
            # # Crop out the center 224x224 portion of the image.

            # image = image.crop(box=((image.width/2)-112, (image.height/2)-112, (image.width/2)+112, (image.height/2)+112))

            # image.save(destination_path)
            shutil.copy(image_path, destination_path)
            print(f"Copied {image_path} to {destination_path}")
        except Exception as e:
            print(f"Failed to copy {image_path}: {e}")

def create_thumbnails_from_folder(source_folder, destination_folder):
    file_list = os.listdir(source_folder)
    os.makedirs(destination_folder, exist_ok=True)
    for file in file_list:
        image_path = os.path.join(source_folder, file)
        destination_path = os.path.join(destination_folder, file)
        try:
            image = Image.open(image_path)
            # Resize the images where shortest side is 256 pixels, keeping aspect ratio. 
            if image.width > image.height: 
                factor = image.width/image.height
                image = image.resize(size=(int(round(factor*256,0)),256))
            else:
                factor = image.height/image.width
                image = image.resize(size=(256, int(round(factor*256,0))))
            # Crop out the center 224x224 portion of the image.

            image = image.crop(box=((image.width/2)-112, (image.height/2)-112, (image.width/2)+112, (image.height/2)+112))

            image.save(destination_path)
        except Exception as e:
            print(f"[ERROR] Failed to create thumbnail of file {file}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-index",
                        action="store",
                        type=int,
                        default=1,
                        help="Index of the session that is being processed. Default: 1")
    args = parser.parse_args()
    session_index = args.session_index - 1
    
    # source_folder = '/home/datawork-iot-nos/Seatizen/mauritius_use_case/Mauritius/162.38.140.205/Deep_mapping/backup/validated'
    # source_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_processing_output/useless_images_04092023/session_2017_11_04_kite_Le_Morne'
    
    # destination_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/zipped_sessions'
    # destination_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_processing_output/useless_images'
    # destination_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_unzipped_31082023'
    # destination_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_processing_output/useless_images_04092023/session_2017_11_04_kite_Le_Morne_thumbnails'
    
    # copy_folder_to_folder(source_folder, destination_folder, session_index)
    # create_thumbnails_from_folder(source_folder, destination_folder)

    # csv_path = '/home/datawork-iot-nos/Seatizen/data/useless_classification/ground_truth_annotations/useless_useful_df.csv'
    # image_folder = '/home/datawork-iot-nos/Seatizen/data/useless_classification/blurred_mauritius_seagrass'
    # destination_folder = '/home/datawork-iot-nos/Seatizen/data/herbier_classification/herbiers/entrainement_dataset/images'

    # copy_path_to_folder(csv_path, image_folder, destination_folder)

    source_folder = ''
    destination_folder = ''

    copy_folder_to_folder(source_folder, destination_folder, session_index)


if __name__ == '__main__':
    main()