import numpy as np
from sklearn.metrics import r2_score, accuracy_score
from sklearn.model_selection import KFold
from scipy.optimize import least_squares

def relu(x):
    return (np.maximum(0, x))

def flatten_list(X):
    """
    Converting list containing multiple ndarrays into a large ndarray
    X: a list
    return: a numpy ndarray
    """
    n_col = np.size(X[0],1)
    Y = np.empty((0, n_col))
    for each in X:
        Y = np.vstack((Y, each))
    return Y

def format_data(x, y, n_lag):
    """
    To reshape the numpy arrays for Wiener filter fitting
    Parameters
        x: the input data for Wiener filter fitting, an ndarray
        y: the output data for Wiener filter fitting, an ndarray
        n_lag: the number of time lags, an int number
    Returns:
        out1: the reshaped array for x, an ndarray
        out2: the trimmed array for y, an ndarray
    """
    x_ = [x[i:i+n_lag, :].reshape(n_lag*x.shape[1]) for i in range(x.shape[0]-n_lag+1)]
    return np.asarray(x_), y[n_lag-1:, :]

def format_data_from_list(x, y, n_lag):
    if type(x) == np.ndarray:
        x = [x]
    if type(y) == np.ndarray:
        y = [y]
    x_, y_ = [], []
    for each in zip(x, y):
        temp = format_data(each[0], each[1], n_lag)
        x_.append(temp[0])
        y_.append(temp[1])
    return np.concatenate(x_), np.concatenate(y_)

def format_data_from_trials(x, y, n_lag):
    """
    To reshape lists containing multiple trials into a big array so as to form 
    the training data for Wiener filter fitting
    Parameters
        x: a list containing multiple trials, as the inputs for Wiener filter fitting
        y: a list containing multiple trials, as the outputs for Wiener filter fitting
        n_lag: the number of time lags, an int number
    Returns
        out1: the reshaped data for the input list x, an ndarray
        out2: the reshaped data for the input list y, an ndarray
    """
    if type(x) == np.ndarray:
        x = [x]
    if type(y) == np.ndarray:
        y = [y]
    x_, y_ = [], []
    for each in zip(x, y):
        temp = format_data(each[0], each[1], n_lag)
        x_.append(temp[0])
        y_.append(temp[1])
    return np.concatenate(x_), np.concatenate(y_)

def parameter_fit(x, y, c):
    """
    c : L2 regularization coefficient
    I : Identity Matrix
    Linear Least Squares (code defaults to this if c is not passed)
    H = ( X^T * X )^-1 * X^T * Y
    Ridge Regression
    R = c * I
    ridge regression doesn't penalize x
    R[0,0] = 0
    H = ( (X^T * X) + R )^-1 * X^T * Y
    """
    x_plus_bias = np.c_[np.ones((np.size(x, 0), 1)), x]
    R = c * np.eye( x_plus_bias.shape[1] )
    R[0,0] = 0;
    temp = np.linalg.inv(np.dot(x_plus_bias.T, x_plus_bias) + R)
    temp2 = np.dot(temp,x_plus_bias.T)
    H = np.dot(temp2,y)
    return H

def parameter_fit_with_sweep( x, y, C, kf ):
    reg_r2 = []
    print ('Sweeping ridge regularization using CV decoding on train data' )
    for c in C:
        print( 'Testing c= ' + str(c) )
        cv_r2 = []
        for train_indices, test_indices in kf.split(x):
            # split data into train and test
            train_x, test_x = x[train_indices,:], x[test_indices,:]
            train_y, test_y = y[train_indices,:], y[test_indices,:]
            # fit decoder
            H = parameter_fit(train_x, train_y, c)
            #print( H.shape )
            # predict
            test_y_pred = test_wiener_filter(test_x, H)
            # evaluate performance
            cv_r2.append(r2_score(test_y, test_y_pred, multioutput='raw_values'))
        # append mean of CV decoding for output
        cv_r2 = np.asarray(cv_r2)
        reg_r2.append( np.mean( cv_r2, axis=0 ) )

    reg_r2 = np.asarray(reg_r2)        
    reg_r2 = np.mean( reg_r2, axis=1 )
    best_c = C[ np.argmax( reg_r2 ) ] 
    return best_c

def train_wiener_filter(x, y, l2 = 0):
    """
    To train a linear decoder
    x: input data, e.g. neural firing rates
    y: expected results, e.g. true EMG values
    l2: 0 or 1, switch for turning L2 regularization on or off
    """
    if l2 == 1:
        n_l2 = 20
        C = np.logspace( 1, 5, n_l2 )
        kfolds = 4
        kf = KFold( n_splits = kfolds )
        best_c = parameter_fit_with_sweep( x, y, C, kf )
        print(best_c)
    else:
        best_c = 0
    H_reg = parameter_fit( x, y, best_c )
    return H_reg
   
def test_wiener_filter(x, H):
    """
    To get predictions from input data x with linear decoder
    x: input data
    H: parameter vector obtained by training
    """
    x_plus_bias = np.c_[np.ones((np.size(x, 0), 1)), x]
    y_pred = np.dot(x_plus_bias, H)
    return y_pred    
      
def nonlinearity(p, y, nonlinear_type = 'poly2'):
    if nonlinear_type == 'poly':
        print('Version updated, please specify if you need poly 2 or poly 3')
        return None
    elif nonlinear_type == 'poly2':
        return p[0]+p[1]*y+p[2]*y*y
    elif nonlinear_type == 'poly3':
        return p[0]+p[1]*y+p[2]*y**2+p[3]*y**3
    elif nonlinear_type == 'sigmoid':
        return 1/( 1+np.exp(-10*(y-p[0])) )
    
def nonlinearity_residue(p, y, z, nonlinear_type = 'poly2'):
    return (nonlinearity(p, y, nonlinear_type) - z).reshape((-1,))

def train_nonlinear_wiener_filter(x, y, l2 = 0, nonlinear_type = 'poly2'):
    """
    To train a nonlinear decoder
    x: input data, e.g. neural firing rates
    y: expected results, e.g. true EMG values
    l2: 0 or 1, switch for turning L2 regularization on or off
    """
    if l2 == 1:
        n_l2 = 20
        C = np.logspace( 1, 5, n_l2 )
        kfolds = 4
        kf = KFold( n_splits = kfolds )
        best_c = parameter_fit_with_sweep( x, y, C, kf )
        print(best_c)
    else:
        best_c = 0
    H_reg = parameter_fit( x, y, best_c )
    y_pred = test_wiener_filter(x, H_reg)
    if nonlinear_type == 'relu':
        return H_reg
    else:
        if nonlinear_type == 'poly':
            print('Version updated. Please specify if you want poly-2 or poly-3')
            init = [0, 0]
        elif nonlinear_type == 'poly2':
            init = [0.1, 0.1, 0.1]
        elif nonlinear_type == 'poly3':
            init = [0.1, 0.1, 0.1, 0.1]
        elif nonlinear_type == 'sigmoid':
            init = [0.5]
        res_lsq = least_squares(nonlinearity_residue, init, args = (y_pred, y, nonlinear_type))
        return H_reg, res_lsq

def test_nonlinear_wiener_filter(x, H, res_lsq, nonlinear_type = 'poly2'):  
    """
    To get predictions from input data x with nonlinear decoder
    x: input data
    H: parameter vector obtained by training
    res_lsq: nonlinear components obtained by training
    """
    y1 = test_wiener_filter(x, H)
    if nonlinear_type == 'relu':
        y2 = relu(y1)
    else:
        y2 = nonlinearity(res_lsq.x, y1, nonlinear_type)
    return y2    
    
    
    
    


import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import os
import glob
from torch.utils.data import DataLoader

class Generator(nn.Module):
    def __init__(self, input_dim, hidden_dim, drop_out):
        """
        input_dim: the number of input channels.
        hidden_dim: the number of neurons in the hidden layer.
        drop_out: drop-out rate.
        """
        super(Generator, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.drop_out = drop_out
        self.model = nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dim),
            nn.Dropout(self.drop_out),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.Dropout(self.drop_out),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.input_dim),
            nn.ReLU()
        )

    def forward(self, input):
        """
        input: spike firing rate data
        x: transformed spike firing rate data
        """
        x = self.model(input)
        return x



class Discriminator(nn.Module):
    def __init__(self, input_dim, hidden_dim, drop_out):
        """
        input_dim: the number of input channels.
        hidden_dim: the number of neurons in the hidden layer.
        drop_out: drop-out rate.
        """
        super(Discriminator, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.drop_out = drop_out
        self.model = nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dim),
            nn.Dropout(self.drop_out),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.Dropout(self.drop_out),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, 1)
        )

    def forward(self, input):
        """
        input: spike firing rate data
        return: a label indicating if the input data is real or fake
        """
        label = self.model(input)
        return label


