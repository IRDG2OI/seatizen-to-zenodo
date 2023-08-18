import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


class SavePredictionsDf():

    def __init__(self, files_dir, dest_path, csv_name):
        self.files_dir = files_dir
        self.dest_path = dest_path
        self.csv_name = csv_name

    def initialize_df(self, labels):
        empty_df = pd.DataFrame(columns = ['dir', 'image'] + labels)
        return empty_df

    def append_df_rows(self, df, file, prediction):
        rounded_prediction = np.round(prediction, 3)
        row = np.concatenate(([self.files_dir, file], rounded_prediction))
        df_length = len(df)
        df.loc[df_length] = row
        return df

    def save_csv_predictions(self, df):
        df.to_csv(self.dest_path + self.csv_name + '.csv', index = False, header = True)


def display_predictions(label, image, prob):
    img = mpimg.imread(image)
    plt.imshow(img)
    print(label)
    print(prob)
    plt.show()

