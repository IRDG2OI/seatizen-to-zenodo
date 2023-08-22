#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 15:03:13 2023

@author: g2oi
"""

import os
import argparse
import time
import pandas as pd
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
    
    source_folder = '/home/datawork-iot-nos/Seatizen/seatizen_to_zenodo/mauritius_sessions_unzipped'

    if session_index < 84:
        sessions = list_directories(source_folder)
        sessions.sort()
        session = sessions[session_index]
        input_file = os.path.join(source_folder, session + f'/LABEL/classification_{session}_jacques-v0.1.0_model-epoch=7-step=2056.csv')
        output_file = os.path.join(source_folder, session + f'/LABEL/{session}_stats.txt')
        
        df = pd.read_csv(input_file)
        total_images = len(df)
        useless_images = len(df[df['class'] == 'useless'])
        percentage_useless = (useless_images / total_images) * 100
        
        with open(output_file, 'w') as f:
            f.write(f"Total Images: {total_images}\n")
            f.write(f"Useless Images: {useless_images}\n")
            f.write(f"Percentage of Useless Images: {percentage_useless:.2f}%\n")
        
        execution_time_seconds = time.time() - start_time
        execution_time_minutes = "{:.2f}".format(execution_time_seconds / 60)
        print(f"\n{session} statistics written to {output_file}.")
        print(f"\nEnd time: {datetime.now()}")
        print(f"Total execution time: {execution_time_minutes} minutes")
        print("========================================================\n")

if __name__ == '__main__':
    main()