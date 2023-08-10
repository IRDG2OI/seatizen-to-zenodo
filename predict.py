import os
import torch
import numpy as np
import shutil
import torchvision.models as models
from torchvision import datasets, transforms
from torch import nn, optim
from torchvision.models.resnet import ResNet
from torch.utils.data import DataLoader, random_split, Dataset
from torchvision import datasets, transforms
import pytorch_lightning as pl
import torchmetrics
from model_building.model_config import neural_network_settings
from model_building.layers import HeadNet, build_model
from dataloading.datamodule import DataModule
from model_building.model import UselessImagesClassifier
from inference.predictor import UselessImagesPredictor
from inference.save_predictions import SavePredictionsDf, display_predictions
from torch.multiprocessing import Pool, Process, set_start_method
from dataloading.custom_datasets import UnlabeledDataset

def herbier_model(useful_path, output_path):
    
    try:
     set_start_method('spawn')
    except RuntimeError:
        pass

    os.environ['MKL_THREADING_LAYER'] = 'GNU'
    
################ VARIABLES ###########################
#     useful_path = '/home/datawork-iot-nos/Seatizen/data/herbiers_leanne/session_2023_06_01_hermitage_plancha_body_v1A_00/useful'
#     output_path = '/home/datawork-iot-nos/Seatizen/data/herbiers_leanne/session_2023_06_01_hermitage_plancha_body_v1A_00/grasskelly'
#     herbier_path = '/home/datawork-iot-nos/Seatizen/data/herbiers_leanne/session_2023_06_01_hermitage_plancha_body_v1A_00/herbier'
#     not_herbier_path = '/home/datawork-iot-nos/Seatizen/data/herbiers_leanne/session_2023_06_01_hermitage_plancha_body_v1A_00/not_herbier'


################ BUILD MODEL #########################
    backbone = models.resnet50(weights='ResNet50_Weights.DEFAULT')
    headnet = HeadNet(bodynet_features_out = backbone.fc.in_features,
                                       head_aggregation_function = neural_network_settings['head_aggregation'],
                                       head_hidden_layers_activation_function = neural_network_settings['head_hidden_layers_activation'],
                                       head_normalization_function = neural_network_settings['head_normalization'],
                                       head_proba_dropout = neural_network_settings['proba_dropout'],
                                       nb_hidden_head_layers = neural_network_settings['nb_hidden_head_layers'], 
                                       nb_classes = len(neural_network_settings['class_labels']))
    model = build_model(backbone, headnet)
    ckpt_path='/home/datawork-iot-nos/Seatizen/models/stage_leanne/herbier_classification/lightning_logs/version_17/checkpoints/epoch=8-step=620.ckpt'
    predictor = UselessImagesPredictor(model, ckpt_path)

################## LOAD IMAGES ########################
    unlabeled_img = os.listdir(useful_path)
    
    # Filter out only the image files
    image_extensions = ['.jpg', '.jpeg']
    image_files = [img for img in unlabeled_img if any(img.lower().endswith(ext) for ext in image_extensions)]
    
    dm = DataModule()
    unlabeled_set = UnlabeledDataset(image_files, useful_path, dm.transforms_test)

################### PREPARE PREDICTION ################  
    csv = 'results_herbier_classification'
    predict_dataloader = DataLoader(unlabeled_set, batch_size=1, shuffle = False, num_workers = 8)
    savepredictionsdf = SavePredictionsDf(files_dir = useful_path, dest_path = output_path, csv_name = csv)
    df = savepredictionsdf.initialize_df()

################### PREDICT ###########################
    for batch in predict_dataloader:
        image_name, image = batch
        prediction, label = predictor.predict(image)
        df = savepredictionsdf.append_df_rows(df, image_name[0], prediction, label)

################### SAVE PREDICTION ###################
#     df.to_csv(os.path.join(output_path, csv))
#     df.to_csv(output_path)
    return df
    
################### SELECT USEFUL FRAMES ##############
#     directory = df['dir'][1]
#     image_list = df['image'].tolist()
#     class_list = df['class'].tolist()
#     for i in range(len(image_list)):
#         if class_list[i]=='herbier':
#             full_file_name = os.path.join(directory,image_list[i])
#             shutil.copy(full_file_name,herbier_path)
#         if class_list[i]=='not_herbier':
#             full_file_name = os.path.join(directory,image_list[i])
#             shutil.copy(full_file_name,not_herbier_path)

# if __name__ == "__main__":
#     main()