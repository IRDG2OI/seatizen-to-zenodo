import os
import numpy as np
import pandas as pd
import torch
from torchvision import datasets, transforms
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms
import pytorch_lightning as pl
import torchmetrics
from PIL import ImageFile, Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
from pathlib import Path
from typing import Optional
from torch.multiprocessing import Pool, Process, set_start_method
from dataloading.custom_datasets import LabeledDataset, UnlabeledDataset
try:
     set_start_method('spawn')
except RuntimeError:
    pass


class DataModule(pl.LightningDataModule):
    
    def __init__(self, batch_size=32):
        super().__init__()
        self.batch_size = batch_size
        
        self.transforms_train = transforms.Compose([transforms.RandomResizedCrop(224),
                                      transforms.RandomHorizontalFlip(),
                                      transforms.ToTensor(),
                                      transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                                             ])
        
        self.transforms_test = transforms.Compose([transforms.Resize(224),
                                             transforms.CenterCrop(224),
                                             transforms.ToTensor(),
                                             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                                            ])

    def setup(self, stage=None):
        #Register train & test CSV
        self.train_df = pd.read_csv('/home1/datawork/lcarpent/herbiers/entrainement_dataset/ground_truth/train80.csv')
        self.val_df = pd.read_csv('/home1/datawork/lcarpent/herbiers/entrainement_dataset/ground_truth/test20.csv')

        self.train_df['label'] = self.train_df['label'].astype(int)
        self.val_df['label'] = self.val_df['label'].astype(int)

        # prepare transforms standards
        self.trainset = LabeledDataset(self.train_df, Path("/home1/datawork/lcarpent/herbiers/entrainement_dataset/images"), self.transforms_train)

        self.valset = LabeledDataset(self.val_df, Path("/home1/datawork/lcarpent/herbiers/entrainement_dataset/images"), self.transforms_test)
        

    def train_dataloader(self):
        return DataLoader(self.trainset, batch_size=self.batch_size, shuffle = True, num_workers = 8)

    def val_dataloader(self):
        return DataLoader(self.valset, batch_size=self.batch_size, shuffle = False, num_workers = 8)

    

    
