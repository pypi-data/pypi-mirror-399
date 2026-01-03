############### IMPORT PACKAGES ##################

import numpy as np
from numpy.linalg import inv as inv #Used in kalman filter
import torch

#Used for naive bayes decoder
try:
    import statsmodels.api as sm
except ImportError:
    print("\nWARNING: statsmodels is not installed. You will be unable to use the Naive Bayes Decoder")
    pass
try:
    import math
except ImportError:
    print("\nWARNING: math is not installed. You will be unable to use the Naive Bayes Decoder")
    pass
try:
    from scipy.spatial.distance import pdist
    from scipy.spatial.distance import squareform
    from scipy.stats import norm
    from scipy.spatial.distance import cdist
except ImportError:
    print("\nWARNING: scipy is not installed. You will be unable to use the Naive Bayes Decoder")
    pass



#Import scikit-learn (sklearn) if it is installed
try:
    from sklearn import linear_model #For Wiener Filter and Wiener Cascade
    from sklearn.svm import SVR #For support vector regression (SVR)
    from sklearn.svm import SVC #For support vector classification (SVM)
except ImportError:
    print("\nWARNING: scikit-learn is not installed. You will be unable to use the Wiener Filter or Wiener Cascade Decoders")
    pass

#Import XGBoost if the package is installed
try:
    import xgboost as xgb #For xgboost
except ImportError:
    print("\nWARNING: Xgboost package is not installed. You will be unable to use the xgboost decoder")
    pass

#Import functions for Keras if Keras is installed
#Note that Keras has many more built-in functions that I have not imported because I have not used them
#But if you want to modify the decoders with other functions (e.g. regularization), import them here


try:
    from sklearn.preprocessing import OneHotEncoder
except ImportError:
    print("\nWARNING: Sklearn OneHotEncoder not installed. You will be unable to use XGBoost for Classification")
    pass



##################### DECODER FUNCTIONS ##########################
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet

class KalmanDecoderV2:
    """
    Kalman filter decoding algorithm.

    Parameters
    ----------
        reg_type : str {'l1', 'l2', 'l12'}. Default None.
            regularization type.
            'l1' : Linear least squares with l1 regularization (i.e. Lasso).
            'l2' : Linear least squares with l2 regularization (i.e. Ridge).
            'l12' : Linear least squares with combined L1 and L2 regularization (i.e. Elastic Net).
        reg_alpha : float. Default 0.
            regularization constant/strength.
    """
    def __init__(self, reg_type=None, reg_alpha=0):
        self.reg_type = reg_type 
        self.reg_alpha = reg_alpha

    def fit(self, X_train, y_train):
        if self.reg_type == 'l1':
            regres = Lasso(alpha=self.alpha_reg)            
        elif self.reg_type == 'l2':
            regres = Ridge(alpha=self.alpha_reg)
        elif self.reg_type == 'l12':
            regres = ElasticNet(alpha=self.alpha_reg)
        else:
            regres = LinearRegression()
        
        X = y_train 
        Z = X_train 
        nt = X.shape[0]              
        X1 = X[:nt-1,:] 
        X2 = X[1:,:] 
        
        regres.fit(X1, X2)
        A = regres.coef_
        W = np.cov((X2 - np.dot(X1, A.T)).T)
        regres.fit(X, Z)
        H = regres.coef_ 
        Q = np.cov((Z - np.dot(X, H.T)).T) 
        self.model = [A, W, H, Q] 
    
    def predict(self, X_test, y_init):
        # extract parameters
        A, W, H, Q = self.model

        X = np.matrix(y_init.T)
        Z = np.matrix(X_test.T)

        # initialise states and covariance matrix
        n_states = X.shape[0] # dimensionality of the state
        states = np.empty((n_states, Z.shape[1])) # keep track of states over time (states is what will be returned as y_pred)
        P_m = np.matrix(np.zeros([n_states, n_states]))
        P = np.matrix(np.zeros([n_states, n_states]))
        state = X[:,0] # initial state
        states[:,0] = np.copy(np.squeeze(state))

        # get predicted state for every time bin
        for t in range(Z.shape[1]-1):
            # do first part of state update - based on transition matrix
            P_m = A*P*A.T + W
            state_m = A*state

            # do second part of state update - based on measurement matrix
            try:
                K = P_m*H.T*inv(H*P_m*H.T + Q) # calculate Kalman gain
            except np.linalg.LinAlgError:
                K = P_m*H.T*pinv(H*P_m*H.T+Q) # calculate Kalman gain
            P = (np.matrix(np.eye(n_states)) - K*H)*P_m
            state = state_m + K*(Z[:,t+1] - H*state_m)
            states[:,t+1] = np.squeeze(state) # record state at the timestep
        y_pred = states.T
        return y_pred



