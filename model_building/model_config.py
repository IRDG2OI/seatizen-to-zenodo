import os
import torch
from torch import nn, optim
from torch.multiprocessing import Pool, Process, set_start_method
try:
     set_start_method('spawn')
except RuntimeError:
    pass


neural_network_settings = {'head_aggregation' : nn.Linear,
                          'head_hidden_layers_activation' : nn.Sigmoid,
                          'head_normalization' : nn.BatchNorm1d,
                          'proba_dropout' : 0.5,
                          'nb_hidden_head_layers' : 2,
                          'class_labels' :  ['herbier']}
