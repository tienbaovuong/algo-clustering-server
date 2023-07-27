from typing import Any, List

import gensim
import torch
import underthesea
import numpy as np
from transformers import AutoModel, AutoTokenizer

class NLP():
    phobert: Any = None
    tokenizer: Any = None
    stop_word_data: List[str] = []

    def initialize(self):
        # Load model
        self.phobert = AutoModel.from_pretrained("model")
        self.tokenizer = AutoTokenizer.from_pretrained("model")

        # Stop word
        fname = 'app/helpers/vn_stopword.txt'
        self.stop_word_data = np.genfromtxt(fname, dtype='str', delimiter='\n', encoding="utf8").tolist()

    def extract_feature(self, lines):
        if not self.phobert or not self.tokenizer:
            print("ohno")
            return None
        features_list = []
        for line in lines:
            # Preprocess
            line = gensim.utils.simple_preprocess(str(line))
            line = " ".join(line)
            # Segmentation
            line = underthesea.word_tokenize(line, format="text")
            line = "".join(line)
            # Extract feature
            input_ids = torch.tensor([self.tokenizer.encode(line)])
            input_ids = torch.slice_copy(input_ids, 1, 0, 256)
            with torch.no_grad():
                features = self.phobert(input_ids)
            v_features = features[0][:, 0, :]
            features_list.append(v_features[0].tolist())
        return features_list

nlp_service = NLP()