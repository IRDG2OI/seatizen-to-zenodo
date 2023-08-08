### Section 1 - First, let's import everything we will be needing.
# conda install pytorch
# conda install torchvision
from __future__ import print_function, division
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
'''
# To use LaTeX and select Helvetica as the default font, without editing matplotlibrc use:
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('text', usetex=True)
'''
import time
import copy
import os
import shutil
import matplotlib.image as mpimg

# in order to split "training_dataset" folder into train and val folders
#import splitfolders  # or import split_folders
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
# from fine_tuning_config_file import * # no fine tuning config file
# packages and functions for the confusion matrix
from sklearn.metrics import confusion_matrix
#from resources.plotcm import plot_confusion_matrix
# packages and functions for plot images
#from resources.plotimg import imshow, visualize_model
#from resources.images_in_folder import print_images

## If you want to keep a track of your network on tensorboard, set USE_TENSORBOARD TO 1 in config file.
#if USE_TENSORBOARD:
#    from pycrayon import CrayonClient
#    cc = CrayonClient(hostname=TENSORBOARD_SERVER)
#    try:
#        cc.remove_experiment(EXP_NAME)
#    except:
#        pass
#    foo = cc.create_experiment(EXP_NAME)
## If you want to use the GPU, set GPU_MODE TO 1 in config file
#device = "cpu"
#use_gpu = GPU_MODE
#if use_gpu:
#    #torch.cuda.set_device(CUDA_DEVICE)
#    torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# import useful extra libraries
from PIL import Image
# sort 
import operator
import pandas as pd
# copy image in folder
from shutil import copyfile
# add text on images
from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont
#get subpaths of path
import pathlib
from itertools import compress, chain

###############################################################################
###############################################################################
# session name
#session_name = "multilabel_session_2017_11_04_kite_Le_Morne_100GOPRO"
# txt path with informations about the session
#output_txt_path = "/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_txt/output_" + session_name + ".txt"
#output_txt_path = "/home1/datahome/mcontini/multilabelTest/results_txt/output_500_iterations.txt"
#file = open(output_txt_path, "a+")
#file.write("Simulation started on %s \r\n" %device)
#file.close()
###############################################################################
###############################################################################
classLabels = ["Acropore_branched", "Acropore_digitised", "Acropore_tabular", "Algae_assembly", 
               "Algae_limestone", "Algae_sodding", "Dead_coral", "Fish", "Human_object",
               "Living_coral", "Millepore", "No_acropore_encrusting", "No_acropore_massive",
              "No_acropore_sub_massive",  "Rock", "Sand",
               "Scrap", "Sea_cucumber", "Syringodium_isoetifolium",
               "Thalassodendron_ciliatum",  "Useless"]
###############################################################################
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
###############################################################################
###############################################################################
def is_an_image(img_path) :
    try:
        im=Image.open(img_path)
    except:
        return False
    return True
###############################################################################
##############################################################################
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
###############################################################################
###############################################################################
def predict_probabilities(image_path, checkpoint_path):
    ''' Predict the class (or classes) of an image using a trained deep learning model.
    '''
    model = models.resnet50() # model initialization
    num_features = model.fc.in_features # get the no of on_features in last Linear unit
    top_head = create_head(num_features , len(classLabels)) # because ten classes
    model.fc = top_head # replace the fully connected layer
    # select here the right device, if GPU bugs keep CPU
    #st = torch.load(checkpoint_path, map_location='cpu')
    st = torch.load(checkpoint_path, map_location='cuda:0' if torch.cuda.is_available() else 'cpu')
    model.load_state_dict(st, strict=False) # load the state_dict from disk

    # Implement the code to predict the class from an image file
    tensor_image = process_image(image_path)
    # classes
    inv_classes_dictionary = classLabels
    model.eval()
    with torch.no_grad():
        #feed the input
        tensor_image.unsqueeze_(0)
        output = model(tensor_image)
        #output = torch.sigmoid(output).data > 0.5
        output = torch.sigmoid(output).data
        #output = output > 0.2
        #print("output is :")
        #print(output)
        output = output.cpu().numpy()
        #print("output is :")
        #print(output)
        output = output[0]
        output = np.around(output, decimals=3)
        #pred_class = list(compress(classLabels, output))
        #pred_class = pred_class[0]
        #pred_class = list(chain.from_iterable(pred_class))
        #print("the predicted classes are :")
        #print(pred_class)
        #print(type(output))
    #return pred_class
    return output
###############################################################################
###############################################################################
def write_csv(df, test_path, checkpoint_path, output_txt_path):
    files = os.listdir(test_path)
    # we sort the images by name
    files = sorted(files)
    # count the number of images
    nb_images = 0
    # define lists
    images_list = []
    probs_list = []
    classes_list = []
    for file in files :
        img_path = test_path + '/'+ file
        # check that the file is not a jpynb checkpoint
        if (is_an_image(img_path)) :
            probs = predict_probabilities(img_path, checkpoint_path)
            probs = np.concatenate(([img_path], probs))
            df_length = len(df)
            df.loc[df_length] = probs
            nb_images += 1
        # keep informations on txt output file
        if nb_images%100 == 0 :
            file = open(output_txt_path, "a+")
            file.write("We are at photo : %f\r\n" % nb_images)
            file.close()
    return df
###############################################################################
###############################################################################
# flag to save the csv file with paths and classes probabilities
#save_csv = 1
# create csv file for predicted images
#df = pd.DataFrame(columns=['Image_path',"Acropore_branched", "Acropore_digitised", "Acropore_tabular", "Algae_assembly", 
#               "Algae_limestone", "Algae_sodding", "Dead_coral", "Fish", "Human_object",
#               "Living_coral", "Millepore", "No_acropore_encrusting", "No_acropore_massive",
#              "No_acropore_sub_massive",  "Rock", "Sand",
#               "Scrap", "Sea_cucumber", "Syringodium_isoetifolium",
#               "Thalassodendron_ciliatum",  "Useless"])
# folder path with all the images
#source = "/home/datawork-iot-nos/Seatizen/mauritius_use_case/Mauritius/162.38.140.205/Deep_mapping/backup/validated/session_2017_11_04_kite_Le_Morne/DCIM/100GOPRO"
# NN path
#checkpoint_path = "/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/models/multilabel_with_sable.pth"
#df = write_csv(df, source, checkpoint_path)
#if save_csv :
#    # output df path
#    df_path = "/home3/datahome/aboyer/Documents/seatizen-to-zenodo/multilabelTest/results_csv/df_" + session_name + ".csv"
#    # save dataframe with images and predictions 
#    df.to_csv (df_path, index = False, header=True)
