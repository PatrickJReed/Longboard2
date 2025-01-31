#!/home/ubuntu/miniconda2/bin/python

from __future__ import print_function
import glob, os, gc, sys
import os.path
import csv
import numpy as np
np.random.seed(1337)  # for reproducibility
from time import time
from subprocess import (call, Popen, PIPE)
from itertools import product
from IPython.display import display
from PIL import Image
from IPython.display import Image as IPImage
import shutil
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import uuid
import pickle
from boto3.session import Session
import boto3
import h5py


##Path to Data
basepath = "/home/ubuntu/"

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')

Data_Sets = []
Data_Sets.append(["USD41",Cells_USD41])

img_width, img_height = 512,512
nb_epochs = 50
batch_size = 32

#download training_data_all
s3.meta.client.download_file('bsmn-data',os.path.join('Training_Keras_Final.h5'),os.path.join('Training_Keras_Final.h5'))

hf = h5py.File(os.path.join('Training_Keras_Final.h5'), 'r')
Y_All = hf['Y_All'][()]
Final_Labels = hf['Final_Labels'][()]
Classes = len(set(Final_Labels))

#pull all cells per sample from Train_Y
L = len(Final_Labels)
T={}

#cell_id = Train_Y[i].strip().split('-')[0]
for i in range(0, L):
    position_key = Y_All[i]
    Y_Class = Final_Labels[i].astype(str)
    T[position_key] = Y_Class
    
for dset in Data_Sets:
    subject = dset[0]
    print(subject)
    for cell in dset[1]:
        print(cell)
        cell_ids = []
        s3.meta.client.download_file('bsmn-data',os.path.join(subject, cell+'_IDs.h5'),os.path.join(basepath,cell+'_IDs.h5'))
        f = h5py.File(os.path.join(basepath,cell+'_IDs.h5'), 'r')
        os.remove(os.path.join(basepath,cell+'_IDs.h5'))
        cell_ids = f['ID']
        count = 0
        for cid in cell_ids:
            s3.meta.client.download_file('bsmn-data',os.path.join(subject, cell+'_'+cid+'.h5'),os.path.join(basepath,cell+'_'+cid+'.h5'))
            xyz = h5py.File(os.path.join(basepath,cell+'_'+cid+'.h5'), 'r')
            os.remove(os.path.join(basepath,cell+'_'+cid+'.h5'))
            if count == 0:
                X = xyz['X'][()]
                Y = xyz['Y'][()]
                count+=1
            else:
                X = np.append(X,xyz['X'][()], axis=0)
                Y = np.append(Y,xyz['Y'][()], axis=0)
        print(X.shape)
        Labels = [None] * len(Y)
        for i in range(0,len(Y)):
            if Y[i] in Y_All:
                Labels[i] = T[Y[i]]
            else:
                Labels[i] = "NotClassified"                    
        rm=[]
        for i in range(0,len(Labels)):               
            if Labels[i] == "NotClassified": 
                rm=np.append(rm,i)
        X = np.delete(X,rm,0)
        Labels = np.delete(Labels,rm,0)
        Y = np.delete(Y,rm,0)
        for l in Labels:
            if not os.path.exists(os.path.join(basepath,"Test_Images",l)):
                os.makedirs(os.path.join(basepath,"Test_Images",l),0755)           
        for i in range(0,len(Labels)):
            im = Image.fromarray(np.uint8(X[i,:,:,:]*255),mode='RGB')
            im.save(os.path.join(basepath,"Test_Images",Labels[i],Y[i]))    
