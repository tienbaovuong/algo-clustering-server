import gensim
import torch
import underthesea
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from transformers import AutoModel, AutoTokenizer, T5ForConditionalGeneration, T5Tokenizer

#data test
from app.data_test import data

# Load model vector hóa
phobert = AutoModel.from_pretrained("vinai/phobert-base")
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

# Load stopword
fname = 'vn_stopword.txt'
stopWordData = np.genfromtxt(fname, dtype='str', delimiter='\n', encoding="utf8")
stopWordData = stopWordData.tolist()

