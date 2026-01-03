import math
import numbers
import torch
from torch import nn
from torch.nn import functional as F


class WhiteNoise(nn.Module):
    def __init__(self, std=0.1):
        super().__init__()
        self.std = std

    def forward(self, x):
        noise = torch.randn_like(x) * self.std
        return x + noise

class MeanDriftNoise(nn.Module):
    def __init__(self, std=0.1):
        super().__init__()
        self.std = std

    def forward(self, x):
        _, C = x.shape
        noise = torch.randn(1, C) * self.std
        return x + noise

class GaussianSmoothing(nn.Module):
    """
    Apply gaussian smoothing on a
    1d, 2d or 3d tensor. Filtering is performed seperately for each channel
    in the input using a depthwise convolution.
    Arguments:
        channels (int, sequence): Number of channels of the input tensors. Output will
            have this number of channels as well.
        kernel_size (int, sequence): Size of the gaussian kernel.
        sigma (float, sequence): Standard deviation of the gaussian kernel.
        dim (int, optional): The number of dimensions of the data.
            Default value is 2 (spatial).
    """

    def __init__(self, channels, kernel_size, sigma, dim=2):
        super(GaussianSmoothing, self).__init__()
        if isinstance(kernel_size, numbers.Number):
            kernel_size = [kernel_size] * dim
        if isinstance(sigma, numbers.Number):
            sigma = [sigma] * dim

        # The gaussian kernel is the product of the
        # gaussian function of each dimension.
        kernel = 1
        meshgrids = torch.meshgrid(
            [torch.arange(size, dtype=torch.float32) for size in kernel_size]
        )
        for size, std, mgrid in zip(kernel_size, sigma, meshgrids):
            mean = (size - 1) / 2
            kernel *= (
                1
                / (std * math.sqrt(2 * math.pi))
                * torch.exp(-(((mgrid - mean) / std) ** 2) / 2)
            )

        # Make sure sum of values in gaussian kernel equals 1.
        kernel = kernel / torch.sum(kernel)

        # Reshape to depthwise convolutional weight
        kernel = kernel.view(1, 1, *kernel.size())
        kernel = kernel.repeat(channels, *[1] * (kernel.dim() - 1))

        self.register_buffer("weight", kernel)
        self.groups = channels

        if dim == 1:
            self.conv = F.conv1d
        elif dim == 2:
            self.conv = F.conv2d
        elif dim == 3:
            self.conv = F.conv3d
        else:
            raise RuntimeError(
                "Only 1, 2 and 3 dimensions are supported. Received {}.".format(dim)
            )

    def forward(self, input):
        """
        Apply gaussian filter to input.
        Arguments:
            input (torch.Tensor): Input to apply gaussian filter on.
        Returns:
            filtered (torch.Tensor): Filtered output.
        """
        return self.conv(input, weight=self.weight, groups=self.groups, padding="same")