##################### WIENER FILTER ##########################

class WienerFilterRegression(object):

    """
    Class for the Wiener Filter Decoder

    There are no parameters to set.

    This simply leverages the scikit-learn linear regression.
    """

    def __init__(self):
        return


    def fit(self,X_flat_train,y_train):

        """
        Train Wiener Filter Decoder

        Parameters
        ----------
        X_flat_train: numpy 2d array of shape [n_samples,n_features]
            This is the neural data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples, n_outputs]
            This is the outputs that are being predicted
        """

        self.model=linear_model.LinearRegression() #Initialize linear regression model
        self.model.fit(X_flat_train, y_train) #Train the model


    def predict(self,X_flat_test):

        """
        Predict outcomes using trained Wiener Cascade Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        y_test_predicted=self.model.predict(X_flat_test) #Make predictions
        return y_test_predicted




##################### WIENER CASCADE ##########################

class WienerCascadeRegression(object):

    """
    Class for the Wiener Cascade Decoder

    Parameters
    ----------
    degree: integer, optional, default 3
        The degree of the polynomial used for the static nonlinearity
    """

    def __init__(self,degree=3):
         self.degree=degree


    def fit(self,X_flat_train,y_train):

        """
        Train Wiener Cascade Decoder

        Parameters
        ----------
        X_flat_train: numpy 2d array of shape [n_samples,n_features]
            This is the neural data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples, n_outputs]
            This is the outputs that are being predicted
        """

        num_outputs=y_train.shape[1] #Number of outputs
        models=[] #Initialize list of models (there will be a separate model for each output)
        for i in range(num_outputs): #Loop through outputs
            #Fit linear portion of model
            regr = linear_model.LinearRegression() #Call the linear portion of the model "regr"
            regr.fit(X_flat_train, y_train[:,i]) #Fit linear
            y_train_predicted_linear=regr.predict(X_flat_train) # Get outputs of linear portion of model
            #Fit nonlinear portion of model
            p=np.polyfit(y_train_predicted_linear,y_train[:,i],self.degree)
            #Add model for this output (both linear and nonlinear parts) to the list "models"
            models.append([regr,p])
        self.model=models


    def predict(self,X_flat_test):

        """
        Predict outcomes using trained Wiener Cascade Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        num_outputs=len(self.model) #Number of outputs being predicted. Recall from the "fit" function that self.model is a list of models
        y_test_predicted=np.empty([X_flat_test.shape[0],num_outputs]) #Initialize matrix that contains predicted outputs
        for i in range(num_outputs): #Loop through outputs
            [regr,p]=self.model[i] #Get the linear (regr) and nonlinear (p) portions of the trained model
            #Predictions on test set
            y_test_predicted_linear=regr.predict(X_flat_test) #Get predictions on the linear portion of the model
            y_test_predicted[:,i]=np.polyval(p,y_test_predicted_linear) #Run the linear predictions through the nonlinearity to get the final predictions
        return y_test_predicted



##################### KALMAN FILTER ##########################

