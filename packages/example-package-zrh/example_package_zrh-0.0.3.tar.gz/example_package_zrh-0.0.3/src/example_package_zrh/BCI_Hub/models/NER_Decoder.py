import sys
import os
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import joblib as jl
import cebra.datasets
from cebra import CEBRA
import scipy.io as sio
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
import torch
import yaml

import numpy as np
# import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from joblib import dump
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") ### select either 0 or 1
print(f'Using device: {device}')
import statsmodels.api as sm







class NER_ClassificationDecoder:
    """
    NER_ClassificationDecoder

    """
    def __init__(self, iterations=5000, output_dimension=8, batch_size=512,device="cuda:0"):
        # self.reg_type = reg_type 
        # self.reg_alpha = reg_alpha
        self.iterations = iterations # 5000
        self.output_dimension = output_dimension  # 8
        self.device = device  # "cuda:0"
        self.batch_size = batch_size  # 512
        self.cebra_veldir_model = CEBRA(model_architecture='offset1-model',
                                batch_size=self.batch_size,
                                learning_rate = 0.0001,
                                temperature = 1,
                                output_dimension = self.output_dimension,
                                max_iterations=self.iterations,
                                distance='cosine',
                                conditional='time_delta',
                                # device="cuda:1", ### 'cuda_if_available'
                                device=self.device, ### 'cuda_if_available'
                                verbose=True,
                                time_offsets=1)  # time_offsets=0，conditional='none' 
        # sub-C 0.69 0.70  单天0.425  sub-J 0.57 sub-M 0.72 sub-T 0.56  所有数据准确度0.67
        self.LogisticRegression_model = LogisticRegression(multi_class="multinomial", solver="lbfgs", max_iter=500)

    def fit(self, X_train, y_train):
        
        self.cebra_veldir_model.fit(X_train, y_train)
        cebra_veldir_train = self.cebra_veldir_model.transform(X_train)

                
        self.LogisticRegression_model.fit(cebra_veldir_train, y_train)
    
    def predict(self, X_test):
        
        cebra_veldir_test = self.cebra_veldir_model.transform(X_test)
        
        
        # 4. 预测
        y_pred = self.LogisticRegression_model.predict(cebra_veldir_test)

        # 5. 评估
        # acc = accuracy_score(y_init, y_pred)
        return y_pred
    
    # ======================================================
    # ✔ 严格模式 build_model
    # ======================================================
    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build NER_ClassificationDecoder from config dict.
        """

        # with open(path, "r") as f:
        #     model_params = yaml.safe_load(f)

        # ---------- 必须参数 ----------

        if "num_classes" not in model_params and "output_dim" not in model_params:
            raise KeyError(
                "[NER_ClassificationDecoder] Missing required parameter: "
                "`num_classes` or `output_dim`"
            )

        # 统一类别参数名
        output_dim = (
            model_params["num_classes"]
            if "num_classes" in model_params
            else model_params["output_dim"]
        )

        # ---------- 构建模型 ----------
        return NER_ClassificationDecoder(
                iterations=model_params.get("iterations", 5000),
                output_dimension=output_dim,
                batch_size=model_params.get("batch_size", 512),
                device=model_params.get("device", "cuda:0")
            )
    
    
    
    
    
# Classification NER_RegressionDecoder

class NER_RegressionDecoder:
    """
    NER_RegressionDecoder

    """
    def __init__(self, iterations=5000, output_dimension=8, batch_size=512,device="cuda:0"):
        # self.reg_type = reg_type 
        # self.reg_alpha = reg_alpha
        self.iterations = iterations # 5000
        self.output_dimension = output_dimension  # 8
        self.device = device  # "cuda:0"
        self.batch_size = batch_size  # 512
        self.cebra_veldir_model = CEBRA(model_architecture='offset1-model',
                                batch_size=self.batch_size,
                                learning_rate = 0.0001,
                                temperature = 1,
                                output_dimension = self.output_dimension,
                                max_iterations=self.iterations,
                                distance='cosine',
                                conditional='time_delta',
                                # device="cuda:1", ### 'cuda_if_available'
                                device=self.device, ### 'cuda_if_available'
                                verbose=True,
                                time_offsets=1)  # time_offsets=0，conditional='none' 
        # sub-C 0.69 0.70  单天0.425  sub-J 0.57 sub-M 0.72 sub-T 0.56  所有数据准确度0.67
        self.LinearRegression = LinearRegression()

    def fit(self, X_train, y_train):
        
        self.cebra_veldir_model.fit(X_train, y_train)
        cebra_veldir_train = self.cebra_veldir_model.transform(X_train)

                
        self.LinearRegression.fit(cebra_veldir_train, y_train)
    
    def predict(self, X_test):
        cebra_veldir_test = self.cebra_veldir_model.transform(X_test)
        
        # 4. 预测
        y_pred = self.LinearRegression.predict(cebra_veldir_test)

        # r2 = r2_score(y_pred, y_test, multioutput='variance_weighted')
        return y_pred
    
    # ======================================================
    # ✔ 严格模式 build_model
    # ======================================================
    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build NER_RegressionDecoder from config dict.
        """

        # with open(path, "r") as f:
        #     model_params = yaml.safe_load(f)

        # ---------- 必须参数 ----------

        if "num_classes" not in model_params and "output_dim" not in model_params:
            raise KeyError(
                "[NER_RegressionDecoder] Missing required parameter: "
                "`num_classes` or `output_dim`"
            )

        # 统一类别参数名
        output_dim = (
            model_params["num_classes"]
            if "num_classes" in model_params
            else model_params["output_dim"]
        )

        # ---------- 构建模型 ----------
        return NER_RegressionDecoder(
                iterations=model_params.get("iterations", 5000),
                output_dimension=output_dim,
                batch_size=model_params.get("batch_size", 512),
                device=model_params.get("device", "cuda:0")
            )