class GRUDecoder(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        strideLen=4,
        kernelLen=14,
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(GRUDecoder, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.strideLen = strideLen
        self.kernelLen = kernelLen
        self.gaussianSmoothWidth = gaussianSmoothWidth
        self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()
        self.unfolder = torch.nn.Unfold(
            (self.kernelLen, 1), dilation=1, padding=0, stride=self.strideLen
        )
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))

        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # GRU layers
        self.gru_decoder = nn.GRU(
            (neural_dim) * self.kernelLen,
            hidden_dim,
            layer_dim,
            batch_first=True,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        )

        for name, param in self.gru_decoder.named_parameters():
            if "weight_hh" in name:
                nn.init.orthogonal_(param)
            if "weight_ih" in name:
                nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # rnn outputs
        if self.bidirectional:
            self.fc_decoder_out = nn.Linear(
                hidden_dim * 2, n_classes + 1
            )  # +1 for CTC blank
        else:
            self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)  # +1 for CTC blank

    def forward(self, neuralInput, dayIdx):
        neuralInput = torch.permute(neuralInput, (0, 2, 1))
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # print("transformedNeural.shape---------", transformedNeural.shape)

        # stride/kernel
        stridedInputs = torch.permute(
            self.unfolder(
                torch.unsqueeze(torch.permute(transformedNeural, (0, 2, 1)), 3)
            ),
            (0, 2, 1),
        )

        # print("stridedInputs.shape---------", stridedInputs.shape)  

        # apply RNN layer
        if self.bidirectional:
            h0 = torch.zeros(
                self.layer_dim * 2,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()
        else:
            h0 = torch.zeros(
                self.layer_dim,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()

        # print("h0.shape---------", h0.shape)

        

        hid, _ = self.gru_decoder(stridedInputs, h0.detach())

        # print("hid.shape---------", hid.shape)

        # get seq
        seq_out = self.fc_decoder_out(hid)

        # print("seq_out.shape---------", seq_out.shape)

        # transformedNeural.shape--------- torch.Size([64, 919, 256])
        # stridedInputs.shape--------- torch.Size([64, 222, 8192])
        # hid.shape--------- torch.Size([64, 222, 2048])
        # seq_out.shape--------- torch.Size([64, 222, 41])

        return seq_out


class LSTMDecoder(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        strideLen=4,
        kernelLen=14,
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(LSTMDecoder, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.strideLen = strideLen
        self.kernelLen = kernelLen
        self.gaussianSmoothWidth = gaussianSmoothWidth
        self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()
        self.unfolder = torch.nn.Unfold(
            (self.kernelLen, 1), dilation=1, padding=0, stride=self.strideLen
        )
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))

        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # LSTM layers
        self.lstm_decoder = nn.LSTM(
            (neural_dim) * self.kernelLen,
            hidden_dim,
            layer_dim,
            batch_first=True,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        )

        for name, param in self.lstm_decoder.named_parameters():
            if "weight_hh" in name:
                nn.init.orthogonal_(param)
            if "weight_ih" in name:
                nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # rnn outputs
        if self.bidirectional:
            self.fc_decoder_out = nn.Linear(
                hidden_dim * 2, n_classes + 1
            )  # +1 for CTC blank
        else:
            self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)  # +1 for CTC blank

    def forward(self, neuralInput, dayIdx):
        neuralInput = torch.permute(neuralInput, (0, 2, 1))
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # print(" LSTM transformedNeural.shape---------", transformedNeural.shape)

        # stride/kernel
        stridedInputs = torch.permute(
            self.unfolder(
                torch.unsqueeze(torch.permute(transformedNeural, (0, 2, 1)), 3)
            ),
            (0, 2, 1),
        )

        # print("stridedInputs.shape---------", stridedInputs.shape)  

        # apply RNN layer
        if self.bidirectional:
            h0 = torch.zeros(
                self.layer_dim * 2,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()
            c0 = torch.zeros(
                self.layer_dim * 2,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()

        else:
            h0 = torch.zeros(
                self.layer_dim,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()
            c0 = torch.zeros(
                self.layer_dim * 2,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()

        
        # print("h0.shape---------", h0.shape)
        

        hid, (_, _) = self.lstm_decoder(stridedInputs, (h0.detach(), c0.detach()))

        # print("hid.shape---------", hid.shape)

        # get seq
        seq_out = self.fc_decoder_out(hid)

        # print("seq_out.shape---------", seq_out.shape)

        # transformedNeural.shape--------- torch.Size([64, 919, 256])
        # stridedInputs.shape--------- torch.Size([64, 222, 8192])
        # hid.shape--------- torch.Size([64, 222, 2048])
        # seq_out.shape--------- torch.Size([64, 222, 41])

        return seq_out
    

class GRUDecoderNoUnfold(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(GRUDecoderNoUnfold, self).__init__()

        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.gaussianSmoothWidth = gaussianSmoothWidth
        self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()

        # 高斯平滑
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )

        # 每天的权重 & bias
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))
        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # GRU: 输入直接是 neural_dim (不再乘 kernelLen)
        self.gru_decoder = nn.GRU(
            neural_dim,
            hidden_dim,
            layer_dim,
            batch_first=True,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        )

        for name, param in self.gru_decoder.named_parameters():
            if "weight_hh" in name:
                nn.init.orthogonal_(param)
            if "weight_ih" in name:
                nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # 输出层
        if self.bidirectional:
            self.fc_decoder_out = nn.Linear(hidden_dim * 2, n_classes + 1)
        else:
            self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)

    def forward(self, neuralInput, dayIdx):
        # neuralInput: [batch, time, channels]
        neuralInput = torch.permute(neuralInput, (0, 2, 1))   # [B, C, T]
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))   # [B, T, C]

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # RNN 初始状态
        if self.bidirectional:
            h0 = torch.zeros(
                self.layer_dim * 2,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()
        else:
            h0 = torch.zeros(
                self.layer_dim,
                transformedNeural.size(0),
                self.hidden_dim,
                device=self.device,
            ).requires_grad_()

        # GRU 输入: [B, T, neural_dim]
        hid, _ = self.gru_decoder(transformedNeural, h0.detach())

        seq_out = self.fc_decoder_out(hid)  # [B, T, n_classes+1]
        return seq_out



class ConvDecoder(nn.Module):
    def __init__(self, input_dim, n_classes, hidden_dim=1024, kernel_size=3, num_layers=3):
        super().__init__()
        layers = []
        for i in range(num_layers):
            in_ch = input_dim if i == 0 else hidden_dim
            layers.append(nn.Conv1d(in_ch, hidden_dim, kernel_size, padding=kernel_size//2))
            layers.append(nn.ReLU())
        self.conv = nn.Sequential(*layers)
        self.fc_out = nn.Conv1d(hidden_dim, n_classes + 1, 1)  # +1 for CTC blank

    def forward(self, x):
        # x: [batch, seq_len, input_dim] -> [batch, input_dim, seq_len]
        x = x.permute(0, 2, 1)
        x = self.conv(x)  # [batch, hidden_dim, seq_len]
        x = self.fc_out(x)  # [batch, n_classes+1, seq_len]
        x = x.permute(0, 2, 1)  # -> [batch, seq_len, n_classes+1]
        return x
    

class Conv1DClassifier(nn.Module):
    def __init__(self, input_dim=8192, num_classes=10, hidden_dim=256, num_layers=3, dropout=0.3):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        layers = []
        in_ch = input_dim
        for i in range(num_layers):
            out_ch = hidden_dim
            layers.append(nn.Conv1d(in_ch, out_ch, kernel_size=3, padding=1))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            in_ch = out_ch

        self.conv = nn.Sequential(*layers)

        # Global pooling over time dimension
        self.pool = nn.AdaptiveAvgPool1d(1)

        # Final classification layer
        self.fc = nn.Linear(hidden_dim, num_classes+1)

    def forward(self, x):
        # x: [B, T, F] → Conv1d expects [B, F, T]
        x = x.permute(0, 2, 1)  # [B, F, T]

        x = self.conv(x)        # [B, hidden_dim, T]
        x = self.pool(x)        # [B, hidden_dim, 1]
        x = x.squeeze(-1)       # [B, hidden_dim]
        out = self.fc(x)        # [B, num_classes]
        return out




class CNNDecoder(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        strideLen=4,
        kernelLen=14,
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(CNNDecoder, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.strideLen = strideLen
        self.kernelLen = kernelLen
        self.gaussianSmoothWidth = gaussianSmoothWidth
        # self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()
        self.unfolder = torch.nn.Unfold(
            (self.kernelLen, 1), dilation=1, padding=0, stride=self.strideLen
        )
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))

        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # # GRU layers
        # self.gru_decoder = nn.GRU(
        #     (neural_dim) * self.kernelLen,
        #     hidden_dim,
        #     layer_dim,
        #     batch_first=True,
        #     dropout=self.dropout,
        #     bidirectional=self.bidirectional,
        # )

        # for name, param in self.gru_decoder.named_parameters():
        #     if "weight_hh" in name:
        #         nn.init.orthogonal_(param)
        #     if "weight_ih" in name:
        #         nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # # rnn outputs
        # if self.bidirectional:
        #     self.fc_decoder_out = nn.Linear(
        #         hidden_dim * 2, n_classes + 1
        #     )  # +1 for CTC blank
        # else:
        #     self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)  # +1 for CTC blank


        self.conv_decoder = ConvDecoder(input_dim=(neural_dim) * self.kernelLen, n_classes=n_classes+1, hidden_dim=self.hidden_dim, num_layers=self.layer_dim)  # 0.24

        # self.conv_decoder = Conv1DClassifier(input_dim=(neural_dim) * self.kernelLen, num_classes=n_classes)

        # from models.FingerFlex import AutoEncoder1D
        # self.conv_decoder = AutoEncoder1D(n_electrodes=8192,  # Number of channels
        #                 n_freqs=1,  # Number of wavelets
        #                 n_channels_out=n_classes+1,  # Number of fingers
        #                   channels=[32, 32, 64, 64, 128, 128],
        #                   kernel_sizes=[7, 7, 5, 5, 5],
        #                   strides=[2, 2, 2, 2, 2],
        #                   dilation=[1, 1, 1, 1, 1],)

    def forward(self, neuralInput, dayIdx):
        neuralInput = torch.permute(neuralInput, (0, 2, 1))
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # print("CNN transformedNeural.shape---------", transformedNeural.shape)

        # stride/kernel
        stridedInputs = torch.permute(
            self.unfolder(
                torch.unsqueeze(torch.permute(transformedNeural, (0, 2, 1)), 3)
            ),
            (0, 2, 1),
        )

        # print("stridedInputs.shape---------", stridedInputs.shape)  

        # apply RNN layer
        # if self.bidirectional:
        #     h0 = torch.zeros(
        #         self.layer_dim * 2,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()
        # else:
        #     h0 = torch.zeros(
        #         self.layer_dim,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()

        

        # hid, _ = self.gru_decoder(stridedInputs, h0.detach())

        # print("hid.shape---------", hid.shape)

        # get seq
        # seq_out = self.fc_decoder_out(hid)

        # print("seq_out.shape---------", seq_out.shape)

        # transformedNeural.shape--------- torch.Size([64, 919, 256])
        # stridedInputs.shape--------- torch.Size([64, 222, 8192])
        # hid.shape--------- torch.Size([64, 222, 2048])
        # seq_out.shape--------- torch.Size([64, 222, 41])


        seq_out = self.conv_decoder(stridedInputs)

        return seq_out
    

import numpy as np
from scipy.signal import resample

def resample_eeg_numpy(X, T_new, batch_size=4096):
    """
    批量重采样 EEG 数据 (N, C, T_old) -> (N, C, T_new)，使用 scipy.signal.resample

    Args:
        X (np.ndarray): 输入数据，shape=(N, C, T_old)
        T_new (int): 目标时间长度
        batch_size (int): 每批处理的样本数

    Returns:
        np.ndarray: 重采样后的数据，shape=(N, C, T_new)
    """
    N, C, T_old = X.shape
    X_resampled = np.zeros((N, C, T_new), dtype=np.float32)

    for start in range(0, N, batch_size):
        end = min(start + batch_size, N)
        batch = X[start:end]  # shape: (B, C, T_old)
        X_resampled[start:end] = resample(batch, num=T_new, axis=2)

    return X_resampled


import torch

def resample_fft_torch(X, T_new, batch_size=4096, device="cuda"):
    """
    FFT-based 重采样 EEG 数据 (N, C, T_old) -> (N, C, T_new)，等价于 scipy.signal.resample

    Args:
        X (torch.Tensor or np.ndarray): 输入数据，shape=(N, C, T_old)
        T_new (int): 目标时间长度
        batch_size (int): 每批处理的样本数
        device (str): "cuda" 或 "cpu"

    Returns:
        torch.Tensor: 重采样后的数据，shape=(N, C, T_new)，在 device 上
    """
    # 转换 numpy -> torch
    if isinstance(X, np.ndarray):
        X = torch.from_numpy(X)

    X = X.to(device)
    N, C, T_old = X.shape
    X_resampled = torch.zeros((N, C, T_new), dtype=X.dtype, device=device)

    for start in range(0, N, batch_size):
        end = min(start + batch_size, N)
        batch = X[start:end]  # (B, C, T_old)

        # 1. FFT
        X_fft = torch.fft.rfft(batch, dim=-1)  # (B, C, T_old//2+1)

        # 2. 频谱裁剪/零填充
        new_len = T_new // 2 + 1
        old_len = X_fft.shape[-1]

        if new_len > old_len:
            # 零填充到更长频率 bins
            X_fft_new = torch.zeros(batch.shape[0], batch.shape[1], new_len, dtype=X_fft.dtype, device=device)
            X_fft_new[..., :old_len] = X_fft
        else:
            # 截断频率
            X_fft_new = X_fft[..., :new_len]

        # 3. iFFT
        batch_resampled = torch.fft.irfft(X_fft_new, n=T_new, dim=-1)

        # 存到结果里
        X_resampled[start:end] = batch_resampled

    return X_resampled



class CommonDecoder(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        strideLen=4,
        kernelLen=14,
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(CommonDecoder, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.strideLen = strideLen
        self.kernelLen = kernelLen
        self.gaussianSmoothWidth = gaussianSmoothWidth
        self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()
        self.unfolder = torch.nn.Unfold(
            (self.kernelLen, 1), dilation=1, padding=0, stride=self.strideLen
        )
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))

        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # GRU layers
        self.gru_decoder = nn.GRU(
            (neural_dim) * self.kernelLen,
            hidden_dim,
            layer_dim,
            batch_first=True,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        )

        for name, param in self.gru_decoder.named_parameters():
            if "weight_hh" in name:
                nn.init.orthogonal_(param)
            if "weight_ih" in name:
                nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # rnn outputs
        if self.bidirectional:
            self.fc_decoder_out = nn.Linear(
                hidden_dim * 2, n_classes + 1
            )  # +1 for CTC blank
        else:
            self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)  # +1 for CTC blank


        # self.conv_decoder = ConvDecoder(input_dim=8192, n_classes=n_classes)

        # self.conv_decoder = Conv1DClassifier(input_dim=8192, num_classes=n_classes)

        # self.spatial_conv = nn.Conv1d(in_channels=8192, out_channels=96, kernel_size=1)


        # from models.FingerFlex import AutoEncoder1D
        # self.conv_decoder = AutoEncoder1D(n_electrodes=8192,  # Number of channels  8196
        #                 n_freqs=1,  # Number of wavelets
        #                 n_channels_out=n_classes,  # Number of fingers
        #                   channels=[32, 32, 64, 64, 128, 128],
        #                   kernel_sizes=[7, 7, 5, 5, 5],
        #                   strides=[2, 2, 2, 2, 2],
        #                   dilation=[1, 1, 1, 1, 1],)

    def forward(self, neuralInput, dayIdx):
        neuralInput = torch.permute(neuralInput, (0, 2, 1))
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # print("transformedNeural.shape---------", transformedNeural.shape)

        # stride/kernel
        stridedInputs = torch.permute(
            self.unfolder(
                torch.unsqueeze(torch.permute(transformedNeural, (0, 2, 1)), 3)
            ),
            (0, 2, 1),
        )

        # print("stridedInputs.shape---------", stridedInputs.shape)  

        # apply RNN layer
        # if self.bidirectional:
        #     h0 = torch.zeros(
        #         self.layer_dim * 2,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()
        # else:
        #     h0 = torch.zeros(
        #         self.layer_dim,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()

        

        # hid, _ = self.gru_decoder(stridedInputs, h0.detach())

        # print("hid.shape---------", hid.shape)

        # get seq
        # seq_out = self.fc_decoder_out(hid)

        # print("seq_out.shape---------", seq_out.shape)

        # transformedNeural.shape--------- torch.Size([64, 919, 256])
        # stridedInputs.shape--------- torch.Size([64, 222, 8192])
        # hid.shape--------- torch.Size([64, 222, 2048])
        # seq_out.shape--------- torch.Size([64, 222, 41])



        # stridedInputs = stridedInputs.permute(0, 2, 1)
        # stridedInputs = stridedInputs.detach().cpu().numpy()

        # stridedInputs = resample_eeg_numpy(stridedInputs, T_new=640, batch_size=24)

        # stridedInputs = torch.from_numpy(stridedInputs).to(self.device)

        # stridedInputs = stridedInputs.permute(0, 2, 1)

        # stridedInputs = self.spatial_conv(stridedInputs)
        # # stridedInputs = resample_eeg_torch(stridedInputs, T_new=640, device="cuda")
        # stridedInputs = resample_fft_torch(stridedInputs, T_new=640, device="cuda")


        # seq_out = self.conv_decoder(stridedInputs)

        return stridedInputs
    

import torch
import torch.nn.functional as F

def pad_to_max_len(x, max_len):
    """
    将 tensor 的第二个维度 (时间维度) 补零到指定长度 max_len
    Args:
        x: Tensor, shape = (B, T, D)
        max_len: int, 目标长度
    Returns:
        Tensor, shape = (B, max_len, D)
    """
    pad_len = max_len - x.size(1)
    if pad_len > 0:
        x_padded = F.pad(x, (0, 0, 0, pad_len, 0, 0))
    else:
        x_padded = x[:, :max_len, :]
    return x_padded

# # 测试 GPU
# x = torch.randn(64, 222, 8192, device="cuda")  # 放在 GPU
# x_padded = pad_to_max_len(x, 300)
# print(x_padded.shape, x_padded.device)



class FingerDecoder(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        strideLen=4,
        kernelLen=14,
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(FingerDecoder, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.strideLen = strideLen
        self.kernelLen = kernelLen
        self.gaussianSmoothWidth = gaussianSmoothWidth
        self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()
        self.unfolder = torch.nn.Unfold(
            (self.kernelLen, 1), dilation=1, padding=0, stride=self.strideLen
        )
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))

        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # GRU layers
        self.gru_decoder = nn.GRU(
            (neural_dim) * self.kernelLen,
            hidden_dim,
            layer_dim,
            batch_first=True,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        )

        for name, param in self.gru_decoder.named_parameters():
            if "weight_hh" in name:
                nn.init.orthogonal_(param)
            if "weight_ih" in name:
                nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # rnn outputs
        if self.bidirectional:
            self.fc_decoder_out = nn.Linear(
                hidden_dim * 2, n_classes + 1
            )  # +1 for CTC blank
        else:
            self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)  # +1 for CTC blank


        # self.conv_decoder = ConvDecoder(input_dim=8192, n_classes=n_classes)

        # self.conv_decoder = Conv1DClassifier(input_dim=8192, num_classes=n_classes)

        # self.spatial_conv = nn.Conv1d(in_channels=8192, out_channels=96, kernel_size=1)


        from models.FingerFlex import AutoEncoder1D
        self.conv_decoder = AutoEncoder1D(n_electrodes=8192,  # Number of channels  8196
                        n_freqs=1,  # Number of wavelets
                        n_channels_out=n_classes+1,  # Number of fingers
                          channels=[32, 32, 64, 64, 128, 128],
                          kernel_sizes=[7, 7, 5, 5, 5],
                          strides=[2, 2, 2, 2, 2],
                          dilation=[1, 1, 1, 1, 1],)

    def forward(self, neuralInput, dayIdx):
        neuralInput = torch.permute(neuralInput, (0, 2, 1))
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # print("transformedNeural.shape---------", transformedNeural.shape)

        # stride/kernel
        stridedInputs = torch.permute(
            self.unfolder(
                torch.unsqueeze(torch.permute(transformedNeural, (0, 2, 1)), 3)
            ),
            (0, 2, 1),
        )

        # print("stridedInputs.shape---------", stridedInputs.shape)  

        # apply RNN layer
        # if self.bidirectional:
        #     h0 = torch.zeros(
        #         self.layer_dim * 2,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()
        # else:
        #     h0 = torch.zeros(
        #         self.layer_dim,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()

        

        # hid, _ = self.gru_decoder(stridedInputs, h0.detach())

        # print("hid.shape---------", hid.shape)

        # get seq
        # seq_out = self.fc_decoder_out(hid)

        # print("seq_out.shape---------", seq_out.shape)

        # transformedNeural.shape--------- torch.Size([64, 919, 256])
        # stridedInputs.shape--------- torch.Size([64, 222, 8192])
        # hid.shape--------- torch.Size([64, 222, 2048])
        # seq_out.shape--------- torch.Size([64, 222, 41])



        # stridedInputs = stridedInputs.permute(0, 2, 1)
        # stridedInputs = stridedInputs.detach().cpu().numpy()

        # stridedInputs = resample_eeg_numpy(stridedInputs, T_new=256, batch_size=24)

        # stridedInputs = torch.from_numpy(stridedInputs).to(self.device)

        # stridedInputs = stridedInputs.permute(0, 2, 1)

        # # # print("stridedInputs.shape---------", stridedInputs.shape)

        # # # stridedInputs = self.spatial_conv(stridedInputs)
        # # # stridedInputs = resample_eeg_torch(stridedInputs, T_new=640, device="cuda")
        # stridedInputs = resample_fft_torch(stridedInputs, T_new=256, device="cuda")  # 0.403 fingerflex  resample_fft_torch 256 截断

        stridedInputs = pad_to_max_len(stridedInputs, 256)
        stridedInputs = stridedInputs.permute(0, 2, 1)


        seq_out = self.conv_decoder(stridedInputs)  # 0.403 fingerflex  resample_fft_torch 256 截断

        return seq_out



import random

from torch import nn
import torch.nn.functional as F

from models.transformer import TransformerEncoderLayer

from absl import flags
FLAGS = flags.FLAGS
flags.DEFINE_integer('model_size', 768, 'number of hidden dimensions')
flags.DEFINE_integer('num_layers', 6, 'number of layers')
flags.DEFINE_float('dropout', .2, 'dropout')

class ResBlock(nn.Module):
    def __init__(self, num_ins, num_outs, stride=1):
        super().__init__()

        self.conv1 = nn.Conv1d(num_ins, num_outs, 3, padding=1, stride=stride)
        self.bn1 = nn.BatchNorm1d(num_outs)
        self.conv2 = nn.Conv1d(num_outs, num_outs, 3, padding=1)
        self.bn2 = nn.BatchNorm1d(num_outs)

        if stride != 1 or num_ins != num_outs:
            self.residual_path = nn.Conv1d(num_ins, num_outs, 1, stride=stride)
            self.res_norm = nn.BatchNorm1d(num_outs)
        else:
            self.residual_path = None

    def forward(self, x):
        input_value = x

        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))

        if self.residual_path is not None:
            res = self.res_norm(self.residual_path(input_value))
        else:
            res = input_value

        return F.relu(x + res)