class KalmanFilterRegression(object):

    """
    Class for the Kalman Filter Decoder

    Parameters
    -----------
    C - float, optional, default 1
    This parameter scales the noise matrix associated with the transition in kinematic states.
    It effectively allows changing the weight of the new neural evidence in the current update.

    Our implementation of the Kalman filter for neural decoding is based on that of Wu et al 2003 (https://papers.nips.cc/paper/2178-neural-decoding-of-cursor-motion-using-a-kalman-filter.pdf)
    with the exception of the addition of the parameter C.
    The original implementation has previously been coded in Matlab by Dan Morris (http://dmorris.net/projects/neural_decoding.html#code)
    """

    def __init__(self,C=1):
        self.C=C


    def fit(self,X_kf_train,y_train):

        """
        Train Kalman Filter Decoder

        Parameters
        ----------
        X_kf_train: numpy 2d array of shape [n_samples(i.e. timebins) , n_neurons]
            This is the neural data in Kalman filter format.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples(i.e. timebins), n_outputs]
            This is the outputs that are being predicted
        """

        #First we'll rename and reformat the variables to be in a more standard kalman filter nomenclature (specifically that from Wu et al, 2003):
        #xs are the state (here, the variable we're predicting, i.e. y_train)
        #zs are the observed variable (neural data here, i.e. X_kf_train)
        X=np.matrix(y_train.T)
        Z=np.matrix(X_kf_train.T)

        #number of time bins
        nt=X.shape[1]

        #Calculate the transition matrix (from x_t to x_t+1) using least-squares, and compute its covariance
        #In our case, this is the transition from one kinematic state to the next
        X2 = X[:,1:]
        X1 = X[:,0:nt-1]
        A=X2*X1.T*inv(X1*X1.T) #Transition matrix
        W=(X2-A*X1)*(X2-A*X1).T/(nt-1)/self.C #Covariance of transition matrix. Note we divide by nt-1 since only nt-1 points were used in the computation (that's the length of X1 and X2). We also introduce the extra parameter C here.

        #Calculate the measurement matrix (from x_t to z_t) using least-squares, and compute its covariance
        #In our case, this is the transformation from kinematics to spikes
        H = Z*X.T*(inv(X*X.T)) #Measurement matrix
        Q = ((Z - H*X)*((Z - H*X).T)) / nt #Covariance of measurement matrix
        params=[A,W,H,Q]
        self.model=params

    def predict(self,X_kf_test,y_test):

        """
        Predict outcomes using trained Kalman Filter Decoder

        Parameters
        ----------
        X_kf_test: numpy 2d array of shape [n_samples(i.e. timebins) , n_neurons]
            This is the neural data in Kalman filter format.

        y_test: numpy 2d array of shape [n_samples(i.e. timebins),n_outputs]
            The actual outputs
            This parameter is necesary for the Kalman filter (unlike other decoders)
            because the first value is nececessary for initialization

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples(i.e. timebins),n_outputs]
            The predicted outputs
        """

        #Extract parameters
        A,W,H,Q=self.model

        #First we'll rename and reformat the variables to be in a more standard kalman filter nomenclature (specifically that from Wu et al):
        #xs are the state (here, the variable we're predicting, i.e. y_train)
        #zs are the observed variable (neural data here, i.e. X_kf_train)
        X=np.matrix(y_test.T)
        Z=np.matrix(X_kf_test.T)

        #Initializations
        num_states=X.shape[0] #Dimensionality of the state
        states=np.empty(X.shape) #Keep track of states over time (states is what will be returned as y_test_predicted)
        P_m=np.matrix(np.zeros([num_states,num_states]))
        P=np.matrix(np.zeros([num_states,num_states]))
        state=X[:,0] #Initial state
        states[:,0]=np.copy(np.squeeze(state))

        #Get predicted state for every time bin
        for t in range(X.shape[1]-1):
            #Do first part of state update - based on transition matrix
            P_m=A*P*A.T+W
            state_m=A*state

            #Do second part of state update - based on measurement matrix
            # K=P_m*H.T*inv(H*P_m*H.T+Q) #Calculate Kalman gain

            

            # 原来是：
            # K = P_m @ H.T @ np.linalg.inv(H @ P_m @ H.T + Q)

            # 改成稳健版：
            S = H @ P_m @ H.T + Q
            # 加正则，避免奇异
            S += 1e-6 * np.eye(S.shape[0])  

            K = P_m @ H.T @ np.linalg.inv(S)

            # K = P_m @ H.T @ np.linalg.pinv(H @ P_m @ H.T + Q)



            # from numpy.linalg import pinv
            # K = P_m @ H.T @ pinv(H @ P_m @ H.T + Q)


            P=(np.matrix(np.eye(num_states))-K*H)*P_m
            state=state_m+K*(Z[:,t+1]-H*state_m)
            states[:,t+1]=np.squeeze(state) #Record state at the timestep
        y_test_predicted=states.T
        return y_test_predicted
    
    def save(self, path):
        if self.model is None:
            raise RuntimeError("Model not fitted; cannot save an empty model.")

        A, W, H, Q = self.model

        save_dict = {
            "C": self.C,
            "A": A,
            "W": W,
            "H": H,
            "Q": Q,
        }

        torch.save(save_dict, path)
        print(f"[KalmanDecoder] Model saved to {path}")


    @classmethod
    def load(cls, path, map_location="cpu"):
        ckpt = torch.load(path, map_location=map_location)

        # 创建对象
        decoder = cls(
            C=ckpt["C"]
        )

        # 恢复模型参数
        decoder.model = [
            ckpt["A"],
            ckpt["W"],
            ckpt["H"],
            ckpt["Q"],
        ]

        print(f"[KalmanDecoder] Model loaded from {path}")

        return decoder
    
    # ======================================================
    # ✔ 严格模式 build_model
    # ======================================================
    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build KalmanFilterDecoder from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        # ---------- 构建模型 ----------
        return KalmanFilterDecoder(model_params.get("C", 1))





