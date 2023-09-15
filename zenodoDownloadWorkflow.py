#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:38:42 2023

@author: g2oi
"""

import requests
import os

# Zenodo deposit URL (replace with your deposit URL)
deposit_url = "https://sandbox.zenodo.org/record/1241047"

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
        
        # Define the archive(s) you want to download
        archive_names_to_download = ["41597_2018_BFsdata2018124_MOESM320_ESM.zip"]
        
        # # Specify a download directory
        download_dir = "/home/g2oi/Documents/IRD/Travail/zenodo_tests/downloads/"
        os.makedirs(download_dir, exist_ok=True)
        
        # # Loop through the files and download the selected archives
        for file_info in files:
            # print(file_info["key"])
            if file_info["key"] in archive_names_to_download:
                download_url = file_info["links"]["self"]
                file_name = os.path.join(download_dir, file_info["key"])
                
                # Download the archive
                with requests.get(download_url, stream=True) as download_response:
                    download_response.raise_for_status()
                    with open(file_name, "wb") as file:
                        for chunk in download_response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                
                print(f"Downloaded: {file_name}")
    else:
        print("Access to this Zenodo deposit is restricted!")
else:
    print(f"Failed to retrieve deposit metadata. Status code: {response.status_code}")