class Model(nn.Module):
    def __init__(self, num_outs, num_aux_outs=None):
        super().__init__()

        self.conv_blocks = nn.Sequential(
            # ResBlock(256, 768, 2),
            # ResBlock(768, 768, 2),
            # ResBlock(768, 768, 2),
                        ResBlock(256, 768, 1),
            ResBlock(768, 768, 1),
            ResBlock(768, 768, 1),
        )
        self.w_raw_in = nn.Linear(768, 768)

        # encoder_layer = TransformerEncoderLayer(d_model=768, nhead=8, relative_positional=True, relative_positional_distance=100, dim_feedforward=3072, dropout=.2)
        # self.transformer = nn.TransformerEncoder(encoder_layer, 6)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=768,
            nhead=8,
            dim_feedforward=768 * 4,
            dropout=0.1,
            batch_first=True  # 注意：PyTorch >=1.9 支持这个参数
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=6)
        self.w_out = nn.Linear(768, num_outs)

        self.has_aux_out = num_aux_outs is not None
        if self.has_aux_out:
            self.w_aux = nn.Linear(FLAGS.model_size, num_aux_outs)

    def forward(self, x_raw):
        # x shape is (batch, time, electrode)

        if self.training:
            r = random.randrange(8)
            if r > 0:
                x_raw[:,:-r,:] = x_raw[:,r:,:] # shift left r
                x_raw[:,-r:,:] = 0

        x_raw = x_raw.transpose(1,2) # put channel before time for conv
        x_raw = self.conv_blocks(x_raw)
        x_raw = x_raw.transpose(1,2)
        x_raw = self.w_raw_in(x_raw)

        x = x_raw

        x = x.transpose(0,1) # put time first
        x = self.transformer(x)
        x = x.transpose(0,1)

        if self.has_aux_out:
            return self.w_out(x), self.w_aux(x)
        else:
            return self.w_out(x)