from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from numpy.linalg import inv, pinv

class KalmanDecoder:
    """
    Kalman filter decoding algorithm.

    Parameters
    ----------
        reg_type : str {'l1', 'l2', 'l12'}. Default None.
            regularization type.
            'l1' : Linear least squares with l1 regularization (i.e. Lasso).
            'l2' : Linear least squares with l2 regularization (i.e. Ridge).
            'l12' : Linear least squares with combined L1 and L2 regularization (i.e. Elastic Net).
        reg_alpha : float. Default 0.
            regularization constant/strength.
    """
    def __init__(self, reg_type=None, reg_alpha=0):
        self.reg_type = reg_type 
        self.reg_alpha = reg_alpha

    def fit(self, X_train, y_train):
        if self.reg_type == 'l1':
            regres = Lasso(alpha=self.alpha_reg)            
        elif self.reg_type == 'l2':
            regres = Ridge(alpha=self.alpha_reg)
        elif self.reg_type == 'l12':
            regres = ElasticNet(alpha=self.alpha_reg)
        else:
            regres = LinearRegression()
        
        X = y_train 
        Z = X_train 
        nt = X.shape[0]              
        X1 = X[:nt-1,:] 
        X2 = X[1:,:] 
        
        regres.fit(X1, X2)
        A = regres.coef_
        W = np.cov((X2 - np.dot(X1, A.T)).T)
        regres.fit(X, Z)
        H = regres.coef_ 
        Q = np.cov((Z - np.dot(X, H.T)).T) 
        self.model = [A, W, H, Q] 
    
    def predict(self, X_test, y_init):
        # extract parameters
        A, W, H, Q = self.model

        X = np.matrix(y_init.T)
        Z = np.matrix(X_test.T)

        # initialise states and covariance matrix
        n_states = X.shape[0] # dimensionality of the state
        states = np.empty((n_states, Z.shape[1])) # keep track of states over time (states is what will be returned as y_pred)
        P_m = np.matrix(np.zeros([n_states, n_states]))
        P = np.matrix(np.zeros([n_states, n_states]))
        state = X[:,0] # initial state
        states[:,0] = np.copy(np.squeeze(state))

        # get predicted state for every time bin
        for t in range(Z.shape[1]-1):
            # do first part of state update - based on transition matrix
            P_m = A*P*A.T + W
            state_m = A*state

            # do second part of state update - based on measurement matrix
            try:
                K = P_m*H.T*inv(H*P_m*H.T + Q) # calculate Kalman gain
            except np.linalg.LinAlgError:
                K = P_m*H.T*pinv(H*P_m*H.T+Q) # calculate Kalman gain
            P = (np.matrix(np.eye(n_states)) - K*H)*P_m
            state = state_m + K*(Z[:,t+1] - H*state_m)
            states[:,t+1] = np.squeeze(state) # record state at the timestep
        y_pred = states.T
        return y_pred



##################### DENSE (FULLY-CONNECTED) NEURAL NETWORK #########################



##################### SIMPLE RECURRENT NEURAL NETWORK ##########################



##################### GATED RECURRENT UNIT (GRU) DECODER #########################


#################### LONG SHORT TERM MEMORY (LSTM) DECODER #########################



##################### EXTREME GRADIENT BOOSTING (XGBOOST) ##########################