def train_cycle_gan_aligner(x1, x2, y2, D_params, G_params, training_params, decoder, n_lags, logs=True):
    """
    x1: M1 spike firing rates on day-0. A list, where each item is a numpy array containing the neural data of one trial

    x2: M1 spike firing rates on day-k. A list, where each item is a numpy array containing the neural data of one trial
        x2 will be divided into two portions (ratio 3:1), where the first portion will be used to train the aligner, and
        the second portion will be used as the validation set.

    y2: EMGs on day-k. A list, where each item is a numpy array containing the EMGs of one trial. Only a portion of y2
        (those corresponding to the trials used as the validation set) will be used.

    D_params: the hyper-parameters determining the structure of the discriminators, a dictionary.

    G_params: the hyper-parameters determining the structure of the generators, a dictionary.

    training_parameters: the hyper-parameters controlling the training process, a dictionary.

    decoder: the day-0 decoder to be tested on the validation set, an array.

    n_lags: the number of time lags of the decoder, a number.

    logs: to indicate if training logs is needed to be recorded as a .pkl file, a bool.

    return: a trained "aligner" (generator) for day-k use.
    """
    # ============================================= Specifying hyper-parameters =============================================
    D_hidden_dim = D_params['hidden_dim']
    G_hidden_dim = G_params['hidden_dim']
    loss_type = training_params['loss_type']
    optim_type = training_params['optim_type']
    epochs = training_params['epochs']
    batch_size = training_params['batch_size']
    D_lr = training_params['D_lr']
    G_lr = training_params['G_lr']
    ID_loss_p = training_params['ID_loss_p']
    cycle_loss_p = training_params['cycle_loss_p']
    drop_out_D = training_params['drop_out_D']
    drop_out_G = training_params['drop_out_G']

    # ============================================= Defining networks ===================================================
    x_dim = x1[0].shape[1]
    generator1, generator2 = Generator(x_dim, G_hidden_dim, drop_out_G), Generator(x_dim, G_hidden_dim, drop_out_G)
    discriminator1, discriminator2 = Discriminator(x_dim, D_hidden_dim, drop_out_D), Discriminator(x_dim, D_hidden_dim,
                                                                                                   drop_out_D)

    # ==================================== Specifying the type of the losses ===============================================
    if loss_type == 'L1':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.L1Loss()
        criterion_identity = torch.nn.L1Loss()
    elif loss_type == 'MSE':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.MSELoss()
        criterion_identity = torch.nn.MSELoss()

    # ====================================== Specifying the type of the optimizer ==============================================
    if optim_type == 'SGD':
        gen1_optim = optim.SGD(generator1.parameters(), lr=G_lr, momentum=0.9)
        gen2_optim = optim.SGD(generator2.parameters(), lr=G_lr, momentum=0.9)
        dis1_optim = optim.SGD(discriminator1.parameters(), lr=D_lr, momentum=0.9)
        dis2_optim = optim.SGD(discriminator2.parameters(), lr=D_lr, momentum=0.9)
    elif optim_type == 'Adam':
        gen1_optim = optim.Adam(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.Adam(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.Adam(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.Adam(discriminator2.parameters(), lr=D_lr)
    elif optim_type == 'RMSProp':
        gen1_optim = optim.RMSprop(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.RMSprop(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.RMSprop(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.RMSprop(discriminator2.parameters(), lr=D_lr)

    # =============================== Split x2 into the actual training set and the validation set ==============================
    # ----------- x2_train will be used in Cycle-GAN training -------------
    x2_train = x2[:int(len(x2) * 0.75)]  # training set

    # ------- x2_valid and y2_valid will be isolated from training, and used to test the performance of the aligner every 10 trials
    x2_valid, y2_valid = x2[int(len(x2) * 0.75):], y2[int(len(x2) * 0.75):]  # validation set

    # ================================================  Define data Loaders ======================================================
    x1, x2_train = np.concatenate(x1), np.concatenate(x2_train)

    # print("x1.shape----------------", x1.shape)
    # print("x2_train.shape----------------", x2_train.shape)

    # --------------- loader1 is for day-0 data ---------------------
    loader1 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x1)), batch_size=batch_size, shuffle=True)
    # --------------- loader2 is for day-k data in the training set ---------------------
    loader2 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x2_train)), batch_size=batch_size, shuffle=True)

    # ============================================ Training logs =========================================================
    train_log = {'epoch': [], 'batch_idx': [],
                 'loss D1': [], 'loss D2': [],
                 'loss G1': [], 'loss G2': [],
                 'loss cycle 121': [], 'loss cycle 212': [],
                 'decoder r2 wiener': [],
                 'decoder r2 rnn': []}

    # ============================================ Preparing to train ========================================================
    generator1.train()
    generator2.train()
    discriminator1.train()
    discriminator2.train()
    aligner_list = []
    mr2_all_list = []

    # ================================================== The training loop ====================================================
    for epoch in range(epochs):
        for batch_idx, (data1_, data2_) in enumerate(zip(loader1, loader2)):
            # ========================= loader1 and loader2 will yield mini-batches of data when running =========================
            # ------ The batches by loader1 will be stored in data1, while the batches by loader2 will be stored in data2 ------
            data1, data2 = data1_[0], data2_[0]
            if data1.__len__() != data2.__len__():
                continue
            # ------------ The labels for real samples --------------
            target_real = torch.ones((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')
            # ------------ The labels for fake samples --------------
            target_fake = torch.zeros((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')

            # ================================================== Generators ==================================================
            gen1_optim.zero_grad()
            gen2_optim.zero_grad()

            # ------------ Identity loss, to make sure the generators do not distort the inputs --------------
            same2 = generator1(data2)
            loss_identity2 = criterion_identity(same2, data2) * ID_loss_p
            same1 = generator2(data1)
            loss_identity1 = criterion_identity(same1, data1) * ID_loss_p

            # ------------ GAN loss for generator1, see the figure right above --------------
            fake2 = generator1(data1)
            pred_fake = discriminator2(fake2)
            loss_GAN2 = criterion_GAN(pred_fake, target_real)

            # ------------ GAN loss for generator2, see the figure right above --------------
            fake1 = generator2(data2)
            pred_fake = discriminator1(fake1)
            loss_GAN1 = criterion_GAN(pred_fake, target_real)

            # ------------ Cycle loss, see the figure right above --------------
            recovered1 = generator2(fake2)
            loss_cycle_121 = criterion_cycle(recovered1, data1) * cycle_loss_p

            recovered2 = generator1(fake1)
            loss_cycle_212 = criterion_cycle(recovered2, data2) * cycle_loss_p

            # ----------- Total loss of G, the sum of all the losses defined above -----------
            loss_G = loss_identity1 + loss_identity2 + loss_GAN1 + loss_GAN2 + loss_cycle_121 + loss_cycle_212

            # -------- Backward() and step() for generators ---------
            loss_G.backward()
            gen1_optim.step()
            gen2_optim.step()

            # ================================================== Discriminator 1 ==================================================
            dis1_optim.zero_grad()

            # -------------- Adversarial loss from discriminator 1, see the figure above ------------------
            pred_real = discriminator1(data1)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator1(generator2(data2).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D1 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator1 ---------
            loss_D1.backward()
            dis1_optim.step()

            # -------------- Adversarial loss from discriminator 2, see the figure above ------------------
            dis2_optim.zero_grad()

            pred_real = discriminator2(data2)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator2(generator1(data1).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D2 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator2 ---------
            loss_D2.backward()
            dis2_optim.step()

            # ====================================== save the training logs ========================================
            if logs == True:
                train_log['epoch'].append(epoch)
                train_log['batch_idx'].append(batch_idx)
                train_log['loss D1'].append(loss_D1.item())
                train_log['loss D2'].append(loss_D2.item())
                train_log['loss G1'].append(loss_GAN1.item())
                train_log['loss G2'].append(loss_GAN2.item())
                train_log['loss cycle 121'].append(loss_cycle_121.item())
                train_log['loss cycle 212'].append(loss_cycle_212.item())

        # ================ Test the aligner every 10 epoches on the validation set ====================
        if (epoch + 1) % 10 == 0:
            # ---------- Put generator2, namely the aligner, into evaluation mode ------------
            generator2.eval()

            # ---------- Use the trained aligner to transform the trials in x2_valid -----------
            # print(x2_valid.shape)
            x2_valid_aligned = []
            with torch.no_grad():
                for each in x2_valid:
                    data = torch.from_numpy(each).type('torch.FloatTensor')
                    x2_valid_aligned.append(generator2(data).numpy())

            # --------- Feed the day-0 decoder with x2_valid_aligned to evaluate the performance of the aligner ----------
            # print(x2_valid_aligned.shape)
            # x2_valid_aligned = np.concatenate(x2_valid_aligned)


            # y2_valid = [y2_valid[i] for i in range(len(y2_valid))]

            x2_valid_aligned_, y2_valid_ = format_data_from_trials(x2_valid_aligned, y2_valid, n_lags)
            pred_y2_valid_ = test_wiener_filter(x2_valid_aligned_, decoder)

            # --------- Compute the multi-variate R2 between pred_y2_valid (predicted EMGs) and y2_valid (real EMGs) ----------



            # print(y2_valid_.shape, pred_y2_valid_.shape)
            mr2 = r2_score(y2_valid_, pred_y2_valid_, multioutput='variance_weighted')
            print('On the %dth epoch, the R\u00b2 on the validation set is %.2f' % (epoch + 1, mr2))

            # ------- Save the half-trained aligners and the corresponding performance on the validation set ---------
            aligner_list.append(generator2)
            mr2_all_list.append(mr2)

            # ---------- Put generator2 back into training mode after finishing the evaluation -----------
            generator2.train()

    IDX = np.argmax(mr2_all_list)
    # print("mr2_all_list---------------------", mr2_all_list)
    print('The aligner has been well trained on the %dth epoch' % (IDX * 10))
    # train_log['decoder r2 wiener'] = mr2_all_list
    # ============================================ save the training log =================================================
    # if logs == True:
    #     dt_string = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    #     with open('./model_logs/train_logs/train_log_' + dt_string + '.pkl', 'wb') as fp:
    #         pickle.dump(train_log, fp)

    return aligner_list[IDX]





def test_cycle_gan_aligner(net, dayk_data):
    """
    net: the trained aligner
    dayk_data: the data that needs to be processed by the trained aligner
    """
    # ------ Put the net in eval mode ------ #
    aligner = net.eval()
    dayk_aligned = []

    # ------ Use the trained aligner to process the dayk_data ------#
    with torch.no_grad():
        for each in dayk_data:
            data_tensor = torch.from_numpy(each).type('torch.FloatTensor')
            dayk_aligned.append(aligner(data_tensor).numpy())

    # ------ Return the aligned day-k data --------#
    return dayk_aligned





def train_cycle_gan_aligner_Merge(x1, y1, x2, y2, D_params, G_params, training_params, decoder, n_lags, logs=True):
    """
    x1: M1 spike firing rates on day-0. A list, where each item is a numpy array containing the neural data of one trial

    x2: M1 spike firing rates on day-k. A list, where each item is a numpy array containing the neural data of one trial
        x2 will be divided into two portions (ratio 3:1), where the first portion will be used to train the aligner, and
        the second portion will be used as the validation set.

    y2: EMGs on day-k. A list, where each item is a numpy array containing the EMGs of one trial. Only a portion of y2
        (those corresponding to the trials used as the validation set) will be used.

    D_params: the hyper-parameters determining the structure of the discriminators, a dictionary.

    G_params: the hyper-parameters determining the structure of the generators, a dictionary.

    training_parameters: the hyper-parameters controlling the training process, a dictionary.

    decoder: the day-0 decoder to be tested on the validation set, an array.

    n_lags: the number of time lags of the decoder, a number.

    logs: to indicate if training logs is needed to be recorded as a .pkl file, a bool.

    return: a trained "aligner" (generator) for day-k use.
    """
    # ============================================= Specifying hyper-parameters =============================================
    D_hidden_dim = D_params['hidden_dim']
    G_hidden_dim = G_params['hidden_dim']
    loss_type = training_params['loss_type']
    optim_type = training_params['optim_type']
    epochs = training_params['epochs']
    batch_size = training_params['batch_size']
    D_lr = training_params['D_lr']
    G_lr = training_params['G_lr']
    ID_loss_p = training_params['ID_loss_p']
    cycle_loss_p = training_params['cycle_loss_p']
    drop_out_D = training_params['drop_out_D']
    drop_out_G = training_params['drop_out_G']

    # ============================================= Defining networks ===================================================
    x_dim = x1[0].shape[1]
    generator1, generator2 = Generator(x_dim, G_hidden_dim, drop_out_G), Generator(x_dim, G_hidden_dim, drop_out_G)
    discriminator1, discriminator2 = Discriminator(x_dim, D_hidden_dim, drop_out_D), Discriminator(x_dim, D_hidden_dim,
                                                                                                   drop_out_D)

    # ==================================== Specifying the type of the losses ===============================================
    if loss_type == 'L1':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.L1Loss()
        criterion_identity = torch.nn.L1Loss()
    elif loss_type == 'MSE':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.MSELoss()
        criterion_identity = torch.nn.MSELoss()

    # ====================================== Specifying the type of the optimizer ==============================================
    if optim_type == 'SGD':
        gen1_optim = optim.SGD(generator1.parameters(), lr=G_lr, momentum=0.9)
        gen2_optim = optim.SGD(generator2.parameters(), lr=G_lr, momentum=0.9)
        dis1_optim = optim.SGD(discriminator1.parameters(), lr=D_lr, momentum=0.9)
        dis2_optim = optim.SGD(discriminator2.parameters(), lr=D_lr, momentum=0.9)
    elif optim_type == 'Adam':
        gen1_optim = optim.Adam(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.Adam(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.Adam(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.Adam(discriminator2.parameters(), lr=D_lr)
    elif optim_type == 'RMSProp':
        gen1_optim = optim.RMSprop(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.RMSprop(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.RMSprop(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.RMSprop(discriminator2.parameters(), lr=D_lr)



    # decoder = WienerFilterDecoder(n_lags=4, l2=1.0)

    decoder.fit(x1[:int(0.75*len(x1))], y1[:int(0.75*len(y1))] ,x1[int(0.75*len(x1)):], y1[int(0.75*len(y1)):] )
    dayk_On_day0_mr2 = decoder.evaluate(x2[int(0.75*len(x2)):], y2[int(0.75*len(y2)):])
    print("Dayk R2 eval on Day0:", dayk_On_day0_mr2)


    x1 = x1[:int(0.75*len(x1))]
    y1 = y1[:int(0.75*len(y1))]
    x2 = x2[:int(0.75*len(x2))]
    y2 = y2[:int(0.75*len(y2))]

    # =============================== Split x2 into the actual training set and the validation set ==============================
    # ----------- x2_train will be used in Cycle-GAN training -------------
    x2_train = x2[:int(len(x2) * 0.75)]  # training set

    # ------- x2_valid and y2_valid will be isolated from training, and used to test the performance of the aligner every 10 trials
    x2_valid, y2_valid = x2[int(len(x2) * 0.75):], y2[int(len(x2) * 0.75):]  # validation set

    # ================================================  Define data Loaders ======================================================
    x1, x2_train = np.concatenate(x1), np.concatenate(x2_train)

    # print("x1.shape----------------", x1.shape)
    # print("x2_train.shape----------------", x2_train.shape)

    # --------------- loader1 is for day-0 data ---------------------
    loader1 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x1)), batch_size=batch_size, shuffle=True)
    # --------------- loader2 is for day-k data in the training set ---------------------
    loader2 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x2_train)), batch_size=batch_size, shuffle=True)

    # ============================================ Training logs =========================================================
    train_log = {'epoch': [], 'batch_idx': [],
                 'loss D1': [], 'loss D2': [],
                 'loss G1': [], 'loss G2': [],
                 'loss cycle 121': [], 'loss cycle 212': [],
                 'decoder r2 wiener': [],
                 'decoder r2 rnn': []}

    # ============================================ Preparing to train ========================================================
    generator1.train()
    generator2.train()
    discriminator1.train()
    discriminator2.train()
    aligner_list = []
    mr2_all_list = []

    # ================================================== The training loop ====================================================
    for epoch in range(epochs):
        for batch_idx, (data1_, data2_) in enumerate(zip(loader1, loader2)):
            # ========================= loader1 and loader2 will yield mini-batches of data when running =========================
            # ------ The batches by loader1 will be stored in data1, while the batches by loader2 will be stored in data2 ------
            data1, data2 = data1_[0], data2_[0]
            if data1.__len__() != data2.__len__():
                continue
            # ------------ The labels for real samples --------------
            target_real = torch.ones((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')
            # ------------ The labels for fake samples --------------
            target_fake = torch.zeros((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')

            # ================================================== Generators ==================================================
            gen1_optim.zero_grad()
            gen2_optim.zero_grad()

            # ------------ Identity loss, to make sure the generators do not distort the inputs --------------
            same2 = generator1(data2)
            loss_identity2 = criterion_identity(same2, data2) * ID_loss_p
            same1 = generator2(data1)
            loss_identity1 = criterion_identity(same1, data1) * ID_loss_p

            # ------------ GAN loss for generator1, see the figure right above --------------
            fake2 = generator1(data1)
            pred_fake = discriminator2(fake2)
            loss_GAN2 = criterion_GAN(pred_fake, target_real)

            # ------------ GAN loss for generator2, see the figure right above --------------
            fake1 = generator2(data2)
            pred_fake = discriminator1(fake1)
            loss_GAN1 = criterion_GAN(pred_fake, target_real)

            # ------------ Cycle loss, see the figure right above --------------
            recovered1 = generator2(fake2)
            loss_cycle_121 = criterion_cycle(recovered1, data1) * cycle_loss_p

            recovered2 = generator1(fake1)
            loss_cycle_212 = criterion_cycle(recovered2, data2) * cycle_loss_p

            # ----------- Total loss of G, the sum of all the losses defined above -----------
            loss_G = loss_identity1 + loss_identity2 + loss_GAN1 + loss_GAN2 + loss_cycle_121 + loss_cycle_212

            # -------- Backward() and step() for generators ---------
            loss_G.backward()
            gen1_optim.step()
            gen2_optim.step()

            # ================================================== Discriminator 1 ==================================================
            dis1_optim.zero_grad()

            # -------------- Adversarial loss from discriminator 1, see the figure above ------------------
            pred_real = discriminator1(data1)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator1(generator2(data2).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D1 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator1 ---------
            loss_D1.backward()
            dis1_optim.step()

            # -------------- Adversarial loss from discriminator 2, see the figure above ------------------
            dis2_optim.zero_grad()

            pred_real = discriminator2(data2)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator2(generator1(data1).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D2 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator2 ---------
            loss_D2.backward()
            dis2_optim.step()

            # ====================================== save the training logs ========================================
            if logs == True:
                train_log['epoch'].append(epoch)
                train_log['batch_idx'].append(batch_idx)
                train_log['loss D1'].append(loss_D1.item())
                train_log['loss D2'].append(loss_D2.item())
                train_log['loss G1'].append(loss_GAN1.item())
                train_log['loss G2'].append(loss_GAN2.item())
                train_log['loss cycle 121'].append(loss_cycle_121.item())
                train_log['loss cycle 212'].append(loss_cycle_212.item())

        # ================ Test the aligner every 10 epoches on the validation set ====================
        if (epoch + 1) % 10 == 0:
            # ---------- Put generator2, namely the aligner, into evaluation mode ------------
            generator2.eval()

            # ---------- Use the trained aligner to transform the trials in x2_valid -----------
            # print(x2_valid.shape)
            x2_valid_aligned = []
            with torch.no_grad():
                for each in x2_valid:
                    data = torch.from_numpy(each).type('torch.FloatTensor')
                    x2_valid_aligned.append(generator2(data).numpy())

            # --------- Feed the day-0 decoder with x2_valid_aligned to evaluate the performance of the aligner ----------
            # print(x2_valid_aligned.shape)
            # x2_valid_aligned = np.concatenate(x2_valid_aligned)


            # y2_valid = [y2_valid[i] for i in range(len(y2_valid))]

            x2_valid_aligned_, y2_valid_ = format_data_from_trials(x2_valid_aligned, y2_valid, n_lags)
            pred_y2_valid_ = test_wiener_filter(x2_valid_aligned_, decoder.best_H)

            # --------- Compute the multi-variate R2 between pred_y2_valid (predicted EMGs) and y2_valid (real EMGs) ----------



            # print(y2_valid_.shape, pred_y2_valid_.shape)
            mr2 = r2_score(y2_valid_, pred_y2_valid_, multioutput='variance_weighted')
            print('On the %dth epoch, the R\u00b2 on the validation set is %.2f' % (epoch + 1, mr2))

            # ------- Save the half-trained aligners and the corresponding performance on the validation set ---------
            aligner_list.append(generator2)
            mr2_all_list.append(mr2)

            # ---------- Put generator2 back into training mode after finishing the evaluation -----------
            generator2.train()

    IDX = np.argmax(mr2_all_list)
    # print("mr2_all_list---------------------", mr2_all_list)
    print('The aligner has been well trained on the %dth epoch' % (IDX * 10))
    # train_log['decoder r2 wiener'] = mr2_all_list
    # ============================================ save the training log =================================================
    # if logs == True:
    #     dt_string = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    #     with open('./model_logs/train_logs/train_log_' + dt_string + '.pkl', 'wb') as fp:
    #         pickle.dump(train_log, fp)

    return aligner_list[IDX], decoder.best_H, dayk_On_day0_mr2



from sklearn.model_selection import KFold
from sklearn.metrics import r2_score

def train_cycle_gan_aligner_Merge_Pth(x1, y1, x2, y2, D_params, G_params, training_params, decoder, n_lags, decoder_pth, logs=True):
    """
    x1: M1 spike firing rates on day-0. A list, where each item is a numpy array containing the neural data of one trial

    x2: M1 spike firing rates on day-k. A list, where each item is a numpy array containing the neural data of one trial
        x2 will be divided into two portions (ratio 3:1), where the first portion will be used to train the aligner, and
        the second portion will be used as the validation set.

    y2: EMGs on day-k. A list, where each item is a numpy array containing the EMGs of one trial. Only a portion of y2
        (those corresponding to the trials used as the validation set) will be used.

    D_params: the hyper-parameters determining the structure of the discriminators, a dictionary.

    G_params: the hyper-parameters determining the structure of the generators, a dictionary.

    training_parameters: the hyper-parameters controlling the training process, a dictionary.

    decoder: the day-0 decoder to be tested on the validation set, an array.

    n_lags: the number of time lags of the decoder, a number.

    logs: to indicate if training logs is needed to be recorded as a .pkl file, a bool.

    return: a trained "aligner" (generator) for day-k use.
    """
    # ============================================= Specifying hyper-parameters =============================================
    D_hidden_dim = D_params['hidden_dim']
    G_hidden_dim = G_params['hidden_dim']
    loss_type = training_params['loss_type']
    optim_type = training_params['optim_type']
    epochs = training_params['epochs']
    batch_size = training_params['batch_size']
    D_lr = training_params['D_lr']
    G_lr = training_params['G_lr']
    ID_loss_p = training_params['ID_loss_p']
    cycle_loss_p = training_params['cycle_loss_p']
    drop_out_D = training_params['drop_out_D']
    drop_out_G = training_params['drop_out_G']

    # ============================================= Defining networks ===================================================
    x_dim = x1[0].shape[1]
    generator1, generator2 = Generator(x_dim, G_hidden_dim, drop_out_G), Generator(x_dim, G_hidden_dim, drop_out_G)
    discriminator1, discriminator2 = Discriminator(x_dim, D_hidden_dim, drop_out_D), Discriminator(x_dim, D_hidden_dim,
                                                                                                   drop_out_D)

    # ==================================== Specifying the type of the losses ===============================================
    if loss_type == 'L1':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.L1Loss()
        criterion_identity = torch.nn.L1Loss()
    elif loss_type == 'MSE':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.MSELoss()
        criterion_identity = torch.nn.MSELoss()

    # ====================================== Specifying the type of the optimizer ==============================================
    if optim_type == 'SGD':
        gen1_optim = optim.SGD(generator1.parameters(), lr=G_lr, momentum=0.9)
        gen2_optim = optim.SGD(generator2.parameters(), lr=G_lr, momentum=0.9)
        dis1_optim = optim.SGD(discriminator1.parameters(), lr=D_lr, momentum=0.9)
        dis2_optim = optim.SGD(discriminator2.parameters(), lr=D_lr, momentum=0.9)
    elif optim_type == 'Adam':
        gen1_optim = optim.Adam(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.Adam(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.Adam(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.Adam(discriminator2.parameters(), lr=D_lr)
    elif optim_type == 'RMSProp':
        gen1_optim = optim.RMSprop(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.RMSprop(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.RMSprop(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.RMSprop(discriminator2.parameters(), lr=D_lr)



    # decoder = WienerFilterDecoder(n_lags=4, l2=1.0)

    if os.path.exists(decoder_pth):
        print("存在，加载该解码器")
        decoder.load_weights(decoder_pth)
        dayk_On_day0_mr2 = decoder.evaluate(x2[int(0.75*len(x2)):], y2[int(0.75*len(y2)):])
        print("Dayk R2 eval on Day0:", dayk_On_day0_mr2)
    else:
        print("解码器权重不存在，重新训练该解码器")
        # decoder.fit(x1[:int(0.75*len(x1))], y1[:int(0.75*len(y1))] ,x1[int(0.75*len(x1)):], y1[int(0.75*len(y1)):])
        # dayk_On_day0_mr2 = decoder.evaluate(x2[int(0.75*len(x2)):], y2[int(0.75*len(y2)):])
        # print("Dayk R2 eval on Day0:", dayk_On_day0_mr2)


        kf = KFold(n_splits=4, shuffle=False)
        #
        decoder_list = []  # for decoder saving
        mr2_list = []  # for multi-variate r2 saving
        r2_list = []  # for single-channel r2 saving
        for train_idx, test_idx in kf.split(x1):
            # ------ select training trials from the specified fold ------#
            x_train = [x1[i] for i in train_idx]
            y_train = [y1[i] for i in train_idx]
            decoder.fit(x_train,y_train)

            # ------ select testing trials from the specified fold ------#
            x_test = [x1[i] for i in test_idx]
            y_test = [y1[i] for i in test_idx]
            # ------ format data to fit the requirements of Wiener filter ------#
            dayk_On_day0_mr2 = decoder.evaluate(x_test, y_test)

            mr2_list.append(dayk_On_day0_mr2)
            decoder_list.append(decoder.best_H)
            # clear_output()

        print('The multi-variate r2 values for all the folds are:')
        print(mr2_list)
        decoder.best_H = decoder_list[np.argmax(mr2_list)]
            


    x1 = x1[:int(0.75*len(x1))]
    y1 = y1[:int(0.75*len(y1))]
    x2 = x2[:int(0.75*len(x2))]
    y2 = y2[:int(0.75*len(y2))]

    # =============================== Split x2 into the actual training set and the validation set ==============================
    # ----------- x2_train will be used in Cycle-GAN training -------------
    x2_train = x2[:int(len(x2) * 0.75)]  # training set

    # ------- x2_valid and y2_valid will be isolated from training, and used to test the performance of the aligner every 10 trials
    x2_valid, y2_valid = x2[int(len(x2) * 0.75):], y2[int(len(x2) * 0.75):]  # validation set

    # ================================================  Define data Loaders ======================================================
    x1, x2_train = np.concatenate(x1), np.concatenate(x2_train)

    # print("x1.shape----------------", x1.shape)
    # print("x2_train.shape----------------", x2_train.shape)

    # --------------- loader1 is for day-0 data ---------------------
    loader1 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x1)), batch_size=batch_size, shuffle=True)
    # --------------- loader2 is for day-k data in the training set ---------------------
    loader2 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x2_train)), batch_size=batch_size, shuffle=True)

    # ============================================ Training logs =========================================================
    train_log = {'epoch': [], 'batch_idx': [],
                 'loss D1': [], 'loss D2': [],
                 'loss G1': [], 'loss G2': [],
                 'loss cycle 121': [], 'loss cycle 212': [],
                 'decoder r2 wiener': [],
                 'decoder r2 rnn': []}

    # ============================================ Preparing to train ========================================================
    generator1.train()
    generator2.train()
    discriminator1.train()
    discriminator2.train()
    aligner_list = []
    mr2_all_list = []

    # ================================================== The training loop ====================================================
    for epoch in range(epochs):
        for batch_idx, (data1_, data2_) in enumerate(zip(loader1, loader2)):
            # ========================= loader1 and loader2 will yield mini-batches of data when running =========================
            # ------ The batches by loader1 will be stored in data1, while the batches by loader2 will be stored in data2 ------
            data1, data2 = data1_[0], data2_[0]
            if data1.__len__() != data2.__len__():
                continue
            # ------------ The labels for real samples --------------
            target_real = torch.ones((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')
            # ------------ The labels for fake samples --------------
            target_fake = torch.zeros((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')

            # ================================================== Generators ==================================================
            gen1_optim.zero_grad()
            gen2_optim.zero_grad()

            # ------------ Identity loss, to make sure the generators do not distort the inputs --------------
            same2 = generator1(data2)
            loss_identity2 = criterion_identity(same2, data2) * ID_loss_p
            same1 = generator2(data1)
            loss_identity1 = criterion_identity(same1, data1) * ID_loss_p

            # ------------ GAN loss for generator1, see the figure right above --------------
            fake2 = generator1(data1)
            pred_fake = discriminator2(fake2)
            loss_GAN2 = criterion_GAN(pred_fake, target_real)

            # ------------ GAN loss for generator2, see the figure right above --------------
            fake1 = generator2(data2)
            pred_fake = discriminator1(fake1)
            loss_GAN1 = criterion_GAN(pred_fake, target_real)

            # ------------ Cycle loss, see the figure right above --------------
            recovered1 = generator2(fake2)
            loss_cycle_121 = criterion_cycle(recovered1, data1) * cycle_loss_p

            recovered2 = generator1(fake1)
            loss_cycle_212 = criterion_cycle(recovered2, data2) * cycle_loss_p

            # ----------- Total loss of G, the sum of all the losses defined above -----------
            loss_G = loss_identity1 + loss_identity2 + loss_GAN1 + loss_GAN2 + loss_cycle_121 + loss_cycle_212

            # -------- Backward() and step() for generators ---------
            loss_G.backward()
            gen1_optim.step()
            gen2_optim.step()

            # ================================================== Discriminator 1 ==================================================
            dis1_optim.zero_grad()

            # -------------- Adversarial loss from discriminator 1, see the figure above ------------------
            pred_real = discriminator1(data1)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator1(generator2(data2).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D1 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator1 ---------
            loss_D1.backward()
            dis1_optim.step()

            # -------------- Adversarial loss from discriminator 2, see the figure above ------------------
            dis2_optim.zero_grad()

            pred_real = discriminator2(data2)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator2(generator1(data1).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D2 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator2 ---------
            loss_D2.backward()
            dis2_optim.step()

            # ====================================== save the training logs ========================================
            if logs == True:
                train_log['epoch'].append(epoch)
                train_log['batch_idx'].append(batch_idx)
                train_log['loss D1'].append(loss_D1.item())
                train_log['loss D2'].append(loss_D2.item())
                train_log['loss G1'].append(loss_GAN1.item())
                train_log['loss G2'].append(loss_GAN2.item())
                train_log['loss cycle 121'].append(loss_cycle_121.item())
                train_log['loss cycle 212'].append(loss_cycle_212.item())

        # ================ Test the aligner every 10 epoches on the validation set ====================
        if (epoch + 1) % 10 == 0:
            # ---------- Put generator2, namely the aligner, into evaluation mode ------------
            generator2.eval()

            # ---------- Use the trained aligner to transform the trials in x2_valid -----------
            # print(x2_valid.shape)
            x2_valid_aligned = []
            with torch.no_grad():
                for each in x2_valid:
                    data = torch.from_numpy(each).type('torch.FloatTensor')
                    x2_valid_aligned.append(generator2(data).numpy())

            # --------- Feed the day-0 decoder with x2_valid_aligned to evaluate the performance of the aligner ----------
            # print(x2_valid_aligned.shape)
            # x2_valid_aligned = np.concatenate(x2_valid_aligned)


            # y2_valid = [y2_valid[i] for i in range(len(y2_valid))]

            x2_valid_aligned_, y2_valid_ = format_data_from_trials(x2_valid_aligned, y2_valid, n_lags)
            pred_y2_valid_ = test_wiener_filter(x2_valid_aligned_, decoder.best_H)

            # --------- Compute the multi-variate R2 between pred_y2_valid (predicted EMGs) and y2_valid (real EMGs) ----------



            # print(y2_valid_.shape, pred_y2_valid_.shape)
            mr2 = r2_score(y2_valid_, pred_y2_valid_, multioutput='variance_weighted')
            print('On the %dth epoch, the R\u00b2 on the validation set is %.2f' % (epoch + 1, mr2))
            # print('On the %dth epoch, the R\u00b2 on the validation loss set is %.2f' % (epoch + 1, loss_G))

            # ------- Save the half-trained aligners and the corresponding performance on the validation set ---------
            aligner_list.append(generator2)
            mr2_all_list.append(mr2)

            # ---------- Put generator2 back into training mode after finishing the evaluation -----------
            generator2.train()

    IDX = np.argmax(mr2_all_list)
    # print("mr2_all_list---------------------", mr2_all_list)
    print('The aligner has been well trained on the %dth epoch' % (IDX * 10))
    # train_log['decoder r2 wiener'] = mr2_all_list
    # ============================================ save the training log =================================================
    # if logs == True:
    #     dt_string = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    #     with open('./model_logs/train_logs/train_log_' + dt_string + '.pkl', 'wb') as fp:
    #         pickle.dump(train_log, fp)

    return aligner_list[IDX], decoder.best_H, dayk_On_day0_mr2




def train_cycle_gan_aligner_Merge_Pth_LSTM(x1, y1, x2, y2, D_params, G_params, training_params, decoder, n_lags, decoder_pth, logs=True):
    """
    x1: M1 spike firing rates on day-0. A list, where each item is a numpy array containing the neural data of one trial

    x2: M1 spike firing rates on day-k. A list, where each item is a numpy array containing the neural data of one trial
        x2 will be divided into two portions (ratio 3:1), where the first portion will be used to train the aligner, and
        the second portion will be used as the validation set.

    y2: EMGs on day-k. A list, where each item is a numpy array containing the EMGs of one trial. Only a portion of y2
        (those corresponding to the trials used as the validation set) will be used.

    D_params: the hyper-parameters determining the structure of the discriminators, a dictionary.

    G_params: the hyper-parameters determining the structure of the generators, a dictionary.

    training_parameters: the hyper-parameters controlling the training process, a dictionary.

    decoder: the day-0 decoder to be tested on the validation set, an array.

    n_lags: the number of time lags of the decoder, a number.

    logs: to indicate if training logs is needed to be recorded as a .pkl file, a bool.

    return: a trained "aligner" (generator) for day-k use.
    """
    # ============================================= Specifying hyper-parameters =============================================
    D_hidden_dim = D_params['hidden_dim']
    G_hidden_dim = G_params['hidden_dim']
    loss_type = training_params['loss_type']
    optim_type = training_params['optim_type']
    epochs = training_params['epochs']
    batch_size = training_params['batch_size']
    D_lr = training_params['D_lr']
    G_lr = training_params['G_lr']
    ID_loss_p = training_params['ID_loss_p']
    cycle_loss_p = training_params['cycle_loss_p']
    drop_out_D = training_params['drop_out_D']
    drop_out_G = training_params['drop_out_G']

    # ============================================= Defining networks ===================================================
    x_dim = x1[0].shape[1]
    generator1, generator2 = Generator(x_dim, G_hidden_dim, drop_out_G), Generator(x_dim, G_hidden_dim, drop_out_G)
    discriminator1, discriminator2 = Discriminator(x_dim, D_hidden_dim, drop_out_D), Discriminator(x_dim, D_hidden_dim,
                                                                                                   drop_out_D)

    # ==================================== Specifying the type of the losses ===============================================
    if loss_type == 'L1':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.L1Loss()
        criterion_identity = torch.nn.L1Loss()
    elif loss_type == 'MSE':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.MSELoss()
        criterion_identity = torch.nn.MSELoss()

    # ====================================== Specifying the type of the optimizer ==============================================
    if optim_type == 'SGD':
        gen1_optim = optim.SGD(generator1.parameters(), lr=G_lr, momentum=0.9)
        gen2_optim = optim.SGD(generator2.parameters(), lr=G_lr, momentum=0.9)
        dis1_optim = optim.SGD(discriminator1.parameters(), lr=D_lr, momentum=0.9)
        dis2_optim = optim.SGD(discriminator2.parameters(), lr=D_lr, momentum=0.9)
    elif optim_type == 'Adam':
        gen1_optim = optim.Adam(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.Adam(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.Adam(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.Adam(discriminator2.parameters(), lr=D_lr)
    elif optim_type == 'RMSProp':
        gen1_optim = optim.RMSprop(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.RMSprop(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.RMSprop(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.RMSprop(discriminator2.parameters(), lr=D_lr)



    # decoder = WienerFilterDecoder(n_lags=4, l2=1.0)

    if os.path.exists(decoder_pth):
        # print("存在，加载该解码器")
        decoder.load_weights(decoder_pth)
        # dayk_On_day0_mr2 = decoder.evaluate(x2[int(0.75*len(x2)):], y2[int(0.75*len(y2)):])

        pred_y2_valid = decoder.predict(x2[int(0.75*len(x2)):])


        # print(y2_valid_.shape, pred_y2_valid_.shape)
        dayk_On_day0_mr2 = r2_score(y2[int(0.75*len(y2)):][:, -1, :], pred_y2_valid, multioutput='variance_weighted')
            
        print("Dayk R2 eval on Day0:", dayk_On_day0_mr2)
    else:
        # print("解码器权重不存在，重新训练该解码器")
        # decoder.fit(x1[:int(0.75*len(x1))], y1[:int(0.75*len(y1))] ,x1[int(0.75*len(x1)):], y1[int(0.75*len(y1)):])
        # dayk_On_day0_mr2 = decoder.evaluate(x2[int(0.75*len(x2)):], y2[int(0.75*len(y2)):])
        # print("Dayk R2 eval on Day0:", dayk_On_day0_mr2)




        # x_test = [x1[i] for i in test_idx]
        # y_test = [y1[i] for i in test_idx]

        decoder.fit(x1, y1)
        # decoder.best_H = decoder.best_state_dict

        pred_y2_valid = decoder.predict(x2[int(0.75*len(x2)):])


        # print(y2_valid_.shape, pred_y2_valid_.shape)
        dayk_On_day0_mr2 = r2_score(y2[int(0.75*len(y2)):][:, -1, :], pred_y2_valid, multioutput='variance_weighted')

        # decoder.save_weights(decoder_pth)    


    x1 = x1[:int(0.75*len(x1))]
    y1 = y1[:int(0.75*len(y1))]
    x2 = x2[:int(0.75*len(x2))]
    y2 = y2[:int(0.75*len(y2))]

    # =============================== Split x2 into the actual training set and the validation set ==============================
    # ----------- x2_train will be used in Cycle-GAN training -------------
    x2_train = x2[:int(len(x2) * 0.75)]  # training set

    # ------- x2_valid and y2_valid will be isolated from training, and used to test the performance of the aligner every 10 trials
    x2_valid, y2_valid = x2[int(len(x2) * 0.75):], y2[int(len(x2) * 0.75):]  # validation set

    # ================================================  Define data Loaders ======================================================
    x1, x2_train = np.concatenate(x1), np.concatenate(x2_train)

    # print("x1.shape----------------", x1.shape)
    # print("x2_train.shape----------------", x2_train.shape)

    # --------------- loader1 is for day-0 data ---------------------
    loader1 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x1)), batch_size=batch_size, shuffle=True)
    # --------------- loader2 is for day-k data in the training set ---------------------
    loader2 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x2_train)), batch_size=batch_size, shuffle=True)

    # ============================================ Training logs =========================================================
    train_log = {'epoch': [], 'batch_idx': [],
                 'loss D1': [], 'loss D2': [],
                 'loss G1': [], 'loss G2': [],
                 'loss cycle 121': [], 'loss cycle 212': [],
                 'decoder r2 wiener': [],
                 'decoder r2 rnn': []}

    # ============================================ Preparing to train ========================================================
    generator1.train()
    generator2.train()
    discriminator1.train()
    discriminator2.train()
    aligner_list = []
    mr2_all_list = []

    # ================================================== The training loop ====================================================
    for epoch in range(epochs):
        for batch_idx, (data1_, data2_) in enumerate(zip(loader1, loader2)):
            # ========================= loader1 and loader2 will yield mini-batches of data when running =========================
            # ------ The batches by loader1 will be stored in data1, while the batches by loader2 will be stored in data2 ------
            data1, data2 = data1_[0], data2_[0]
            if data1.__len__() != data2.__len__():
                continue
            # ------------ The labels for real samples --------------
            target_real = torch.ones((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')
            # ------------ The labels for fake samples --------------
            target_fake = torch.zeros((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')

            # ================================================== Generators ==================================================
            gen1_optim.zero_grad()
            gen2_optim.zero_grad()

            # ------------ Identity loss, to make sure the generators do not distort the inputs --------------
            same2 = generator1(data2)
            loss_identity2 = criterion_identity(same2, data2) * ID_loss_p
            same1 = generator2(data1)
            loss_identity1 = criterion_identity(same1, data1) * ID_loss_p

            # ------------ GAN loss for generator1, see the figure right above --------------
            fake2 = generator1(data1)
            pred_fake = discriminator2(fake2)
            loss_GAN2 = criterion_GAN(pred_fake, target_real)

            # ------------ GAN loss for generator2, see the figure right above --------------
            fake1 = generator2(data2)
            pred_fake = discriminator1(fake1)
            loss_GAN1 = criterion_GAN(pred_fake, target_real)

            # ------------ Cycle loss, see the figure right above --------------
            recovered1 = generator2(fake2)
            loss_cycle_121 = criterion_cycle(recovered1, data1) * cycle_loss_p

            recovered2 = generator1(fake1)
            loss_cycle_212 = criterion_cycle(recovered2, data2) * cycle_loss_p

            # ----------- Total loss of G, the sum of all the losses defined above -----------
            loss_G = loss_identity1 + loss_identity2 + loss_GAN1 + loss_GAN2 + loss_cycle_121 + loss_cycle_212

            # -------- Backward() and step() for generators ---------
            loss_G.backward()
            gen1_optim.step()
            gen2_optim.step()

            # ================================================== Discriminator 1 ==================================================
            dis1_optim.zero_grad()

            # -------------- Adversarial loss from discriminator 1, see the figure above ------------------
            pred_real = discriminator1(data1)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator1(generator2(data2).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D1 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator1 ---------
            loss_D1.backward()
            dis1_optim.step()

            # -------------- Adversarial loss from discriminator 2, see the figure above ------------------
            dis2_optim.zero_grad()

            pred_real = discriminator2(data2)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator2(generator1(data1).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D2 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator2 ---------
            loss_D2.backward()
            dis2_optim.step()

            # ====================================== save the training logs ========================================
            if logs == True:
                train_log['epoch'].append(epoch)
                train_log['batch_idx'].append(batch_idx)
                train_log['loss D1'].append(loss_D1.item())
                train_log['loss D2'].append(loss_D2.item())
                train_log['loss G1'].append(loss_GAN1.item())
                train_log['loss G2'].append(loss_GAN2.item())
                train_log['loss cycle 121'].append(loss_cycle_121.item())
                train_log['loss cycle 212'].append(loss_cycle_212.item())

        # ================ Test the aligner every 10 epoches on the validation set ====================
        if (epoch + 1) % 10 == 0:
            # ---------- Put generator2, namely the aligner, into evaluation mode ------------
            generator2.eval()

            # ---------- Use the trained aligner to transform the trials in x2_valid -----------
            # print(x2_valid.shape)
            x2_valid_aligned = []
            with torch.no_grad():
                for each in x2_valid:
                    data = torch.from_numpy(each).type('torch.FloatTensor')
                    x2_valid_aligned.append(generator2(data).numpy())

            # --------- Feed the day-0 decoder with x2_valid_aligned to evaluate the performance of the aligner ----------
            # print(x2_valid_aligned.shape)
            # x2_valid_aligned = np.concatenate(x2_valid_aligned)


            # y2_valid = [y2_valid[i] for i in range(len(y2_valid))]

            # x2_valid_aligned_, y2_valid_ = format_data_from_trials(x2_valid_aligned, y2_valid, n_lags)
            # pred_y2_valid_ = test_wiener_filter(x2_valid_aligned_, decoder.best_H)

            # --------- Compute the multi-variate R2 between pred_y2_valid (predicted EMGs) and y2_valid (real EMGs) ----------

            x2_valid_aligned, y2_valid = np.stack(x2_valid_aligned,axis=0), np.stack(y2_valid,axis=0)


            pred_y2_valid = decoder.predict(x2_valid_aligned)


            # print(y2_valid_.shape, pred_y2_valid_.shape)
            mr2 = r2_score(y2_valid[:, -1, :], pred_y2_valid, multioutput='variance_weighted')








            print('On the %dth epoch, the R\u00b2 on the validation set is %.2f' % (epoch + 1, mr2))
            # print('On the %dth epoch, the R\u00b2 on the validation loss set is %.2f' % (epoch + 1, loss_G))

            # ------- Save the half-trained aligners and the corresponding performance on the validation set ---------
            aligner_list.append(generator2)
            mr2_all_list.append(mr2)

            # ---------- Put generator2 back into training mode after finishing the evaluation -----------
            generator2.train()

    IDX = np.argmax(mr2_all_list)
    # print("mr2_all_list---------------------", mr2_all_list)
    print('The aligner has been well trained on the %dth epoch' % (IDX * 10))
    # train_log['decoder r2 wiener'] = mr2_all_list
    # ============================================ save the training log =================================================
    # if logs == True:
    #     dt_string = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    #     with open('./model_logs/train_logs/train_log_' + dt_string + '.pkl', 'wb') as fp:
    #         pickle.dump(train_log, fp)

    return aligner_list[IDX], decoder.best_state_dict, dayk_On_day0_mr2



            


def train_cycle_gan_aligner_Merge_Pth_LSTM_Classifier(x1, y1, x2, y2, D_params, G_params, training_params, decoder, n_lags, decoder_pth, logs=True):
    """
    x1: M1 spike firing rates on day-0. A list, where each item is a numpy array containing the neural data of one trial

    x2: M1 spike firing rates on day-k. A list, where each item is a numpy array containing the neural data of one trial
        x2 will be divided into two portions (ratio 3:1), where the first portion will be used to train the aligner, and
        the second portion will be used as the validation set.

    y2: EMGs on day-k. A list, where each item is a numpy array containing the EMGs of one trial. Only a portion of y2
        (those corresponding to the trials used as the validation set) will be used.

    D_params: the hyper-parameters determining the structure of the discriminators, a dictionary.

    G_params: the hyper-parameters determining the structure of the generators, a dictionary.

    training_parameters: the hyper-parameters controlling the training process, a dictionary.

    decoder: the day-0 decoder to be tested on the validation set, an array.

    n_lags: the number of time lags of the decoder, a number.

    logs: to indicate if training logs is needed to be recorded as a .pkl file, a bool.

    return: a trained "aligner" (generator) for day-k use.
    """
    # ============================================= Specifying hyper-parameters =============================================
    D_hidden_dim = D_params['hidden_dim']
    G_hidden_dim = G_params['hidden_dim']
    loss_type = training_params['loss_type']
    optim_type = training_params['optim_type']
    epochs = training_params['epochs']
    batch_size = training_params['batch_size']
    D_lr = training_params['D_lr']
    G_lr = training_params['G_lr']
    ID_loss_p = training_params['ID_loss_p']
    cycle_loss_p = training_params['cycle_loss_p']
    drop_out_D = training_params['drop_out_D']
    drop_out_G = training_params['drop_out_G']

    # ============================================= Defining networks ===================================================
    x_dim = x1[0].shape[1]
    generator1, generator2 = Generator(x_dim, G_hidden_dim, drop_out_G), Generator(x_dim, G_hidden_dim, drop_out_G)
    discriminator1, discriminator2 = Discriminator(x_dim, D_hidden_dim, drop_out_D), Discriminator(x_dim, D_hidden_dim,
                                                                                                   drop_out_D)

    # ==================================== Specifying the type of the losses ===============================================
    if loss_type == 'L1':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.L1Loss()
        criterion_identity = torch.nn.L1Loss()
    elif loss_type == 'MSE':
        criterion_GAN = torch.nn.MSELoss()
        criterion_cycle = torch.nn.MSELoss()
        criterion_identity = torch.nn.MSELoss()

    # ====================================== Specifying the type of the optimizer ==============================================
    if optim_type == 'SGD':
        gen1_optim = optim.SGD(generator1.parameters(), lr=G_lr, momentum=0.9)
        gen2_optim = optim.SGD(generator2.parameters(), lr=G_lr, momentum=0.9)
        dis1_optim = optim.SGD(discriminator1.parameters(), lr=D_lr, momentum=0.9)
        dis2_optim = optim.SGD(discriminator2.parameters(), lr=D_lr, momentum=0.9)
    elif optim_type == 'Adam':
        gen1_optim = optim.Adam(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.Adam(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.Adam(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.Adam(discriminator2.parameters(), lr=D_lr)
    elif optim_type == 'RMSProp':
        gen1_optim = optim.RMSprop(generator1.parameters(), lr=G_lr)
        gen2_optim = optim.RMSprop(generator2.parameters(), lr=G_lr)
        dis1_optim = optim.RMSprop(discriminator1.parameters(), lr=D_lr)
        dis2_optim = optim.RMSprop(discriminator2.parameters(), lr=D_lr)



    # decoder = WienerFilterDecoder(n_lags=4, l2=1.0)

    if os.path.exists(decoder_pth):
        # print("存在，加载该解码器")
        decoder.load_weights(decoder_pth)
        # dayk_On_day0_mr2 = decoder.evaluate(x2[int(0.75*len(x2)):], y2[int(0.75*len(y2)):])

        pred_y2_valid = decoder.predict(x2[int(0.75*len(x2)):])


        # print(y2_valid_.shape, pred_y2_valid_.shape)
        # dayk_On_day0_mr2 = r2_score(y2[int(0.75*len(y2)):][:, -1, :], pred_y2_valid, multioutput='variance_weighted')
            
        dayk_On_day0_acc = accuracy_score(y2[int(0.75*len(y2)):], pred_y2_valid)

        print("Dayk ACC eval on Day0:", dayk_On_day0_acc)
    else:
        # print("解码器权重不存在，重新训练该解码器")
        # decoder.fit(x1[:int(0.75*len(x1))], y1[:int(0.75*len(y1))] ,x1[int(0.75*len(x1)):], y1[int(0.75*len(y1)):])
        # dayk_On_day0_mr2 = decoder.evaluate(x2[int(0.75*len(x2)):], y2[int(0.75*len(y2)):])
        # print("Dayk R2 eval on Day0:", dayk_On_day0_mr2)




        # x_test = [x1[i] for i in test_idx]
        # y_test = [y1[i] for i in test_idx]

        decoder.fit(x1, y1)
        # decoder.best_H = decoder.best_state_dict

        pred_y2_valid = decoder.predict(x2[int(0.75*len(x2)):])


        # print(y2_valid_.shape, pred_y2_valid_.shape)
        # dayk_On_day0_mr2 = r2_score(y2[int(0.75*len(y2)):][:, -1, :], pred_y2_valid, multioutput='variance_weighted')
            
        dayk_On_day0_acc = accuracy_score(y2[int(0.75*len(y2)):], pred_y2_valid)

        print("Dayk ACC eval on Day0:", dayk_On_day0_acc)

        decoder.save_weights(decoder_pth)


    x1 = x1[:int(0.75*len(x1))]
    y1 = y1[:int(0.75*len(y1))]
    x2 = x2[:int(0.75*len(x2))]
    y2 = y2[:int(0.75*len(y2))]

    # =============================== Split x2 into the actual training set and the validation set ==============================
    # ----------- x2_train will be used in Cycle-GAN training -------------
    x2_train = x2[:int(len(x2) * 0.75)]  # training set

    # ------- x2_valid and y2_valid will be isolated from training, and used to test the performance of the aligner every 10 trials
    x2_valid, y2_valid = x2[int(len(x2) * 0.75):], y2[int(len(x2) * 0.75):]  # validation set

    # ================================================  Define data Loaders ======================================================
    x1, x2_train = np.concatenate(x1), np.concatenate(x2_train)

    # print("x1.shape----------------", x1.shape)
    # print("x2_train.shape----------------", x2_train.shape)

    # --------------- loader1 is for day-0 data ---------------------
    loader1 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x1)), batch_size=batch_size, shuffle=True)
    # --------------- loader2 is for day-k data in the training set ---------------------
    loader2 = DataLoader(torch.utils.data.TensorDataset(torch.Tensor(x2_train)), batch_size=batch_size, shuffle=True)

    # ============================================ Training logs =========================================================
    train_log = {'epoch': [], 'batch_idx': [],
                 'loss D1': [], 'loss D2': [],
                 'loss G1': [], 'loss G2': [],
                 'loss cycle 121': [], 'loss cycle 212': [],
                 'decoder r2 wiener': [],
                 'decoder r2 rnn': []}

    # ============================================ Preparing to train ========================================================
    generator1.train()
    generator2.train()
    discriminator1.train()
    discriminator2.train()
    aligner_list = []
    mr2_all_list = []

    # ================================================== The training loop ====================================================
    for epoch in range(epochs):
        for batch_idx, (data1_, data2_) in enumerate(zip(loader1, loader2)):
            # ========================= loader1 and loader2 will yield mini-batches of data when running =========================
            # ------ The batches by loader1 will be stored in data1, while the batches by loader2 will be stored in data2 ------
            data1, data2 = data1_[0], data2_[0]
            if data1.__len__() != data2.__len__():
                continue
            # ------------ The labels for real samples --------------
            target_real = torch.ones((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')
            # ------------ The labels for fake samples --------------
            target_fake = torch.zeros((data1.shape[0], 1), requires_grad=False).type('torch.FloatTensor')

            # ================================================== Generators ==================================================
            gen1_optim.zero_grad()
            gen2_optim.zero_grad()

            # ------------ Identity loss, to make sure the generators do not distort the inputs --------------
            same2 = generator1(data2)
            loss_identity2 = criterion_identity(same2, data2) * ID_loss_p
            same1 = generator2(data1)
            loss_identity1 = criterion_identity(same1, data1) * ID_loss_p

            # ------------ GAN loss for generator1, see the figure right above --------------
            fake2 = generator1(data1)
            pred_fake = discriminator2(fake2)
            loss_GAN2 = criterion_GAN(pred_fake, target_real)

            # ------------ GAN loss for generator2, see the figure right above --------------
            fake1 = generator2(data2)
            pred_fake = discriminator1(fake1)
            loss_GAN1 = criterion_GAN(pred_fake, target_real)

            # ------------ Cycle loss, see the figure right above --------------
            recovered1 = generator2(fake2)
            loss_cycle_121 = criterion_cycle(recovered1, data1) * cycle_loss_p

            recovered2 = generator1(fake1)
            loss_cycle_212 = criterion_cycle(recovered2, data2) * cycle_loss_p

            # ----------- Total loss of G, the sum of all the losses defined above -----------
            loss_G = loss_identity1 + loss_identity2 + loss_GAN1 + loss_GAN2 + loss_cycle_121 + loss_cycle_212

            # -------- Backward() and step() for generators ---------
            loss_G.backward()
            gen1_optim.step()
            gen2_optim.step()

            # ================================================== Discriminator 1 ==================================================
            dis1_optim.zero_grad()

            # -------------- Adversarial loss from discriminator 1, see the figure above ------------------
            pred_real = discriminator1(data1)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator1(generator2(data2).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D1 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator1 ---------
            loss_D1.backward()
            dis1_optim.step()

            # -------------- Adversarial loss from discriminator 2, see the figure above ------------------
            dis2_optim.zero_grad()

            pred_real = discriminator2(data2)
            loss_D_real = criterion_GAN(pred_real, target_real)

            pred_fake = discriminator2(generator1(data1).detach())
            loss_D_fake = criterion_GAN(pred_fake, target_fake)

            loss_D2 = (loss_D_real + loss_D_fake) / 2

            # -------- Backward() and step() for discriminator2 ---------
            loss_D2.backward()
            dis2_optim.step()

            # ====================================== save the training logs ========================================
            if logs == True:
                train_log['epoch'].append(epoch)
                train_log['batch_idx'].append(batch_idx)
                train_log['loss D1'].append(loss_D1.item())
                train_log['loss D2'].append(loss_D2.item())
                train_log['loss G1'].append(loss_GAN1.item())
                train_log['loss G2'].append(loss_GAN2.item())
                train_log['loss cycle 121'].append(loss_cycle_121.item())
                train_log['loss cycle 212'].append(loss_cycle_212.item())

        # ================ Test the aligner every 10 epoches on the validation set ====================
        if (epoch + 1) % 10 == 0:
            # ---------- Put generator2, namely the aligner, into evaluation mode ------------
            generator2.eval()

            # ---------- Use the trained aligner to transform the trials in x2_valid -----------
            # print(x2_valid.shape)
            x2_valid_aligned = []
            with torch.no_grad():
                for each in x2_valid:
                    data = torch.from_numpy(each).type('torch.FloatTensor')
                    x2_valid_aligned.append(generator2(data).numpy())

            # --------- Feed the day-0 decoder with x2_valid_aligned to evaluate the performance of the aligner ----------
            # print(x2_valid_aligned.shape)
            # x2_valid_aligned = np.concatenate(x2_valid_aligned)


            # y2_valid = [y2_valid[i] for i in range(len(y2_valid))]

            # x2_valid_aligned_, y2_valid_ = format_data_from_trials(x2_valid_aligned, y2_valid, n_lags)
            # pred_y2_valid_ = test_wiener_filter(x2_valid_aligned_, decoder.best_H)

            # --------- Compute the multi-variate R2 between pred_y2_valid (predicted EMGs) and y2_valid (real EMGs) ----------

            x2_valid_aligned, y2_valid = np.stack(x2_valid_aligned,axis=0), np.stack(y2_valid,axis=0)


            pred_y2_valid = decoder.predict(x2_valid_aligned)


            # print(y2_valid_.shape, pred_y2_valid_.shape)
            # mr2 = r2_score(y2_valid[:, -1, :], pred_y2_valid, multioutput='variance_weighted')

            mr2 = accuracy_score(y2_valid, pred_y2_valid)








            print('On the %dth epoch, the R\u00b2 on the validation set is %.2f' % (epoch + 1, mr2))
            # print('On the %dth epoch, the R\u00b2 on the validation loss set is %.2f' % (epoch + 1, loss_G))

            # ------- Save the half-trained aligners and the corresponding performance on the validation set ---------
            aligner_list.append(generator2)
            mr2_all_list.append(mr2)

            # ---------- Put generator2 back into training mode after finishing the evaluation -----------
            generator2.train()

    IDX = np.argmax(mr2_all_list)
    # print("mr2_all_list---------------------", mr2_all_list)
    print('The aligner has been well trained on the %dth epoch' % (IDX * 10))
    # train_log['decoder r2 wiener'] = mr2_all_list
    # ============================================ save the training log =================================================
    # if logs == True:
    #     dt_string = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    #     with open('./model_logs/train_logs/train_log_' + dt_string + '.pkl', 'wb') as fp:
    #         pickle.dump(train_log, fp)

    return aligner_list[IDX], decoder.best_state_dict, dayk_On_day0_acc