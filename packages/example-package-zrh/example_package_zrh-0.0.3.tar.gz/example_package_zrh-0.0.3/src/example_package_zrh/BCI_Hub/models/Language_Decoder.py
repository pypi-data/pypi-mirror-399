import numpy as np
import time
from difflib import SequenceMatcher
from torch.utils.data import Dataset, DataLoader

import os
import pickle
import time

from edit_distance import SequenceMatcher
# import hydra
import numpy as np
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader

from torch.utils.data import Dataset, DataLoader, random_split, Subset, TensorDataset
from sklearn.model_selection import train_test_split

from models.GRUDecoder import GRUDecoder, LSTMDecoder, LSTMGRUDecoder, CNNDecoder
# from .dataset import SpeechDataset


def calculate_cer(pred, yt, Xt_len, yt_len, kernel_len, stride_len, blank_id=0):
    """
    通用版本的计算CER函数
    
    Args:
        pred: 模型预测输出 [batch_size, seq_len, vocab_size]
        yt: 真实标签 [batch_size, seq_len]
        Xt_len: 输入序列长度
        yt_len: 真实标签长度
        kernel_len: 卷积核长度
        stride_len: 步长
        blank_id: 空白符ID，默认为0
    
    Returns:
        cer: 字符错误率
        total_edit_distance: 总编辑距离
        total_seq_length: 总序列长度
    """
    total_edit_distance = 0
    total_seq_length = 0
    
    # adjustedLens = ((Xt_len - kernel_len) / stride_len).to(torch.int32)

    adjustedLens = ((Xt_len - kernel_len) / stride_len).astype(np.int32)
    
    for i in range(pred.shape[0]):
        # 解码预测序列
        decoded = torch.argmax(pred[i, :adjustedLens[i]], dim=-1)
        decoded = torch.unique_consecutive(decoded, dim=-1)
        decoded = decoded.cpu().numpy()
        decoded = decoded[decoded != blank_id]
        
        # 获取真实序列
        # trueSeq = yt[i][:yt_len[i]].cpu().numpy()
        trueSeq = yt[i][:yt_len[i]]
        
        # 计算编辑距离
        matcher = SequenceMatcher(a=trueSeq.tolist(), b=decoded.tolist())
        total_edit_distance += matcher.distance()
        total_seq_length += len(trueSeq)
    
    cer = total_edit_distance / total_seq_length if total_seq_length > 0 else float('inf')
    return cer


# ---------------------- Dataset ---------------------- #
class SeqDataset(Dataset):
    def __init__(self, X, y, X_len, y_len, dayIdx):
        self.X = X
        self.y = y
        self.X_len = X_len
        self.y_len = y_len
        self.dayIdx = dayIdx

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return (
            torch.tensor(self.X[idx], dtype=torch.float32),
            torch.tensor(self.y[idx], dtype=torch.int32),
            torch.tensor(self.X_len[idx], dtype=torch.int32),
            torch.tensor(self.y_len[idx], dtype=torch.int32),
            torch.tensor(self.dayIdx[idx], dtype=torch.int32),
        )


# # ---------------------- GRU Decoder ---------------------- #
# class GRUDecoder(torch.nn.Module):
#     def __init__(self, neural_dim, n_classes, hidden_dim, layer_dim,
#                  nDays, dropout, device,
#                  strideLen=1, kernelLen=1, gaussianSmoothWidth=0,
#                  bidirectional=False):
#         super().__init__()

#         self.kernelLen = kernelLen
#         self.strideLen = strideLen

#         self.embedding = torch.nn.Embedding(nDays, neural_dim)

#         self.gru = torch.nn.GRU(
#             input_size=neural_dim,
#             hidden_size=hidden_dim,
#             num_layers=layer_dim,
#             dropout=dropout,
#             batch_first=True,
#             bidirectional=bidirectional,
#         )

#         mul = 2 if bidirectional else 1

#         self.fc = torch.nn.Linear(hidden_dim * mul, n_classes)

#     def forward(self, x, dayIdx):
#         """
#         x: [B, T, C]
#         dayIdx: [B]
#         """
#         B, T, C = x.shape
#         day_embed = self.embedding(dayIdx)  # [B, C]
#         day_embed = day_embed.unsqueeze(1).expand(-1, T, -1)

#         x = x + day_embed

#         out, _ = self.gru(x)
#         out = self.fc(out)
#         return out