class XGBoostRegression(object):

    """
    Class for the XGBoost Decoder

    Parameters
    ----------
    max_depth: integer, optional, default=3
        the maximum depth of the trees

    num_round: integer, optional, default=300
        the number of trees that are fit

    eta: float, optional, default=0.3
        the learning rate

    gpu: integer, optional, default=-1
        if the gpu version of xgboost is installed, this can be used to select which gpu to use
        for negative values (default), the gpu is not used
    """

    def __init__(self,max_depth=3,num_round=300,eta=0.3,gpu=-1):
        self.max_depth=max_depth
        self.num_round=num_round
        self.eta=eta
        self.gpu=gpu

    def fit(self,X_flat_train,y_train):

        """
        Train XGBoost Decoder

        Parameters
        ----------
        X_flat_train: numpy 2d array of shape [n_samples,n_features]
            This is the neural data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples, n_outputs]
            This is the outputs that are being predicted
        """


        num_outputs=y_train.shape[1] #Number of outputs

        #Set parameters for XGBoost
        param = {'objective': "reg:linear", #for linear output
            'eval_metric': "logloss", #loglikelihood loss
            'max_depth': self.max_depth, #this is the only parameter we have set, it's one of the way or regularizing
            'eta': self.eta,
            'seed': 2925, #for reproducibility
            'silent': 1}
        if self.gpu<0:
            param['nthread'] = -1 #with -1 it will use all available threads
        else:
            param['gpu_id']=self.gpu
            param['updater']='grow_gpu'

        models=[] #Initialize list of models (there will be a separate model for each output)
        for y_idx in range(num_outputs): #Loop through outputs
            dtrain = xgb.DMatrix(X_flat_train, label=y_train[:,y_idx]) #Put in correct format for XGB
            bst = xgb.train(param, dtrain, self.num_round) #Train model
            models.append(bst) #Add fit model to list of models

        self.model=models


    def predict(self,X_flat_test):

        """
        Predict outcomes using trained XGBoost Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        dtest = xgb.DMatrix(X_flat_test) #Put in XGB format
        num_outputs=len(self.model) #Number of outputs
        y_test_predicted=np.empty([X_flat_test.shape[0],num_outputs]) #Initialize matrix of predicted outputs
        for y_idx in range(num_outputs): #Loop through outputs
            bst=self.model[y_idx] #Get fit model for this output
            y_test_predicted[:,y_idx] = bst.predict(dtest) #Make prediction
        return y_test_predicted


##################### SUPPORT VECTOR REGRESSION ##########################

class SVRegression(object):

    """
    Class for the Support Vector Regression (SVR) Decoder
    This simply leverages the scikit-learn SVR

    Parameters
    ----------
    C: float, default=3.0
        Penalty parameter of the error term

    max_iter: integer, default=-1
        the maximum number of iteraations to run (to save time)
        max_iter=-1 means no limit
        Typically in the 1000s takes a short amount of time on a laptop
    """

    def __init__(self,max_iter=-1,C=3.0):
        self.max_iter=max_iter
        self.C=C
        return


    def fit(self,X_flat_train,y_train):

        """
        Train SVR Decoder

        Parameters
        ----------
        X_flat_train: numpy 2d array of shape [n_samples,n_features]
            This is the neural data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples, n_outputs]
            This is the outputs that are being predicted
        """

        num_outputs=y_train.shape[1] #Number of outputs
        models=[] #Initialize list of models (there will be a separate model for each output)
        for y_idx in range(num_outputs): #Loop through outputs
            model=SVR(C=self.C, max_iter=self.max_iter) #Initialize SVR model
            model.fit(X_flat_train, y_train[:,y_idx]) #Train the model
            models.append(model) #Add fit model to list of models
        self.model=models


    def predict(self,X_flat_test):

        """
        Predict outcomes using trained SVR Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        num_outputs=len(self.model) #Number of outputs
        y_test_predicted=np.empty([X_flat_test.shape[0],num_outputs]) #Initialize matrix of predicted outputs
        for y_idx in range(num_outputs): #Loop through outputs
            model=self.model[y_idx] #Get fit model for that output
            y_test_predicted[:,y_idx]=model.predict(X_flat_test) #Make predictions
        return y_test_predicted




#GLM helper function for the NaiveBayesDecoder
def glm_run(Xr, Yr, X_range):

    X2 = sm.add_constant(Xr)

    poiss_model = sm.GLM(Yr, X2, family=sm.families.Poisson())
    try:
        glm_results = poiss_model.fit()
        Y_range=glm_results.predict(sm.add_constant(X_range))
    except np.linalg.LinAlgError:
        print("\nWARNING: LinAlgError")
        Y_range=np.mean(Yr)*np.ones([X_range.shape[0],1])

    return Y_range


