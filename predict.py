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

def create_head(num_features , number_classes ,dropout_prob=0.5 ,activation_func =nn.ReLU):
    features_lst = [num_features , num_features//2 , num_features//4]
    layers = []
    for in_f ,out_f in zip(features_lst[:-1] , features_lst[1:]):
        layers.append(nn.Linear(in_f , out_f))
        layers.append(activation_func())
        layers.append(nn.BatchNorm1d(out_f))
        if dropout_prob !=0 : layers.append(nn.Dropout(dropout_prob))
    layers.append(nn.Linear(features_lst[-1] , number_classes))
    return nn.Sequential(*layers)

def annotation_model(useful_path, output_path, ckpt_path, threshold_labels):
    
    try:
     set_start_method('spawn')
    except RuntimeError:
        pass

    os.environ['MKL_THREADING_LAYER'] = 'GNU'


################ BUILD MODEL #########################
    backbone = models.resnet50(weights='ResNet50_Weights.DEFAULT')
    classLabels = list(threshold_labels.keys())
    
    if len(classLabels) == 1: # herbier classification
        headnet = HeadNet(bodynet_features_out = backbone.fc.in_features,
                                           head_aggregation_function = neural_network_settings['head_aggregation'],
                                           head_hidden_layers_activation_function = neural_network_settings['head_hidden_layers_activation'],
                                           head_normalization_function = neural_network_settings['head_normalization'],
                                           head_proba_dropout = neural_network_settings['proba_dropout'],
                                           nb_hidden_head_layers = neural_network_settings['nb_hidden_head_layers'], 
                                           nb_classes = len(neural_network_settings['class_labels']))
        model = build_model(backbone, headnet)
    #     ckpt_path='/home/datawork-iot-nos/Seatizen/models/stage_leanne/herbier_classification/lightning_logs/version_17/checkpoints/epoch=8-step=620.ckpt'
    elif len(classLabels) > 1: # multi-label annotation
        model = models.resnet50()
        num_features = backbone.fc.in_features
        top_head = create_head(num_features , len(classLabels))
        model.fc = top_head
        
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
    df = savepredictionsdf.initialize_df(classLabels)

################### PREDICT ###########################
    for batch in predict_dataloader:
        image_name, image = batch
        image_path = os.path.join(useful_path, image_name[0])
        prediction, results = predictor.predict(image_path, image, threshold_labels)
        df = savepredictionsdf.append_df_rows(df, image_name[0], results)

    return df