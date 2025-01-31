#!/home/ubuntu/miniconda2/bin/python

from __future__ import division
import sys
import glob, os, gc
import uuid
import os.path
import csv
import numpy as np
from time import time
from subprocess import (call, Popen, PIPE)
from itertools import product
import shutil
import re
import pickle
from boto3.session import Session
import boto3
import h5py
import umap
import hdbscan


##Path to Data
basepath = "/home/ubuntu/"

with open(os.path.join(basepath,"config.txt")) as f:
    config = [line.rstrip() for line in f]    
print config[0]
print config[1]

Training = ["USD15","usd19","USD3","USD30","USD36","USD37","USH15","USH19","USH3","USH30","USH36","USH37"]



session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3') 
count = 0
for subject in Training:
    print(subject)
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, subject+'_ef.h5'),os.path.join(basepath,subject+'_ef.h5'))
    hf = h5py.File(os.path.join(basepath,subject+'_ef.h5'), 'r')
    if count == 0:
        Train_Y = hf['Y']
        Train_Z = hf['Z']
#        Train_U = hf['U']
        count+=1
    else:
        Train_Y = np.append(Train_Y,hf['Y'], axis=0)
        Train_Z = np.append(Train_Z,hf['Z'], axis=0)
#        Train_U = np.append(Train_U,hf['U'], axis=0)

hf = h5py.File('Training_af.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
#hf.create_dataset('U', data=Train_U)
hf.close()                

s3.meta.client.upload_file(os.path.join('Training_af.h5'),'bsmn-data',os.path.join('Training_af.h5'))

call(['sudo', 'shutdown', '-h', 'now'])