class NaiveBayesRegression(object):

    """
    Class for the Naive Bayes Decoder

    Parameters
    ----------
    encoding_model: string, default='quadratic'
        what encoding model is used

    res:int, default=100
        resolution of predicted values
        This is the number of bins to divide the outputs into (going from minimum to maximum)
        larger values will make decoding slower
    """

    def __init__(self,encoding_model='quadratic',res=100):
        self.encoding_model=encoding_model
        self.res=res
        return

    def fit(self,X_b_train,y_train):

        """
        Train Naive Bayes Decoder

        Parameters
        ----------
        X_b_train: numpy 2d array of shape [n_samples,n_neurons]
            This is the neural training data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples, n_outputs]
            This is the outputs that are being predicted (training data)
        """

        #### FIT TUNING CURVE ####
        #First, get the output values (x/y position or velocity) that we will be creating tuning curves over
        #Create the range for x and y (position/velocity) values
        input_x_range=np.arange(np.min(y_train[:,0]),np.max(y_train[:,0])+.01,np.round((np.max(y_train[:,0])-np.min(y_train[:,0]))/self.res))
        input_y_range=np.arange(np.min(y_train[:,1]),np.max(y_train[:,1])+.01,np.round((np.max(y_train[:,1])-np.min(y_train[:,1]))/self.res))
        #Get all combinations of x/y values
        input_mat=np.meshgrid(input_x_range,input_y_range)
        #Format so that all combinations of x/y values are in 2 columns (first column x, second column y). This is called "input_xy"
        xs=np.reshape(input_mat[0],[input_x_range.shape[0]*input_y_range.shape[0],1])
        ys=np.reshape(input_mat[1],[input_x_range.shape[0]*input_y_range.shape[0],1])
        input_xy=np.concatenate((xs,ys),axis=1)

        #If quadratic model:
        #   -make covariates have squared components and mixture of x and y
        #   -do same thing for "input_xy", which are the values for creating the tuning curves
        if self.encoding_model=='quadratic':
            input_xy_modified=np.empty([input_xy.shape[0],5])
            input_xy_modified[:,0]=input_xy[:,0]**2
            input_xy_modified[:,1]=input_xy[:,0]
            input_xy_modified[:,2]=input_xy[:,1]**2
            input_xy_modified[:,3]=input_xy[:,1]
            input_xy_modified[:,4]=input_xy[:,0]*input_xy[:,1]
            y_train_modified=np.empty([y_train.shape[0],5])
            y_train_modified[:,0]=y_train[:,0]**2
            y_train_modified[:,1]=y_train[:,0]
            y_train_modified[:,2]=y_train[:,1]**2
            y_train_modified[:,3]=y_train[:,1]
            y_train_modified[:,4]=y_train[:,0]*y_train[:,1]

        #Create tuning curves

        num_nrns=X_b_train.shape[1] #Number of neurons to fit tuning curves for
        tuning_all=np.zeros([num_nrns,input_xy.shape[0]]) #Matrix that stores tuning curves for all neurons

        #Loop through neurons and fit tuning curves
        for j in range(num_nrns): #Neuron number

            if self.encoding_model=='linear':
                tuning=glm_run(y_train,X_b_train[:,j:j+1],input_xy)
            if self.encoding_model=='quadratic':
                tuning=glm_run(y_train_modified,X_b_train[:,j:j+1],input_xy_modified)
            #Enter tuning curves into matrix
            tuning_all[j,:]=np.squeeze(tuning)

        #Save tuning curves to be used in "predict" function
        self.tuning_all=tuning_all
        self.input_xy=input_xy

        #Get information about the probability of being in one state (position/velocity) based on the previous state
        #Here we're calculating the standard deviation of the change in state (velocity/acceleration) in the training set
        n=y_train.shape[0]
        dx=np.zeros([n-1,1])
        for i in range(n-1):
            dx[i]=np.sqrt((y_train[i+1,0]-y_train[i,0])**2+(y_train[i+1,1]-y_train[i,1])**2) #Change in state across time steps
        std=np.sqrt(np.mean(dx**2)) #dx is only positive. this gets approximate stdev of distribution (if it was positive and negative)
        self.std=std #Save for use in "predict" function

        #Get probability of being in each state - we are not using this since it did not help decoding performance
        # n_x=np.empty([input_xy.shape[0]])
        # for i in range(n):
        #     loc_idx=np.argmin(cdist(y_train[0:1,:],input_xy))
        #     n_x[loc_idx]=n_x[loc_idx]+1
        # p_x=n_x/n
        # self.p_x=p_x

    def predict(self,X_b_test,y_test):

        """
        Predict outcomes using trained tuning curves

        Parameters
        ----------
        X_b_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        y_test: numpy 2d array of shape [n_samples,n_outputs]
            The actual outputs
            This parameter is necesary for the NaiveBayesDecoder  (unlike most other decoders)
            because the first value is nececessary for initialization

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        #Get values saved in "fit" function
        tuning_all=self.tuning_all
        input_xy=self.input_xy
        std=self.std

        #Get probability of going from one state to the next
        dists = squareform(pdist(input_xy, 'euclidean')) #Distance between all states in "input_xy"
        #Probability of going from one state to the next, based on the above calculated distances
        #The probability is calculated based on the distances coming from a Gaussian with standard deviation of std
        prob_dists=norm.pdf(dists,0,std)

        #Initializations
        loc_idx= np.argmin(cdist(y_test[0:1,:],input_xy)) #The index of the first location
        num_nrns=tuning_all.shape[0] #Number of neurons
        y_test_predicted=np.empty([X_b_test.shape[0],2]) #Initialize matrix of predicted outputs
        num_ts=X_b_test.shape[0] #Number of time steps we are predicting

        #Loop across time and decode
        for t in range(num_ts):
            rs=X_b_test[t,:] #Number of spikes at this time point (in the interval we've specified including bins_before and bins_after)

            probs_total=np.ones([tuning_all[0,:].shape[0]]) #Vector that stores the probabilities of being in any state based on the neural activity (does not include probabilities of going from one state to the next)
            for j in range(num_nrns): #Loop across neurons
                lam=np.copy(tuning_all[j,:]) #Expected spike counts given the tuning curve
                r=rs[j] #Actual spike count
                probs=np.exp(-lam)*lam**r/math.factorial(r) #Probability of the given neuron's spike count given tuning curve (assuming poisson distribution)
                probs_total=np.copy(probs_total*probs) #Update the probability across neurons (probabilities are multiplied across neurons due to the independence assumption)
            prob_dists_vec=np.copy(prob_dists[loc_idx,:]) #Probability of going to all states from the previous state
            probs_final=probs_total*prob_dists_vec #Get final probability (multiply probabilities based on spike count and previous state)
            # probs_final=probs_total*prob_dists_vec*self.p_x #Get final probability when including p(x), i.e. prior about being in states, which we're not using
            loc_idx=np.argmax(probs_final) #Get the index of the current state (that w/ the highest probability)
            y_test_predicted[t,:]=input_xy[loc_idx,:] #The current predicted output

        return y_test_predicted #Return predictions



######### ALIASES for Regression ########

WienerFilterDecoder = WienerFilterRegression
WienerCascadeDecoder = WienerCascadeRegression
KalmanFilterDecoder = KalmanFilterRegression

XGBoostDecoder = XGBoostRegression
SVRDecoder = SVRegression
NaiveBayesDecoder = NaiveBayesRegression




####################################### CLASSIFICATION ####################################################




class WienerFilterClassification(object):

    """
    Class for the Wiener Filter Decoder

    There are no parameters to set.

    This simply leverages the scikit-learn logistic regression.
    """

    def __init__(self,C=1):
        self.C=C
        return


    def fit(self,X_flat_train,y_train):

        """
        Train Wiener Filter Decoder

        Parameters
        ----------
        X_flat_train: numpy 2d array of shape [n_samples,n_features]
            This is the neural data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples, n_outputs]
            This is the outputs that are being predicted
        """

        # if self.C>0:
        self.model=linear_model.LogisticRegression(C=self.C,multi_class='auto') #Initialize linear regression model
        # else:
            # self.model=linear_model.LogisticRegression(penalty='none',solver='newton-cg') #Initialize linear regression model
        self.model.fit(X_flat_train, y_train) #Train the model


    def predict(self,X_flat_test):

        """
        Predict outcomes using trained Wiener Cascade Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        y_test_predicted=self.model.predict(X_flat_test) #Make predictions
        return y_test_predicted