# ---------------------- Decoder Wrapper Class ---------------------- #
class DecoderGRUModel:
    def __init__(self, args):
        self.args = args
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = GRUDecoder(
            neural_dim=args["nInputFeatures"],
            n_classes=args["nClasses"],
            hidden_dim=args["nUnits"],
            layer_dim=args["nLayers"],
            nDays=args["nDays"],
            dropout=args["dropout"],
            device=self.device,
            strideLen=args["strideLen"],
            kernelLen=args["kernelLen"],
            gaussianSmoothWidth=args["gaussianSmoothWidth"],
            bidirectional=args["bidirectional"],
        ).to(self.device)

        self.loss_ctc = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=True)

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=args["lrStart"],
            betas=(0.9, 0.999),
            eps=0.1,
            weight_decay=args["l2_decay"],
        )

        self.scheduler = torch.optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=1.0,
            end_factor=args["lrEnd"] / args["lrStart"],
            total_iters=args["nBatch"],
        )

        self.bestCER = None

    # ----------------------------------------------------------
    #                       FIT
    # ----------------------------------------------------------
    # def fit(self, X, y, X_len, y_len, dayIdx,
    #         test_X, test_y, test_X_len, test_y_len, test_dayIdx):
        
    def fit(self, X, y, X_len, y_len, dayIdx):
        
        # ----------- 1) 训练 / 验证划分 -----------
        (
            X_train, X_val,
            y_train, y_val,
            Xlen_train, Xlen_val,
            ylen_train, ylen_val,
            dayidx_train, dayidx_val
        ) = train_test_split(
            X, y, X_len, y_len, dayIdx,
            test_size=0.25,
            shuffle=True,
            random_state=42
        )

        # # Build datasets
        # train_ds = SeqDataset(X, y, X_len, y_len, dayIdx)
        # test_ds = SeqDataset(test_X, test_y, test_X_len, test_y_len, test_dayIdx)

            # ----------- 2) Dataset / DataLoader 构建 -----------
        train_ds = SeqDataset(X_train, y_train, Xlen_train, ylen_train, dayidx_train)
        val_ds   = SeqDataset(X_val,   y_val,   Xlen_val,   ylen_val,   dayidx_val)

        trainLoader = DataLoader(train_ds, batch_size=self.args["batchSize"],
                                 shuffle=True, pin_memory=True, num_workers=0)
        testLoader = DataLoader(val_ds, batch_size=self.args["batchSize"],
                                shuffle=False, pin_memory=True, num_workers=0)

        testLoss = []
        testCER = []

        startTime = time.time()

        for batch in range(self.args["nBatch"]):
            self.model.train()

            Xb, yb, X_lenb, y_lenb, dayIdxb = next(iter(trainLoader))
            Xb, yb, X_lenb, y_lenb, dayIdxb = \
                Xb.to(self.device), yb.to(self.device), X_lenb.to(self.device), y_lenb.to(self.device), dayIdxb.to(self.device)

            # ---- Noise Aug ---- #
            if self.args["whiteNoiseSD"] > 0:
                Xb += torch.randn(Xb.shape, device=self.device) * self.args["whiteNoiseSD"]

            if self.args["constantOffsetSD"] > 0:
                Xb += torch.randn([Xb.shape[0], 1, Xb.shape[2]], device=self.device) * self.args["constantOffsetSD"]

            # ---- Forward ---- #
            pred = self.model(Xb, dayIdxb)

            # ---- CTC Loss ---- #
            loss = self.loss_ctc(
                torch.permute(pred.log_softmax(2), [1, 0, 2]),
                yb,
                ((X_lenb - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                y_lenb,
            )
            loss = torch.sum(loss)

            # ---- Backprop ---- #
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            # --------------------------------------------------------
            #                       Eval
            # --------------------------------------------------------
            if batch % 100 == 0:
                self.model.eval()

                allLoss = []
                total_edit_distance, total_seq_length = 0, 0

                with torch.no_grad():
                    for Xt, yt, Xt_len, yt_len, dayt in testLoader:
                        Xt, yt, Xt_len, yt_len, dayt = \
                            Xt.to(self.device), yt.to(self.device), Xt_len.to(self.device), yt_len.to(self.device), dayt.to(self.device)

                        pred = self.model(Xt, dayt)

                        loss = self.loss_ctc(
                            torch.permute(pred.log_softmax(2), [1, 0, 2]),
                            yt,
                            ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                            yt_len,
                        )
                        allLoss.append(loss.cpu().detach().numpy())

                        # ---- Compute CER ---- #
                        adjustedLens = ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32)

                        for i in range(pred.shape[0]):
                            decoded = torch.argmax(pred[i, :adjustedLens[i]], dim=-1)
                            decoded = torch.unique_consecutive(decoded, dim=-1)
                            decoded = decoded.cpu().numpy()
                            decoded = decoded[decoded != 0]

                            trueSeq = yt[i][:yt_len[i]].cpu().numpy()

                            matcher = SequenceMatcher(a=trueSeq.tolist(), b=decoded.tolist())
                            total_edit_distance += matcher.distance()
                            total_seq_length += len(trueSeq)

                avgLoss = np.sum(allLoss) / len(testLoader)
                cer = total_edit_distance / total_seq_length

                print(f"[Batch {batch}] CTC Loss={avgLoss:.4f}, CER={cer:.4f}")

                # ---- Save best model ---- #
                if self.bestCER is None or cer < self.bestCER:
                    self.bestCER = cer
                    torch.save(self.model.state_dict(), self.args["pthDir"] + "/modelWeights")
                    print(f"✓ Saved best model (CER={cer:.4f})")

                testLoss.append(avgLoss)
                testCER.append(cer)

                startTime = time.time()

        return testLoss, testCER

    # ----------------------------------------------------------
    #                   PREDICT (decoding)
    # ----------------------------------------------------------
    def predict(self, X, X_len, dayIdx):
        self.model.eval()
        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        X_len = torch.tensor(X_len, dtype=torch.int32).to(self.device)
        dayIdx = torch.tensor(dayIdx, dtype=torch.int32).to(self.device)

        with torch.no_grad():
            pred = self.model(X, dayIdx)

        decoded_all = []
        for i in range(pred.shape[0]):
            L = int((X_len[i] - self.model.kernelLen) / self.model.strideLen)
            decoded = torch.argmax(pred[i, :L], dim=-1)
            decoded = torch.unique_consecutive(decoded, dim=-1)
            decoded = decoded.cpu().numpy()
            decoded = decoded[decoded != 0]
            decoded_all.append(decoded)

        return decoded_all
    

    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build CycleGANLSTMAligner from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        # with open(path, "r") as f:
        #     model_params = yaml.safe_load(f)

        # ---------- 必须参数 ----------
        # if "input_dim" not in model_params:
        #     raise KeyError(
        #         "[CycleGANLSTMAligner] Missing required parameter: `input_dim`"
        #     )

        # if "num_classes" not in model_params and "output_dim" not in model_params:
        #     raise KeyError(
        #         "[CycleGANLSTMAligner] Missing required parameter: "
        #         "`num_classes` or `output_dim`"
        #     )

        # 统一类别参数名
        # output_dim = (
        #     model_params["num_classes"]
        #     if "num_classes" in model_params
        #     else model_params["output_dim"]
        # )

        model = DecoderGRUModel(
            args=model_params
        )


        # ---------- 构建模型 ----------
        return model



# ---------------------- Decoder Wrapper Class ---------------------- #
class DecoderGRUModel_args:
    def __init__(self, args, model_params):
        self.args = args
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = model_params["device"]

        self.model = GRUDecoder(
            neural_dim=model_params["neural_dim"],
            n_classes=model_params["n_classes"],
            hidden_dim=model_params["hidden_dim"],
            layer_dim=model_params["layer_dim"],
            nDays=model_params["nDays"],
            dropout=model_params["dropout"],
            device=model_params["device"],
            strideLen=model_params["strideLen"],
            kernelLen=model_params["kernelLen"],
            gaussianSmoothWidth=model_params["gaussianSmoothWidth"],
            bidirectional=model_params["bidirectional"],
        ).to(self.device)
        # )

        self.loss_ctc = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=True)

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=args["lrStart"],
            betas=(0.9, 0.999),
            eps=0.1,
            weight_decay=args["l2_decay"],
        )

        self.scheduler = torch.optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=1.0,
            end_factor=args["lrEnd"] / args["lrStart"],
            total_iters=args["nBatch"],
        )

        self.bestCER = None

    # ----------------------------------------------------------
    #                       FIT
    # ----------------------------------------------------------
    # def fit(self, X, y, X_len, y_len, dayIdx,
    #         test_X, test_y, test_X_len, test_y_len, test_dayIdx):
        
    def fit(self, X, y, X_len, y_len, dayIdx):
        
        # ----------- 1) 训练 / 验证划分 -----------
        (
            X_train, X_val,
            y_train, y_val,
            Xlen_train, Xlen_val,
            ylen_train, ylen_val,
            dayidx_train, dayidx_val
        ) = train_test_split(
            X, y, X_len, y_len, dayIdx,
            test_size=0.25,
            shuffle=True,
            random_state=42
        )

        # # Build datasets
        # train_ds = SeqDataset(X, y, X_len, y_len, dayIdx)
        # test_ds = SeqDataset(test_X, test_y, test_X_len, test_y_len, test_dayIdx)

            # ----------- 2) Dataset / DataLoader 构建 -----------
        train_ds = SeqDataset(X_train, y_train, Xlen_train, ylen_train, dayidx_train)
        val_ds   = SeqDataset(X_val,   y_val,   Xlen_val,   ylen_val,   dayidx_val)

        trainLoader = DataLoader(train_ds, batch_size=self.args["batchSize"],
                                 shuffle=True, pin_memory=True, num_workers=0)
        testLoader = DataLoader(val_ds, batch_size=self.args["batchSize"],
                                shuffle=False, pin_memory=True, num_workers=0)

        testLoss = []
        testCER = []

        startTime = time.time()

        for batch in range(self.args["nBatch"]):
            self.model.train()

            Xb, yb, X_lenb, y_lenb, dayIdxb = next(iter(trainLoader))
            Xb, yb, X_lenb, y_lenb, dayIdxb = \
                Xb.to(self.device), yb.to(self.device), X_lenb.to(self.device), y_lenb.to(self.device), dayIdxb.to(self.device)

            # ---- Noise Aug ---- #
            if self.args["whiteNoiseSD"] > 0:
                Xb += torch.randn(Xb.shape, device=self.device) * self.args["whiteNoiseSD"]

            if self.args["constantOffsetSD"] > 0:
                Xb += torch.randn([Xb.shape[0], 1, Xb.shape[2]], device=self.device) * self.args["constantOffsetSD"]

            # ---- Forward ---- #
            pred = self.model(Xb, dayIdxb)

            # ---- CTC Loss ---- #
            loss = self.loss_ctc(
                torch.permute(pred.log_softmax(2), [1, 0, 2]),
                yb,
                ((X_lenb - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                y_lenb,
            )
            loss = torch.sum(loss)

            # ---- Backprop ---- #
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            # --------------------------------------------------------
            #                       Eval
            # --------------------------------------------------------
            if batch % 100 == 0:
                self.model.eval()

                allLoss = []
                total_edit_distance, total_seq_length = 0, 0

                with torch.no_grad():
                    for Xt, yt, Xt_len, yt_len, dayt in testLoader:
                        Xt, yt, Xt_len, yt_len, dayt = \
                            Xt.to(self.device), yt.to(self.device), Xt_len.to(self.device), yt_len.to(self.device), dayt.to(self.device)

                        pred = self.model(Xt, dayt)

                        loss = self.loss_ctc(
                            torch.permute(pred.log_softmax(2), [1, 0, 2]),
                            yt,
                            ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                            yt_len,
                        )
                        allLoss.append(loss.cpu().detach().numpy())

                        # ---- Compute CER ---- #
                        adjustedLens = ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32)

                        for i in range(pred.shape[0]):
                            decoded = torch.argmax(pred[i, :adjustedLens[i]], dim=-1)
                            decoded = torch.unique_consecutive(decoded, dim=-1)
                            decoded = decoded.cpu().numpy()
                            decoded = decoded[decoded != 0]

                            trueSeq = yt[i][:yt_len[i]].cpu().numpy()

                            matcher = SequenceMatcher(a=trueSeq.tolist(), b=decoded.tolist())
                            total_edit_distance += matcher.distance()
                            total_seq_length += len(trueSeq)

                avgLoss = np.sum(allLoss) / len(testLoader)
                cer = total_edit_distance / total_seq_length

                print(f"[Batch {batch}] CTC Loss={avgLoss:.4f}, CER={cer:.4f}")

                # ---- Save best model ---- #
                if self.bestCER is None or cer < self.bestCER:
                    self.bestCER = cer
                    torch.save(self.model.state_dict(), self.args["pthDir"] + "/modelWeights")
                    self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                    print(f"✓ Saved best model (CER={cer:.4f})")

                testLoss.append(avgLoss)
                testCER.append(cer)

                startTime = time.time()

        return testLoss, testCER

    # ----------------------------------------------------------
    #                   PREDICT (decoding)
    # ----------------------------------------------------------
    # def predict(self, X, X_len, dayIdx):
    def predict(self, X, dayIdx):
        self.model.eval()
        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        # X_len = torch.tensor(X_len, dtype=torch.int32).to(self.device)
        dayIdx = torch.tensor(dayIdx, dtype=torch.int32).to(self.device)

        with torch.no_grad():
            pred = self.model(X, dayIdx)

        # decoded_all = []
        # for i in range(pred.shape[0]):
        #     L = int((X_len[i] - self.model.kernelLen) / self.model.strideLen)
        #     decoded = torch.argmax(pred[i, :L], dim=-1)
        #     decoded = torch.unique_consecutive(decoded, dim=-1)
        #     decoded = decoded.cpu().numpy()
        #     decoded = decoded[decoded != 0]
        #     decoded_all.append(decoded)

        # return decoded_all
        
    
        return pred
    
    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build DecoderGRUModel_args from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        model = DecoderGRUModel_args(
            args=model_params,model_params=model_params
        )


        # ---------- 构建模型 ----------
        return model
    
    def save_weights(self, path):
         
         torch.save(self.best_state_dict, path)

    def load_weights(self, path):
        try:
            # 加载权重
            state_dict = torch.load(path, map_location=self.device)
            
            # 加载到模型中
            self.model.load_state_dict(state_dict)
            
            # 更新 best_state_dict
            self.best_state_dict = state_dict
            
            print(f" 模型权重已从 {path} 加载")
            
            
        except Exception as e:
            print(f" 加载权重失败: {e}")




# ---------------------- Decoder Wrapper Class ---------------------- #
class DecoderLSTMModel_args:
    def __init__(self, args, model_params):
        self.args = args
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = model_params["device"]

        self.model = LSTMDecoder(
            neural_dim=model_params["neural_dim"],
            n_classes=model_params["n_classes"],
            hidden_dim=model_params["hidden_dim"],
            layer_dim=model_params["layer_dim"],
            nDays=model_params["nDays"],
            dropout=model_params["dropout"],
            device=model_params["device"],
            strideLen=model_params["strideLen"],
            kernelLen=model_params["kernelLen"],
            gaussianSmoothWidth=model_params["gaussianSmoothWidth"],
            bidirectional=model_params["bidirectional"],
        ).to(self.device)

        self.loss_ctc = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=True)

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=args["lrStart"],
            betas=(0.9, 0.999),
            eps=0.1,
            weight_decay=args["l2_decay"],
        )

        self.scheduler = torch.optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=1.0,
            end_factor=args["lrEnd"] / args["lrStart"],
            total_iters=args["nBatch"],
        )

        self.bestCER = None

    # ----------------------------------------------------------
    #                       FIT
    # ----------------------------------------------------------
    # def fit(self, X, y, X_len, y_len, dayIdx,
    #         test_X, test_y, test_X_len, test_y_len, test_dayIdx):
        
    def fit(self, X, y, X_len, y_len, dayIdx):
        
        # ----------- 1) 训练 / 验证划分 -----------
        (
            X_train, X_val,
            y_train, y_val,
            Xlen_train, Xlen_val,
            ylen_train, ylen_val,
            dayidx_train, dayidx_val
        ) = train_test_split(
            X, y, X_len, y_len, dayIdx,
            test_size=0.25,
            shuffle=True,
            random_state=42
        )

        # # Build datasets
        # train_ds = SeqDataset(X, y, X_len, y_len, dayIdx)
        # test_ds = SeqDataset(test_X, test_y, test_X_len, test_y_len, test_dayIdx)

            # ----------- 2) Dataset / DataLoader 构建 -----------
        train_ds = SeqDataset(X_train, y_train, Xlen_train, ylen_train, dayidx_train)
        val_ds   = SeqDataset(X_val,   y_val,   Xlen_val,   ylen_val,   dayidx_val)

        trainLoader = DataLoader(train_ds, batch_size=self.args["batchSize"],
                                 shuffle=True, pin_memory=True, num_workers=0)
        testLoader = DataLoader(val_ds, batch_size=self.args["batchSize"],
                                shuffle=False, pin_memory=True, num_workers=0)

        testLoss = []
        testCER = []

        startTime = time.time()

        for batch in range(self.args["nBatch"]):
            self.model.train()

            Xb, yb, X_lenb, y_lenb, dayIdxb = next(iter(trainLoader))
            Xb, yb, X_lenb, y_lenb, dayIdxb = \
                Xb.to(self.device), yb.to(self.device), X_lenb.to(self.device), y_lenb.to(self.device), dayIdxb.to(self.device)

            # ---- Noise Aug ---- #
            if self.args["whiteNoiseSD"] > 0:
                Xb += torch.randn(Xb.shape, device=self.device) * self.args["whiteNoiseSD"]

            if self.args["constantOffsetSD"] > 0:
                Xb += torch.randn([Xb.shape[0], 1, Xb.shape[2]], device=self.device) * self.args["constantOffsetSD"]

            # ---- Forward ---- #
            pred = self.model(Xb, dayIdxb)

            # ---- CTC Loss ---- #
            loss = self.loss_ctc(
                torch.permute(pred.log_softmax(2), [1, 0, 2]),
                yb,
                ((X_lenb - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                y_lenb,
            )
            loss = torch.sum(loss)

            # ---- Backprop ---- #
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            # --------------------------------------------------------
            #                       Eval
            # --------------------------------------------------------
            if batch % 100 == 0:
                self.model.eval()

                allLoss = []
                total_edit_distance, total_seq_length = 0, 0

                with torch.no_grad():
                    for Xt, yt, Xt_len, yt_len, dayt in testLoader:
                        Xt, yt, Xt_len, yt_len, dayt = \
                            Xt.to(self.device), yt.to(self.device), Xt_len.to(self.device), yt_len.to(self.device), dayt.to(self.device)

                        pred = self.model(Xt, dayt)

                        loss = self.loss_ctc(
                            torch.permute(pred.log_softmax(2), [1, 0, 2]),
                            yt,
                            ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                            yt_len,
                        )
                        allLoss.append(loss.cpu().detach().numpy())

                        # ---- Compute CER ---- #
                        adjustedLens = ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32)

                        for i in range(pred.shape[0]):
                            decoded = torch.argmax(pred[i, :adjustedLens[i]], dim=-1)
                            decoded = torch.unique_consecutive(decoded, dim=-1)
                            decoded = decoded.cpu().numpy()
                            decoded = decoded[decoded != 0]

                            trueSeq = yt[i][:yt_len[i]].cpu().numpy()

                            matcher = SequenceMatcher(a=trueSeq.tolist(), b=decoded.tolist())
                            total_edit_distance += matcher.distance()
                            total_seq_length += len(trueSeq)

                avgLoss = np.sum(allLoss) / len(testLoader)
                cer = total_edit_distance / total_seq_length

                print(f"[Batch {batch}] CTC Loss={avgLoss:.4f}, CER={cer:.4f}")

                # ---- Save best model ---- #
                if self.bestCER is None or cer < self.bestCER:
                    self.bestCER = cer
                    torch.save(self.model.state_dict(), self.args["pthDir"] + "/modelWeights")
                    self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                    print(f"✓ Saved best model (CER={cer:.4f})")

                testLoss.append(avgLoss)
                testCER.append(cer)

                startTime = time.time()

        return testLoss, testCER

    # ----------------------------------------------------------
    #                   PREDICT (decoding)
    # ----------------------------------------------------------
    # def predict(self, X, X_len, dayIdx):
    def predict(self, X, dayIdx):
        self.model.eval()
        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        # X_len = torch.tensor(X_len, dtype=torch.int32).to(self.device)
        dayIdx = torch.tensor(dayIdx, dtype=torch.int32).to(self.device)

        with torch.no_grad():
            pred = self.model(X, dayIdx)

        # decoded_all = []
        # for i in range(pred.shape[0]):
        #     L = int((X_len[i] - self.model.kernelLen) / self.model.strideLen)
        #     decoded = torch.argmax(pred[i, :L], dim=-1)
        #     decoded = torch.unique_consecutive(decoded, dim=-1)
        #     decoded = decoded.cpu().numpy()
        #     decoded = decoded[decoded != 0]
        #     decoded_all.append(decoded)

        # return decoded_all
        return pred
    
    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build DecoderLSTMModel_args from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        model = DecoderLSTMModel_args(
            args=model_params,model_params=model_params
        )


        # ---------- 构建模型 ----------
        return model




# ---------------------- Decoder Wrapper Class ---------------------- #
class DecoderLSTMGRUModel_args:
    def __init__(self, args, model_params):
        self.args = args
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = model_params["device"]

        self.model = LSTMGRUDecoder(
            neural_dim=model_params["neural_dim"],
            n_classes=model_params["n_classes"],
            hidden_dim=model_params["hidden_dim"],
            layer_dim=model_params["layer_dim"],
            nDays=model_params["nDays"],
            dropout=model_params["dropout"],
            device=model_params["device"],
            strideLen=model_params["strideLen"],
            kernelLen=model_params["kernelLen"],
            gaussianSmoothWidth=model_params["gaussianSmoothWidth"],
            bidirectional=model_params["bidirectional"],
        ).to(self.device)

        self.loss_ctc = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=True)

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=args["lrStart"],
            betas=(0.9, 0.999),
            eps=0.1,
            weight_decay=args["l2_decay"],
        )

        self.scheduler = torch.optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=1.0,
            end_factor=args["lrEnd"] / args["lrStart"],
            total_iters=args["nBatch"],
        )

        self.bestCER = None

    # ----------------------------------------------------------
    #                       FIT
    # ----------------------------------------------------------
    # def fit(self, X, y, X_len, y_len, dayIdx,
    #         test_X, test_y, test_X_len, test_y_len, test_dayIdx):
        
    def fit(self, X, y, X_len, y_len, dayIdx):
        
        # ----------- 1) 训练 / 验证划分 -----------
        (
            X_train, X_val,
            y_train, y_val,
            Xlen_train, Xlen_val,
            ylen_train, ylen_val,
            dayidx_train, dayidx_val
        ) = train_test_split(
            X, y, X_len, y_len, dayIdx,
            test_size=0.25,
            shuffle=True,
            random_state=42
        )

        # # Build datasets
        # train_ds = SeqDataset(X, y, X_len, y_len, dayIdx)
        # test_ds = SeqDataset(test_X, test_y, test_X_len, test_y_len, test_dayIdx)

            # ----------- 2) Dataset / DataLoader 构建 -----------
        train_ds = SeqDataset(X_train, y_train, Xlen_train, ylen_train, dayidx_train)
        val_ds   = SeqDataset(X_val,   y_val,   Xlen_val,   ylen_val,   dayidx_val)

        trainLoader = DataLoader(train_ds, batch_size=self.args["batchSize"],
                                 shuffle=True, pin_memory=True, num_workers=0)
        testLoader = DataLoader(val_ds, batch_size=self.args["batchSize"],
                                shuffle=False, pin_memory=True, num_workers=0)

        testLoss = []
        testCER = []

        startTime = time.time()

        for batch in range(self.args["nBatch"]):
            self.model.train()

            Xb, yb, X_lenb, y_lenb, dayIdxb = next(iter(trainLoader))
            Xb, yb, X_lenb, y_lenb, dayIdxb = \
                Xb.to(self.device), yb.to(self.device), X_lenb.to(self.device), y_lenb.to(self.device), dayIdxb.to(self.device)

            # ---- Noise Aug ---- #
            if self.args["whiteNoiseSD"] > 0:
                Xb += torch.randn(Xb.shape, device=self.device) * self.args["whiteNoiseSD"]

            if self.args["constantOffsetSD"] > 0:
                Xb += torch.randn([Xb.shape[0], 1, Xb.shape[2]], device=self.device) * self.args["constantOffsetSD"]

            # ---- Forward ---- #
            pred = self.model(Xb, dayIdxb)

            # ---- CTC Loss ---- #
            loss = self.loss_ctc(
                torch.permute(pred.log_softmax(2), [1, 0, 2]),
                yb,
                ((X_lenb - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                y_lenb,
            )
            loss = torch.sum(loss)

            # ---- Backprop ---- #
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            # --------------------------------------------------------
            #                       Eval
            # --------------------------------------------------------
            if batch % 100 == 0:
                self.model.eval()

                allLoss = []
                total_edit_distance, total_seq_length = 0, 0

                with torch.no_grad():
                    for Xt, yt, Xt_len, yt_len, dayt in testLoader:
                        Xt, yt, Xt_len, yt_len, dayt = \
                            Xt.to(self.device), yt.to(self.device), Xt_len.to(self.device), yt_len.to(self.device), dayt.to(self.device)

                        pred = self.model(Xt, dayt)

                        loss = self.loss_ctc(
                            torch.permute(pred.log_softmax(2), [1, 0, 2]),
                            yt,
                            ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                            yt_len,
                        )
                        allLoss.append(loss.cpu().detach().numpy())

                        # ---- Compute CER ---- #
                        adjustedLens = ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32)

                        for i in range(pred.shape[0]):
                            decoded = torch.argmax(pred[i, :adjustedLens[i]], dim=-1)
                            decoded = torch.unique_consecutive(decoded, dim=-1)
                            decoded = decoded.cpu().numpy()
                            decoded = decoded[decoded != 0]

                            trueSeq = yt[i][:yt_len[i]].cpu().numpy()

                            matcher = SequenceMatcher(a=trueSeq.tolist(), b=decoded.tolist())
                            total_edit_distance += matcher.distance()
                            total_seq_length += len(trueSeq)

                avgLoss = np.sum(allLoss) / len(testLoader)
                cer = total_edit_distance / total_seq_length

                print(f"[Batch {batch}] CTC Loss={avgLoss:.4f}, CER={cer:.4f}")

                # ---- Save best model ---- #
                if self.bestCER is None or cer < self.bestCER:
                    self.bestCER = cer
                    torch.save(self.model.state_dict(), self.args["pthDir"] + "/modelWeights")
                    self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                    print(f"✓ Saved best model (CER={cer:.4f})")

                testLoss.append(avgLoss)
                testCER.append(cer)

                startTime = time.time()

        return testLoss, testCER

    # ----------------------------------------------------------
    #                   PREDICT (decoding)
    # ----------------------------------------------------------
    # def predict(self, X, X_len, dayIdx):
    def predict(self, X, dayIdx):
    
        self.model.eval()
        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        # X_len = torch.tensor(X_len, dtype=torch.int32).to(self.device)
        dayIdx = torch.tensor(dayIdx, dtype=torch.int32).to(self.device)

        with torch.no_grad():
            pred = self.model(X, dayIdx)

        # decoded_all = []
        # for i in range(pred.shape[0]):
        #     L = int((X_len[i] - self.model.kernelLen) / self.model.strideLen)
        #     decoded = torch.argmax(pred[i, :L], dim=-1)
        #     decoded = torch.unique_consecutive(decoded, dim=-1)
        #     decoded = decoded.cpu().numpy()
        #     decoded = decoded[decoded != 0]
        #     decoded_all.append(decoded)

        # return decoded_all
        return pred
    
    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build DecoderLSTMGRUModel_args from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        model = DecoderLSTMGRUModel_args(
            args=model_params,model_params=model_params
        )


        # ---------- 构建模型 ----------
        return model




# ---------------------- Decoder Wrapper Class ---------------------- #
class DecoderCNNModel_args:
    def __init__(self, args, model_params):
        self.args = args
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = model_params["device"]

        self.model = CNNDecoder(
            neural_dim=model_params["neural_dim"],
            n_classes=model_params["n_classes"],
            hidden_dim=model_params["hidden_dim"],
            layer_dim=model_params["layer_dim"],
            nDays=model_params["nDays"],
            dropout=model_params["dropout"],
            device=model_params["device"],
            strideLen=model_params["strideLen"],
            kernelLen=model_params["kernelLen"],
            gaussianSmoothWidth=model_params["gaussianSmoothWidth"],
            bidirectional=model_params["bidirectional"],
        ).to(self.device)

        self.loss_ctc = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=True)

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=args["lrStart"],
            betas=(0.9, 0.999),
            eps=0.1,
            weight_decay=args["l2_decay"],
        )

        self.scheduler = torch.optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=1.0,
            end_factor=args["lrEnd"] / args["lrStart"],
            total_iters=args["nBatch"],
        )

        self.bestCER = None
        self.best_state_dict = None

    # ----------------------------------------------------------
    #                       FIT
    # ----------------------------------------------------------
    # def fit(self, X, y, X_len, y_len, dayIdx,
    #         test_X, test_y, test_X_len, test_y_len, test_dayIdx):
        
    def fit(self, X, y, X_len, y_len, dayIdx):
        
        # ----------- 1) 训练 / 验证划分 -----------
        (
            X_train, X_val,
            y_train, y_val,
            Xlen_train, Xlen_val,
            ylen_train, ylen_val,
            dayidx_train, dayidx_val
        ) = train_test_split(
            X, y, X_len, y_len, dayIdx,
            test_size=0.25,
            shuffle=True,
            random_state=42
        )

        # # Build datasets
        # train_ds = SeqDataset(X, y, X_len, y_len, dayIdx)
        # test_ds = SeqDataset(test_X, test_y, test_X_len, test_y_len, test_dayIdx)

            # ----------- 2) Dataset / DataLoader 构建 -----------
        train_ds = SeqDataset(X_train, y_train, Xlen_train, ylen_train, dayidx_train)
        val_ds   = SeqDataset(X_val,   y_val,   Xlen_val,   ylen_val,   dayidx_val)

        trainLoader = DataLoader(train_ds, batch_size=self.args["batchSize"],
                                 shuffle=True, pin_memory=True, num_workers=0)
        testLoader = DataLoader(val_ds, batch_size=self.args["batchSize"],
                                shuffle=False, pin_memory=True, num_workers=0)

        testLoss = []
        testCER = []

        startTime = time.time()

        for batch in range(self.args["nBatch"]):
            self.model.train()

            Xb, yb, X_lenb, y_lenb, dayIdxb = next(iter(trainLoader))
            Xb, yb, X_lenb, y_lenb, dayIdxb = \
                Xb.to(self.device), yb.to(self.device), X_lenb.to(self.device), y_lenb.to(self.device), dayIdxb.to(self.device)

            # ---- Noise Aug ---- #
            if self.args["whiteNoiseSD"] > 0:
                Xb += torch.randn(Xb.shape, device=self.device) * self.args["whiteNoiseSD"]

            if self.args["constantOffsetSD"] > 0:
                Xb += torch.randn([Xb.shape[0], 1, Xb.shape[2]], device=self.device) * self.args["constantOffsetSD"]

            # ---- Forward ---- #
            pred = self.model(Xb, dayIdxb)

            # ---- CTC Loss ---- #
            loss = self.loss_ctc(
                torch.permute(pred.log_softmax(2), [1, 0, 2]),
                yb,
                ((X_lenb - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                y_lenb,
            )
            loss = torch.sum(loss)

            # ---- Backprop ---- #
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            # --------------------------------------------------------
            #                       Eval
            # --------------------------------------------------------
            if batch % 100 == 0:
                self.model.eval()

                allLoss = []
                total_edit_distance, total_seq_length = 0, 0

                with torch.no_grad():
                    for Xt, yt, Xt_len, yt_len, dayt in testLoader:
                        Xt, yt, Xt_len, yt_len, dayt = \
                            Xt.to(self.device), yt.to(self.device), Xt_len.to(self.device), yt_len.to(self.device), dayt.to(self.device)

                        pred = self.model(Xt, dayt)

                        loss = self.loss_ctc(
                            torch.permute(pred.log_softmax(2), [1, 0, 2]),
                            yt,
                            ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32),
                            yt_len,
                        )
                        allLoss.append(loss.cpu().detach().numpy())

                        # ---- Compute CER ---- #
                        adjustedLens = ((Xt_len - self.model.kernelLen) / self.model.strideLen).to(torch.int32)

                        for i in range(pred.shape[0]):
                            decoded = torch.argmax(pred[i, :adjustedLens[i]], dim=-1)
                            decoded = torch.unique_consecutive(decoded, dim=-1)
                            decoded = decoded.cpu().numpy()
                            decoded = decoded[decoded != 0]

                            trueSeq = yt[i][:yt_len[i]].cpu().numpy()

                            matcher = SequenceMatcher(a=trueSeq.tolist(), b=decoded.tolist())
                            total_edit_distance += matcher.distance()
                            total_seq_length += len(trueSeq)

                avgLoss = np.sum(allLoss) / len(testLoader)
                cer = total_edit_distance / total_seq_length

                print(f"[Batch {batch}] CTC Loss={avgLoss:.4f}, CER={cer:.4f}")

                # ---- Save best model ---- #
                if self.bestCER is None or cer < self.bestCER:
                    self.bestCER = cer
                    torch.save(self.model.state_dict(), self.args["pthDir"] + "/modelWeights")
                    # self.best_state_dict = self.model.state_dict()
                    self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                    print(f"✓ Saved best model (CER={cer:.4f})")

                testLoss.append(avgLoss)
                testCER.append(cer)

                startTime = time.time()

        return testLoss, testCER

    # ----------------------------------------------------------
    #                   PREDICT (decoding)
    # ----------------------------------------------------------
    # def predict(self, X, X_len, dayIdx):
    #     self.model.eval()
    #     X = torch.tensor(X, dtype=torch.float32).to(self.device)
    #     X_len = torch.tensor(X_len, dtype=torch.int32).to(self.device)
    #     dayIdx = torch.tensor(dayIdx, dtype=torch.int32).to(self.device)

    #     with torch.no_grad():
    #         pred = self.model(X, dayIdx)

    #     decoded_all = []
    #     for i in range(pred.shape[0]):
    #         L = int((X_len[i] - self.model.kernelLen) / self.model.strideLen)
    #         decoded = torch.argmax(pred[i, :L], dim=-1)
    #         decoded = torch.unique_consecutive(decoded, dim=-1)
    #         decoded = decoded.cpu().numpy()
    #         decoded = decoded[decoded != 0]
    #         decoded_all.append(decoded)

    #     return decoded_all
    

    def predict(self, X, dayIdx):

        if self.best_state_dict is not None:
            self.model.load_state_dict(self.best_state_dict)
        else:
            print("Warning: No best weights stored, did you run fit()?")

        self.model.eval()
        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        # X_len = torch.tensor(X_len, dtype=torch.int32).to(self.device)
        dayIdx = torch.tensor(dayIdx, dtype=torch.int32).to(self.device)

        with torch.no_grad():
            pred = self.model(X, dayIdx)

        return pred
    

    def save_weights(self, path):
         
         torch.save(self.best_state_dict, path)

    def load_weights(self, path):
        try:
            # 加载权重
            state_dict = torch.load(path, map_location=self.device)
            
            # 加载到模型中
            self.model.load_state_dict(state_dict)
            
            # 更新 best_state_dict
            self.best_state_dict = state_dict
            
            print(f" 模型权重已从 {path} 加载")
            
            
        except Exception as e:
            print(f" 加载权重失败: {e}")


    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build DecoderCNNModel_args from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        model = DecoderCNNModel_args(
            args=model_params,model_params=model_params
        )


        # ---------- 构建模型 ----------
        return model