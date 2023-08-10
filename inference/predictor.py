import os
import time
import numpy as np
import pandas as pd
import torch
from torchvision import datasets, transforms
from torch import nn, optim
from torchvision.models.resnet import ResNet
from torchvision.datasets import MNIST
from torch.utils.data import DataLoader, random_split, Dataset
from torch.nn import functional as F
from torchvision import datasets, transforms
import pytorch_lightning as pl
import torchmetrics
from torch.multiprocessing import Pool, Process, set_start_method
from PIL import ImageFile, Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
from collections import OrderedDict

try:
     set_start_method('spawn')
except RuntimeError:
    pass


class UselessImagesPredictor():
    def __init__(self, model, checkpoint_path):
                
        self.model = model
        self.model= self.model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        self.checkpoint = checkpoint_path
        
    def load_checkpoint(self):
        checkpoint_loaded = torch.load(self.checkpoint, map_location='cuda:0' if torch.cuda.is_available() else 'cpu')
        new_state_dict = OrderedDict()
        for k, v in checkpoint_loaded['state_dict'].items():
            name = k[6:] 
            new_state_dict[name] = v
        self.model.load_state_dict(new_state_dict)
        return self.model
        
    def predict(self, images):
        self.model = self.load_checkpoint()
        self.model.eval()
        with torch.no_grad():
            logits = self.model(images)
            prob = torch.sigmoid(logits).data
            prob = prob.cpu().numpy()
            prob = prob[0]
            prob = np.around(prob, decimals=3)
        if prob > 0.592: #instead of 0.5
            label = "herbier"
        else:
            label = "not_herbier"
        return prob, label