##################### SUPPORT VECTOR REGRESSION ##########################

class SVClassification(object):

    """
    Class for the Support Vector Classification Decoder
    This simply leverages the scikit-learn SVM

    Parameters
    ----------
    C: float, default=3.0
        Penalty parameter of the error term

    max_iter: integer, default=-1
        the maximum number of iteraations to run (to save time)
        max_iter=-1 means no limit
        Typically in the 1000s takes a short amount of time on a laptop
    """

    def __init__(self,max_iter=-1,C=3.0):
        self.max_iter=max_iter
        self.C=C
        return


    def fit(self,X_flat_train,y_train):

        """
        Train SVR Decoder

        Parameters
        ----------
        X_flat_train: numpy 2d array of shape [n_samples,n_features]
            This is the neural data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 2d array of shape [n_samples, n_outputs]
            This is the outputs that are being predicted
        """

        model=SVC(C=self.C, max_iter=self.max_iter) #Initialize model
        model.fit(X_flat_train, y_train) #Train the model
        self.model=model


    def predict(self,X_flat_test):

        """
        Predict outcomes using trained SV Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        model=self.model #Get fit model for that output
        y_test_predicted=model.predict(X_flat_test) #Make predictions
        return y_test_predicted


##################### DENSE (FULLY-CONNECTED) NEURAL NETWORK ##########################



##################### SIMPLE RNN DECODER ##########################







##################### GATED RECURRENT UNIT (GRU) DECODER ##########################






##################### EXTREME GRADIENT BOOSTING (XGBOOST) ##########################

class XGBoostClassification(object):
    """
    Class for the XGBoost Decoder

    Parameters
    ----------
    max_depth: integer, optional, default=3
        the maximum depth of the trees

    num_round: integer, optional, default=300
        the number of trees that are fit

    eta: float, optional, default=0.3
        the learning rate

    gpu: integer, optional, default=-1
        if the gpu version of xgboost is installed, this can be used to select which gpu to use
        for negative values (default), the gpu is not used
    """

    def __init__(self, max_depth=3, num_round=300, eta=0.3, gpu=-1):
        self.max_depth = max_depth
        self.num_round = num_round
        self.eta = eta
        self.gpu = gpu

    def fit(self, X_flat_train, y_train):

        """
        Train XGBoost Decoder

        Parameters
        ----------
        X_flat_train: numpy 2d array of shape [n_samples,n_features]
            This is the neural data.
            See example file for an example of how to format the neural data correctly

        y_train: numpy 1d array of shape (n_samples), with integers representing classes
                    or 2d array of shape [n_samples, n_outputs] in 1-hot form
            This is the outputs that are being predicted
        """

        # turn to categorial (not 1-hat)
        if (y_train.ndim == 2):
            if (y_train.shape[1] == 1):
                y_train = np.reshape(y_train, -1)
            else:
                y_train = np.argmax(y_train, axis=1, out=None)

        # Get number of classes
        n_classes = len(np.unique(y_train))

        # Set parameters for XGBoost
        param = {'objective': "multi:softmax",  # or softprob
                 'eval_metric': "mlogloss",  # loglikelihood loss
                 # 'eval_metric': "merror",
                 'max_depth': self.max_depth, # this is the only parameter we have set, it's one of the way or regularizing
                 'eta': self.eta,
                 'num_class': n_classes,  # y_train.shape[1],
                 'seed': 2925,  # for reproducibility
                 'silent': 1}
        if self.gpu < 0:
            param['nthread'] = -1  # with -1 it will use all available threads
        else:
            param['gpu_id'] = self.gpu
            param['updater'] = 'grow_gpu'

        dtrain = xgb.DMatrix(X_flat_train, label=y_train)  # Put in correct format for XGB
        bst = xgb.train(param, dtrain, self.num_round)  # Train model

        self.model = bst

    def predict(self, X_flat_test):

        """
        Predict outcomes using trained XGBoost Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 1d array with integers as classes
            The predicted outputs
        """

        dtest = xgb.DMatrix(X_flat_test)  # Put in XGB format
        bst = self.model  # Get fit model
        y_test_predicted = bst.predict(dtest)  # Make prediction
        return y_test_predicted

    def predict(self,X_flat_test):

        """
        Predict outcomes using trained XGBoost Decoder

        Parameters
        ----------
        X_flat_test: numpy 2d array of shape [n_samples,n_features]
            This is the neural data being used to predict outputs.

        Returns
        -------
        y_test_predicted: numpy 2d array of shape [n_samples,n_outputs]
            The predicted outputs
        """

        dtest = xgb.DMatrix(X_flat_test) #Put in XGB format
        bst=self.model #Get fit model
        y_test_predicted = bst.predict(dtest) #Make prediction
        return y_test_predicted
