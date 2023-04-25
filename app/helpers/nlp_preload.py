from typing import Any, List

import gensim
import torch
import underthesea
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from transformers import AutoModel, AutoTokenizer, T5ForConditionalGeneration, T5Tokenizer

class NLP():
    phobert: Any = None
    tokenizer: Any = None
    stop_word_data: List[str] = []

    def initialize(self):
        # Load model
        self.phobert = AutoModel.from_pretrained("vinai/phobert-base")
        self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

        # Stop word
        fname = 'vn_stopword.txt'
        self.stop_word_data = np.genfromtxt(fname, dtype='str', delimiter='\n', encoding="utf8").tolist()

nlp_service = NLP()