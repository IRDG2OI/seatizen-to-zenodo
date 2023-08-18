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
        try:
            new_state_dict = OrderedDict()
            for k, v in checkpoint_loaded['state_dict'].items():
                name = k[6:] 
                new_state_dict[name] = v
            self.model.load_state_dict(new_state_dict)
        except KeyError:
            self.model.load_state_dict(checkpoint_loaded, strict=False)
        return self.model
        
    def predict(self, image_path, images, threshold_labels):
        self.model = self.load_checkpoint()
        self.model.eval()
        tensor_image = process_image(image_path)
        with torch.no_grad():
            tensor_image.unsqueeze_(0)
            logits = self.model(tensor_image)
            probs = torch.sigmoid(logits).data
            probs = probs.cpu().numpy()
            probs = probs[0]
            probs = np.around(probs, decimals=3)
        results = []
        index = -1
        for label, threshold in threshold_labels.items():
            index += 1
            if probs[index] > threshold:
                results.append(probs[index])
            else:
                results.append(0)
        return probs, results

def process_image(image_path, normalize = True):
    ''' Scales, crops, and normalizes a PIL image for a PyTorch model,
        returns an Numpy array
    '''
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

    # Convert to numpy array
    np_image = np.array(image)
    np_image = np_image/255
    # Normalize image
    if (normalize):
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        np_image = (np_image - mean) / std 
    # Reorder dimension for PyTorch
    np_image = np.transpose(np_image, (2, 0, 1))

    tensor_image = torch.from_numpy(np_image).type(torch.FloatTensor)

    return tensor_image