class GRUDecoderModel(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        strideLen=4,
        kernelLen=14,
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(GRUDecoderModel, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.strideLen = strideLen
        self.kernelLen = kernelLen
        self.gaussianSmoothWidth = gaussianSmoothWidth
        self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()
        self.unfolder = torch.nn.Unfold(
            (self.kernelLen, 1), dilation=1, padding=0, stride=self.strideLen
        )
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))

        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # GRU layers
        self.gru_decoder = nn.GRU(
            (neural_dim) * self.kernelLen,
            hidden_dim,
            layer_dim,
            batch_first=True,
            dropout=self.dropout,
            bidirectional=self.bidirectional,
        )

        self.conv_blocks = nn.Sequential(
            # ResBlock(8192, 768, 2),
            # ResBlock(768, 768, 2),
            # ResBlock(768, 768, 2),
                        ResBlock(8192, 768, 1),
            ResBlock(768, 768, 1),
            ResBlock(768, 768, 1),
        )
        self.w_raw_in = nn.Linear(768, 768)
        # import torch.nn as nn

        # self.trans_in = nn.Linear((neural_dim) * self.kernelLen, 1024)  # 0.29

        # encoder_layer = nn.TransformerEncoderLayer(
        #     d_model=1024,
        #     nhead=8,
        #     dim_feedforward=1024 * 4,
        #     dropout=0.1,
        #     batch_first=True  # 注意：PyTorch >=1.9 支持这个参数
        # )
        # # self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=1)  # layer=1 0.29  stride kernel 减少一半
        # self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)  # 待定  结果需要进一步确定

        self.trans_in = nn.Linear((neural_dim) * self.kernelLen, 1024)  # 0.29
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=1024,
            nhead=8, # 8
            dim_feedforward=1024 * 4,
            dropout=0.1,
            batch_first=True  # 注意：PyTorch >=1.9 支持这个参数
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=1)  # layer=1 0.29  stride kernel 减少一半








        # encoder_layer = TransformerEncoderLayer(768, nhead=8, relative_positional=True, relative_positional_distance=100, dim_feedforward=3072, dropout=.2)
        # self.transformer = nn.TransformerEncoder(encoder_layer, 6)
        self.w_out = nn.Linear(768, n_classes + 1)



        for name, param in self.gru_decoder.named_parameters():
            if "weight_hh" in name:
                nn.init.orthogonal_(param)
            if "weight_ih" in name:
                nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # rnn outputs
        if self.bidirectional:
            self.fc_decoder_out = nn.Linear(
                hidden_dim * 2, n_classes + 1
            )  # +1 for CTC blank
        else:
            # self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)  # +1 for CTC blank
            # self.fc_decoder_out = nn.Linear(1024, n_classes + 1)  # +1 for CTC blank
            self.fc_decoder_out = nn.Linear(1024, n_classes + 1)  # +1 for CTC blank

    def forward(self, neuralInput, dayIdx):
        neuralInput = torch.permute(neuralInput, (0, 2, 1))
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # print("transformedNeural.shape---------", transformedNeural.shape)

        # stride/kernel
        stridedInputs = torch.permute(
            self.unfolder(
                torch.unsqueeze(torch.permute(transformedNeural, (0, 2, 1)), 3)
            ),
            (0, 2, 1),
        )

        # x_raw = stridedInputs

        # print("stridedInputs.shape---------", stridedInputs.shape)  

        # # apply RNN layer
        # if self.bidirectional:
        #     h0 = torch.zeros(
        #         self.layer_dim * 2,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()
        # else:
        #     h0 = torch.zeros(
        #         self.layer_dim,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()

        

        # hid, _ = self.gru_decoder(stridedInputs, h0.detach())

        # print("hid.shape---------", hid.shape)


        hid = self.trans_in(stridedInputs)
        hid = self.transformer(hid)

        # get seq
        seq_out = self.fc_decoder_out(hid)

        # print("seq_out.shape---------", seq_out.shape)

        # transformedNeural.shape--------- torch.Size([64, 919, 256])
        # stridedInputs.shape--------- torch.Size([64, 222, 8192])
        # hid.shape--------- torch.Size([64, 222, 2048])
        # seq_out.shape--------- torch.Size([64, 222, 41])

        # if self.training:
        #     r = random.randrange(8)
        #     if r > 0:
        #         x_raw[:,:-r,:] = x_raw[:,r:,:] # shift left r
        #         x_raw[:,-r:,:] = 0

        # x_raw = x_raw.transpose(1,2) # put channel before time for conv
        # x_raw = self.conv_blocks(x_raw)
        # x_raw = x_raw.transpose(1,2)
        # x_raw = self.w_raw_in(x_raw)

        # x = x_raw

        # x = x.transpose(0,1) # put time first
        # x = self.transformer(x)
        # x = x.transpose(0,1)

        # seq_out = self.w_out(x)

        # print("seq_out.shape---------", seq_out.shape)

        return seq_out
    

