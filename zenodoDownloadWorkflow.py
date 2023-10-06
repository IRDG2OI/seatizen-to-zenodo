#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:38:42 2023

@author: g2oi
"""

import requests
import os
import pandas as pd
import zipfile
import shutil

"""
This script defines multiple functions that are used in download_from_filtered_metadata_csv() function which is called in main() at runtime.
With this script, you can download images from Zenodo based on a filtered csv file. 
You will download all the images from one or multiple deposit but you will keep only the images that are listed in the filtered csv file.
The filtered csv file will be build as you wish, but, it must depend on the metadata_image.csv file.
"""

def extract_all_zip(source_folder, destination_folder, selected_zip):
    '''
    Function to extract the content of DCIM.zip or DCIM_THUMBNAILS.zip or FRAMES.zip.
    ### Input
    - source_folder: it's the path to the folder where data from Zenodo where downloaded
    - destination_folder: it's the path to the folder where filtered images will be
    - selected_zip: either "DCIM.zip" or "DCIM_THUMBNAILS.zip" according to whether images should be extracted in  their original size (DCIM.zip) or in a resized format (DCIM_THUMBNAILS.zip)
    ### Output
    Extraction of images that are in DCIM.zip or DCIM_THUMBNAILS.zip or FRAMES.zip.
    '''
    # Getting the list of all zip that are in the source_folder
    zip_files = [file for file in os.listdir(source_folder) if file.endswith('.zip')]

    for zip_file in zip_files:
        zip_file_path = os.path.join(source_folder, zip_file)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # extraction of either DCIM.zip or DCIM_THUMBNAILS.zip
            if zip_file == selected_zip:
                print(f"\nExtraction of the images from the zip {zip_file}...")
            for file_info in zip_ref.infolist():
                # Extract the file, excluding any parent folder information
                file_info.filename = os.path.basename(file_info.filename)
                zip_ref.extract(file_info, destination_folder)
        
        if file_info.filename == "FRAMES.zip":
            frames_zip_path = os.path.join(destination_folder, "FRAMES.zip")
            with zipfile.ZipFile(frames_zip_path, 'r') as zip_ref:
                print(f"\nExtraction of the images from {file_info.filename}")
                zip_ref.extractall(destination_folder)
        
        # Deletion of every zip files that are in the destination_folder following the zip extraction
        destination_folder_file_list = os.listdir(destination_folder)
        for file_name in destination_folder_file_list:
            if file_name.endswith(".zip"):
                file_path = os.path.join(destination_folder, file_name)
                os.remove(file_path)
                print(f"\nRemoved {file_name}")

        
        print(f"\nRemoving {zip_file}...")
        os.remove(zip_file_path)

def delete_unwanted_images(filtered_metadata_csv, image_folder):
    '''
    Function to delete images that are in the image_folder but not listed in the filtered_metadata_csv.
    '''
    print("\nChecking for images not listed in the CSV provided...\n")
    df = pd.read_csv(filtered_metadata_csv)
    if "FileName" in df.columns:
        # getting the list of images names from filtered_metadata_csv
        filtered_img = df["FileName"].tolist()
        # getting the list of images names in the image_folder
        folder_img = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg'))]

        # checking if the images in the folder are in the csv
        for img in folder_img:
            if img not in filtered_img:
                # if images are not in the csv, they are deleted
                img_path = os.path.join(image_folder, img)
                os.remove(img_path)
                print(f"Deleted: {img}")

def rename_images(filtered_metadata_csv, image_folder):
    '''
    Function to rename images from OriginalFileName to FileName.
    '''
    print("\nRenaming images...\n")
    df = pd.read_csv(filtered_metadata_csv)

    for index, row in df.iterrows():
        original_filename = row['OriginalFileName']
        new_filename = row['FileName']

        # Check if the original file exists in the folder
        old_path = os.path.join(image_folder, original_filename)
        if os.path.exists(old_path):
            new_path = os.path.join(image_folder, new_filename)

            # Rename the file
            shutil.move(old_path, new_path)
            print(f'Renamed {original_filename} to {new_filename}')
        else:
            print(f'File {original_filename} not found in the folder.')

    print("Image renaming completed.")

def download_from_filtered_metadata_csv(filtered_metadata_csv, download_dir, filtered_img_dir, thumbnails):
    '''
    # Function to download images from Zenodo based on a filtered csv file.
    ### Input
    - filtered_metadata_csv: the filtered metadata file that contains the list of images you want to download and their associated Zenodo DOI.
    - download_dir: path to the folder where the downloaded zip will be located
    - filtered_img_dir: path to the folder where the images you want will be
    - thumbnails: a boolean that indicate if images should be extracted in  their original size (DCIM.zip) or in a resized format (DCIM_THUMBNAILS.zip)
    ### Output
    The images that you want from Zenodo in the choosen folder.
    '''
    # Selection of the zip to extract based on thumbnails value
    if thumbnails:
        selected_zip = "DCIM_THUMBNAILS.zip"
    else:
        selected_zip = "DCIM.zip"

    df = pd.read_csv(filtered_metadata_csv)

    try:
        sessions_DOI_IDS = df["Session_doi"].unique().tolist()
    except KeyError:
        print("Session_doi column not found in the provided CSV file.")

    for id in sessions_DOI_IDS:
        # Zenodo deposit URL
        deposit_url = f"https://sandbox.zenodo.org/record/{id}"

        # Zenodo API endpoint for the deposit metadata
        api_url = "https://" + deposit_url.split("/")[-3] + "/api/records/" + deposit_url.split("/")[-1]

        # Make a GET request to fetch deposit metadata
        response = requests.get(api_url)

        if response.status_code == 200:
            # Parse the JSON response
            deposit_data = response.json()
            
            # Verify the access right to the deposit
            access_right = deposit_data["metadata"]["access_right"]
            
            if access_right != "restricted":
                # List of files in the deposit
                files = deposit_data["files"]

                # Get deposit title
                title = deposit_data["metadata"]["title"]
                
                # Create the download directory if it doesn't exist
                os.makedirs(download_dir, exist_ok=True)
                
                # Loop through the files and download the selected archives
                for file_info in files:
                    # print(file_info["key"])
                    # Download the archive containing the images -> can either be DCIM.zip or PROCESSED_DATA.zip
                    if file_info["key"] == selected_zip or file_info["key"] == "PROCESSED_DATA.zip":
                        download_url = file_info["links"]["self"]
                        file_name = file_info["key"]
                        file_path = os.path.join(download_dir, file_name)
                        print("\n==============================================")
                        print(f"Downloading {file_name} of deposit {title}...")
                        # Download the archive
                        with requests.get(download_url, stream=True) as download_response:
                            download_response.raise_for_status()
                            with open(file_path, "wb") as file:
                                for chunk in download_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        file.write(chunk)
                        
                        print(f"Downloaded: {file_path}")
                        print("==============================================\n")

                # extraction of zip containing images
                extract_all_zip(download_dir, filtered_img_dir, selected_zip)
                # renaming images from original_filename to filename
                rename_images(filtered_metadata_csv, filtered_img_dir)
                # deletion of images not listed in the filtered csv
                delete_unwanted_images(filtered_metadata_csv, filtered_img_dir)
                
            else:
                print("Access to this Zenodo deposit is restricted!")
        else:
            print(f"Failed to retrieve deposit metadata. Status code: {response.status_code}")


def main():
    filtered_metadata_csv = "/home/g2oi/Documents/IRD/Travail/zenodo_tests/doi_datapaper/filtered_metadata.csv"
    download_dir = "/home/g2oi/Documents/IRD/Travail/zenodo_tests/downloads/test_21092023/"
    filtered_img_dir = "/home/g2oi/Documents/IRD/Travail/zenodo_tests/filtered_images/test_21092023/"
    thumbnails = False

    download_from_filtered_metadata_csv(filtered_metadata_csv, download_dir, filtered_img_dir, thumbnails)


if __name__ == '__main__':
    main()