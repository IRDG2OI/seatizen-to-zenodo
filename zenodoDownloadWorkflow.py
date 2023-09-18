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

def download_from_filtered_metadata_csv(filtered_metadata_csv, download_dir):
    df = pd.read_csv(filtered_metadata_csv)
    try:
        sessions_DOI_IDS = df["session_DOI_ID"].unique().tolist()
    except KeyError:
        print("session_DOI_ID column not found in the provided CSV file.")
    for id in sessions_DOI_IDS:
        # Zenodo deposit URL (replace with your deposit URL)
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
                    if file_info["key"] == "DCIM.zip" or file_info["key"] == "PROCESSED_DATA.zip":
                        download_url = file_info["links"]["self"]
                        file_name = file_info["key"]
                        file_path = os.path.join(download_dir, f"{title}_{file_name}")
                        print(f"Downloading {file_name} of deposit {title}...")
                        # Download the archive
                        with requests.get(download_url, stream=True) as download_response:
                            download_response.raise_for_status()
                            with open(file_path, "wb") as file:
                                for chunk in download_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        file.write(chunk)
                        
                        print(f"Downloaded: {file_path}\n")
            else:
                print("Access to this Zenodo deposit is restricted!")
        else:
            print(f"Failed to retrieve deposit metadata. Status code: {response.status_code}")

def extract_all_zip(source_folder, destination_folder):
    print(f"\nExtraction of every zip located in {source_folder}...")
    zip_files = [file for file in os.listdir(source_folder) if file.endswith('.zip')]
    for zip_file in zip_files:
        zip_file_path = os.path.join(source_folder, zip_file)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                # Extract the file, excluding any parent folder information
                file_info.filename = os.path.basename(file_info.filename)
                zip_ref.extract(file_info, destination_folder)

def delete_unwanted_images(filtered_metadata_csv, image_folder):
    print("\nChecking for images not listed in the CSV provided...")
    df = pd.read_csv(filtered_metadata_csv)
    filtered_img = df["original_filename"].tolist()
    folder_img = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg'))]

    for img in folder_img:
        if img not in filtered_img:
            img_path = os.path.join(image_folder, img)
            os.remove(img_path)
            print(f"Deleted: {img}")

def rename_images(filtered_metadata_csv, image_folder):
    print("\nRenaming images...")
    df = pd.read_csv(filtered_metadata_csv)

    for index, row in df.iterrows():
        original_filename = row['original_filename']
        new_filename = row['filename']

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



def main():
    filtered_metadata_csv = "/home/g2oi/Documents/IRD/Travail/zenodo_tests/doi_datapaper/filtered_metadata.csv"
    download_dir = "/home/g2oi/Documents/IRD/Travail/zenodo_tests/downloads/"
    filtered_img_dir = "/home/g2oi/Documents/IRD/Travail/zenodo_tests/filtered_images/"

    # download_from_filtered_metadata_csv(filtered_metadata_csv, download_dir)

    extract_all_zip(download_dir, filtered_img_dir)

    delete_unwanted_images(filtered_metadata_csv, filtered_img_dir)

    rename_images(filtered_metadata_csv, filtered_img_dir)

if __name__ == '__main__':
    main()