# ====== 模型 ======
class LSTMDecoder(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, output_dim=2, num_layers=2, dropout=0.3):
        super(LSTMDecoder, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers,
                            batch_first=True, dropout=dropout)
        self.norm = nn.LayerNorm(hidden_dim)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.tanh = nn.Tanh()

        # self.loading = nn.Linear(input_dim, 5)
        # self.lstm = nn.LSTM(5, hidden_dim, num_layers,
        #                     batch_first=True, dropout=dropout)

    def forward(self, x):
        # x = self.loading(x)
        out, _ = self.lstm(x)     # (B, T, H)
        out = self.norm(out)
        out = self.fc(out)        # (B, T, 2)
        # out = self.tanh(out)      # 约束输出 [-1, 1]
        return out



class LSTMGRUDecoder(nn.Module):
    def __init__(
        self,
        neural_dim,
        n_classes,
        hidden_dim,
        layer_dim,
        nDays=24,
        dropout=0,
        device="cuda",
        strideLen=4,
        kernelLen=14,
        gaussianSmoothWidth=0,
        bidirectional=False,
    ):
        super(LSTMGRUDecoder, self).__init__()

        # Defining the number of layers and the nodes in each layer
        self.layer_dim = layer_dim
        self.hidden_dim = hidden_dim
        self.neural_dim = neural_dim
        self.n_classes = n_classes
        self.nDays = nDays
        self.device = device
        self.dropout = dropout
        self.strideLen = strideLen
        self.kernelLen = kernelLen
        self.gaussianSmoothWidth = gaussianSmoothWidth
        # self.bidirectional = bidirectional
        self.inputLayerNonlinearity = torch.nn.Softsign()
        self.unfolder = torch.nn.Unfold(
            (self.kernelLen, 1), dilation=1, padding=0, stride=self.strideLen
        )
        self.gaussianSmoother = GaussianSmoothing(
            neural_dim, 20, self.gaussianSmoothWidth, dim=1
        )
        self.dayWeights = torch.nn.Parameter(torch.randn(nDays, neural_dim, neural_dim))
        self.dayBias = torch.nn.Parameter(torch.zeros(nDays, 1, neural_dim))

        for x in range(nDays):
            self.dayWeights.data[x, :, :] = torch.eye(neural_dim)

        # # GRU layers
        # self.gru_decoder = nn.GRU(
        #     (neural_dim) * self.kernelLen,
        #     hidden_dim,
        #     layer_dim,
        #     batch_first=True,
        #     dropout=self.dropout,
        #     bidirectional=self.bidirectional,
        # )

        # for name, param in self.gru_decoder.named_parameters():
        #     if "weight_hh" in name:
        #         nn.init.orthogonal_(param)
        #     if "weight_ih" in name:
        #         nn.init.xavier_uniform_(param)

        # Input layers
        for x in range(nDays):
            setattr(self, "inpLayer" + str(x), nn.Linear(neural_dim, neural_dim))

        for x in range(nDays):
            thisLayer = getattr(self, "inpLayer" + str(x))
            thisLayer.weight = torch.nn.Parameter(
                thisLayer.weight + torch.eye(neural_dim)
            )

        # # rnn outputs
        # if self.bidirectional:
        #     self.fc_decoder_out = nn.Linear(
        #         hidden_dim * 2, n_classes + 1
        #     )  # +1 for CTC blank
        # else:
        #     self.fc_decoder_out = nn.Linear(hidden_dim, n_classes + 1)  # +1 for CTC blank

        self.lstm = LSTMDecoder(input_dim=(neural_dim) * self.kernelLen, hidden_dim=self.hidden_dim, output_dim=n_classes + 1)

    def forward(self, neuralInput, dayIdx):
        neuralInput = torch.permute(neuralInput, (0, 2, 1))
        neuralInput = self.gaussianSmoother(neuralInput)
        neuralInput = torch.permute(neuralInput, (0, 2, 1))

        # apply day layer
        dayWeights = torch.index_select(self.dayWeights, 0, dayIdx)
        transformedNeural = torch.einsum(
            "btd,bdk->btk", neuralInput, dayWeights
        ) + torch.index_select(self.dayBias, 0, dayIdx)
        transformedNeural = self.inputLayerNonlinearity(transformedNeural)

        # print("transformedNeural.shape---------", transformedNeural.shape)

        # stride/kernel
        stridedInputs = torch.permute(
            self.unfolder(
                torch.unsqueeze(torch.permute(transformedNeural, (0, 2, 1)), 3)
            ),
            (0, 2, 1),
        )

        # print("stridedInputs.shape---------", stridedInputs.shape)  

        # # apply RNN layer
        # if self.bidirectional:
        #     h0 = torch.zeros(
        #         self.layer_dim * 2,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()
        # else:
        #     h0 = torch.zeros(
        #         self.layer_dim,
        #         transformedNeural.size(0),
        #         self.hidden_dim,
        #         device=self.device,
        #     ).requires_grad_()

        

        # hid, _ = self.gru_decoder(stridedInputs, h0.detach())

        # print("hid.shape---------", hid.shape)

        # get seq
        # seq_out = self.fc_decoder_out(hid)

        # print("seq_out.shape---------", seq_out.shape)

        # transformedNeural.shape--------- torch.Size([64, 919, 256])
        # stridedInputs.shape--------- torch.Size([64, 222, 8192])
        # hid.shape--------- torch.Size([64, 222, 2048])
        # seq_out.shape--------- torch.Size([64, 222, 41])

        seq_out = self.lstm(stridedInputs)

        return seq_out