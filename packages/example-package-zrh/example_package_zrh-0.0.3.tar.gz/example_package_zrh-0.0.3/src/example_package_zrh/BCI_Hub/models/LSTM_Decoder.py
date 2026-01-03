import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import numpy as np

import yaml


# form utils import load_config

# ---------------------------------------------------------
# 1. 定义 LSTM 分类网络
# ---------------------------------------------------------
class LSTMClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, num_classes, dropout=0.2):
        super(LSTMClassifier, self).__init__()

        self.lstm = nn.LSTM(
            input_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        # print(f"self.fc = nn.Linear({hidden_dim}, {num_classes})")

        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        # x: (batch, time, channels)
        out, _ = self.lstm(x)
        out = out[:, -1, :]          # 最后一个时间步
        out = self.fc(out)
        return out


class CNNClassifier(nn.Module):
    def __init__(self, n_channels, n_classes, 
                 channels=[64, 128], 
                 kernel_sizes=[5, 5],
                 use_batchnorm=True,
                 pooling_type='avg',
                 dropout_rate=0.5):
        """
        可配置参数的EEGCNN模型
        
        Args:
            n_channels: 输入通道数
            n_classes: 分类类别数
            channels: 各层通道数列表，例如 [64, 128]
            kernel_sizes: 各层卷积核大小列表
            use_batchnorm: 是否使用批归一化
            pooling_type: 池化类型 'avg' 或 'max'
            dropout_rate: Dropout比率
        """
        super().__init__()
        
        assert len(channels) == len(kernel_sizes), "channels和kernel_sizes长度必须一致"
        
        layers = []
        in_channels = n_channels
        
        # 构建卷积层
        for i, (out_channels, kernel_size) in enumerate(zip(channels, kernel_sizes)):
            padding = kernel_size // 2  # 保持时间维度不变
            layers.append(nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding))
            
            if use_batchnorm:
                layers.append(nn.BatchNorm1d(out_channels))
            
            layers.append(nn.ReLU())
            
            # 除了最后一层外添加dropout
            if i < len(channels) - 1 and dropout_rate > 0:
                layers.append(nn.Dropout(dropout_rate))
            
            in_channels = out_channels
        
        self.conv_layers = nn.Sequential(*layers)
        
        # 池化层
        if pooling_type == 'avg':
            self.pool = nn.AdaptiveAvgPool1d(1)
        elif pooling_type == 'max':
            self.pool = nn.AdaptiveMaxPool1d(1)
        else:
            raise ValueError("pooling_type必须是 'avg' 或 'max'")
        
        # 全连接层
        self.fc = nn.Linear(channels[-1], n_classes)
        
    def forward(self, x):
        # x: (batch, time, channels) -> (batch, channels, time)
        x = x.permute(0, 2, 1)
        x = self.conv_layers(x)
        x = self.pool(x).squeeze(-1)
        x = self.fc(x)
        return x

# ---------------------------------------------------------
# 2. LSTM 解码器类
# ---------------------------------------------------------
class LSTM_ClassificationDecoder:

    def __init__(self,
                 input_dim,
                 num_classes,
                 hidden_dim=64,
                 num_layers=2,
                 lr=1e-3,
                 batch_size=64,
                 epochs=100,
                 device="cuda:0"):

        self.device = device
        self.batch_size = batch_size
        self.epochs = epochs

        # 网络
        self.model = LSTMClassifier(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            num_classes=num_classes
        ).to(device)

        # self.model = CNNClassifier(
        #     n_channels=input_dim,
        #     n_classes=num_classes).to(device)

        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        # 保存最优模型
        self.best_state_dict = None
        self.best_val_acc = -1


    # -----------------------------------------------------
    # 训练：保存验证集准确率最高的模型权重
    # -----------------------------------------------------
    def fit(self, X, y):

        # 确保 numpy → torch
        X = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.long)

        # 划分训练与验证
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.25, shuffle=True, stratify=y
        )

        train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
        val_dataset = torch.utils.data.TensorDataset(X_val, y_val)

        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=self.batch_size)

        # ---------------- Training Loop ----------------
        for epoch in range(self.epochs):
            self.model.train()
            for xb, yb in train_loader:
                xb = xb.to(self.device)
                yb = yb.to(self.device)

                pred = self.model(xb)
                loss = self.loss_fn(pred, yb)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            # ---------------- Validation ----------------
            val_acc = self.evaluate(val_loader)
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

            print(f"Epoch {epoch+1}/{self.epochs}, Val ACC={val_acc:.4f}")

        print(f"\n🔥 Best Val ACC = {self.best_val_acc:.4f}\n")


    # -----------------------------------------------------
    # 验证函数
    # -----------------------------------------------------
    def evaluate(self, loader):
        self.model.eval()
        preds = []
        labels = []

        with torch.no_grad():
            for xb, yb in loader:
                xb = xb.to(self.device)
                out = self.model(xb)
                pred = out.argmax(dim=1).cpu().numpy()

                preds.append(pred)
                labels.append(yb.numpy())

        preds = np.concatenate(preds)
        labels = np.concatenate(labels)
        return accuracy_score(labels, preds)


    # -----------------------------------------------------
    # 预测：使用训练中验证集最优权重 best_state_dict
    # -----------------------------------------------------
    def predict(self, X_test):

        # 加载最优模型
        if self.best_state_dict is not None:
            self.model.load_state_dict(self.best_state_dict)
        else:
            print("Warning: No best weights found! Did you run fit()?")

        X_test = torch.tensor(X_test, dtype=torch.float32).to(self.device)

        self.model.eval()
        with torch.no_grad():
            out = self.model(X_test)
            preds = out.argmax(dim=1).cpu().numpy()

        return preds
    
    # ======================================================
    # ✔ 严格模式 build_model
    # ======================================================
    @staticmethod
    def build_model(model_params: dict):
    # def build_model(path: str):
        """
        Build LSTM_ClassificationDecoder from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        # with open(path, "r") as f:
        #     model_params = yaml.safe_load(f)

        # ---------- 必须参数 ----------
        if "input_dim" not in model_params:
            raise KeyError(
                "[LSTM_ClassificationDecoder] Missing required parameter: `input_dim`"
            )

        if "num_classes" not in model_params and "output_dim" not in model_params:
            raise KeyError(
                "[LSTM_ClassificationDecoder] Missing required parameter: "
                "`num_classes` or `output_dim`"
            )

        # 统一类别参数名
        num_classes = (
            model_params["num_classes"]
            if "num_classes" in model_params
            else model_params["output_dim"]
        )

        # ---------- 构建模型 ----------
        return LSTM_ClassificationDecoder(
            input_dim=int(model_params["input_dim"]),
            num_classes=int(num_classes),
            hidden_dim=int(model_params.get("hidden_dim", 64)),
            num_layers=int(model_params.get("num_layers", 2)),
            lr=float(model_params.get("lr", 1e-3)),
            batch_size=int(model_params.get("batch_size", 64)),
            epochs=int(model_params.get("epochs", 100)),
            device=model_params.get("device", "cuda:0"),
        )
    
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
    

# ---------------------------------------------------------
# 2. CNN 解码器类（结构仿照你的 CEBRA + LR）
# ---------------------------------------------------------
class CNN_ClassificationDecoder:

    def __init__(self,
                 input_dim,
                 num_classes,
                 channels=[64, 128],
                 kernel_sizes=[5, 5],
                 lr=1e-3,
                 batch_size=64,
                 epochs=100,
                 device="cuda:0"):

        self.device = device
        self.batch_size = batch_size
        self.epochs = epochs

        # 网络
        # self.model = LSTMClassifier(
        #     input_dim=input_dim,
        #     hidden_dim=hidden_dim,
        #     num_layers=num_layers,
        #     num_classes=num_classes
        # ).to(device)

        self.model = CNNClassifier(
            n_channels=input_dim,
            n_classes=num_classes,
            channels=channels,
            kernel_sizes=kernel_sizes).to(device)

        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        # 保存最优模型
        self.best_state_dict = None
        self.best_val_acc = -1


    # -----------------------------------------------------
    # 训练：保存验证集准确率最高的模型权重
    # -----------------------------------------------------
    def fit(self, X, y):

        # 确保 numpy → torch
        X = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.long)

        # 划分训练与验证
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.25, shuffle=True, stratify=y
        )

        train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
        val_dataset = torch.utils.data.TensorDataset(X_val, y_val)

        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=self.batch_size)

        # ---------------- Training Loop ----------------
        for epoch in range(self.epochs):
            self.model.train()
            for xb, yb in train_loader:
                xb = xb.to(self.device)
                yb = yb.to(self.device)

                pred = self.model(xb)
                loss = self.loss_fn(pred, yb)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            # ---------------- Validation ----------------
            val_acc = self.evaluate(val_loader)
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

            print(f"Epoch {epoch+1}/{self.epochs}, Val ACC={val_acc:.4f}")

        print(f"\n🔥 Best Val ACC = {self.best_val_acc:.4f}\n")


    # -----------------------------------------------------
    # 验证函数
    # -----------------------------------------------------
    def evaluate(self, loader):
        self.model.eval()
        preds = []
        labels = []

        with torch.no_grad():
            for xb, yb in loader:
                xb = xb.to(self.device)
                out = self.model(xb)
                pred = out.argmax(dim=1).cpu().numpy()

                preds.append(pred)
                labels.append(yb.numpy())

        preds = np.concatenate(preds)
        labels = np.concatenate(labels)
        return accuracy_score(labels, preds)


    # -----------------------------------------------------
    # 预测：使用训练中验证集最优权重 best_state_dict
    # -----------------------------------------------------
    def predict(self, X_test):

        # 加载最优模型
        if self.best_state_dict is not None:
            self.model.load_state_dict(self.best_state_dict)
        else:
            print("Warning: No best weights found! Did you run fit()?")

        X_test = torch.tensor(X_test, dtype=torch.float32).to(self.device)

        self.model.eval()
        with torch.no_grad():
            out = self.model(X_test)
            preds = out.argmax(dim=1).cpu().numpy()

        return preds
    



import torch
import torch.nn as nn
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


# -----------------------------
# LSTM 网络结构（回归输出）
# -----------------------------
class LSTMRegressor(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=1, output_dim=1):
        super().__init__()

        self.lstm = nn.LSTM(
            input_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True
        )

        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]          # 取最后一个时间步
        out = self.fc(out)
        return out
    
class CNN_Regressor(nn.Module):
    def __init__(self, n_channels, output_dim,
                 channels=[64, 128],
                 kernel_sizes=[5, 5],
                 use_batchnorm=True,
                 dropout_rate=0.5):
        """
        CNN 用于回归任务（输出连续值）
        
        Args:
            n_channels: 输入信号通道数
            output_dim: 回归输出维度，例如 2 (x, y)
        """
        super().__init__()
        
        assert len(channels) == len(kernel_sizes), "channels 和 kernel_sizes 长度必须一致"
        
        layers = []
        in_channels = n_channels
        
        for i, (out_channels, kernel_size) in enumerate(zip(channels, kernel_sizes)):
            padding = kernel_size // 2
            layers.append(nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding))
            
            if use_batchnorm:
                layers.append(nn.BatchNorm1d(out_channels))
            
            layers.append(nn.ReLU())
            
            if i < len(channels) - 1 and dropout_rate > 0:
                layers.append(nn.Dropout(dropout_rate))
            
            in_channels = out_channels
        
        self.conv_layers = nn.Sequential(*layers)
        
        # --- 修改为回归任务 ---
        self.fc = nn.Linear(channels[-1], output_dim)
    
    def forward(self, x):
        # x: (batch, time, channels) -> (batch, channels, time)
        x = x.permute(0, 2, 1)
        x = self.conv_layers(x)

        # 使用 CNN 的最后一个时间步的特征进行回归
        x_last = x[:, :, -1]  # (batch, channels[-1])
        out = self.fc(x_last)
        return out




# -----------------------------------------------------
# LSTM 回归解码器
# -----------------------------------------------------
class LSTM_RegressionDecoder:
    def __init__(
            self,
            input_dim,
            output_dim=1,
            hidden_dim=64,
            num_layers=1,
            batch_size=128,
            epochs=100,
            lr=1e-3,
            device="cuda:0"
    ):

        self.device = device
        self.batch_size = batch_size
        self.epochs = epochs

        # 模型
        self.model = LSTMRegressor(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            output_dim=output_dim
        ).to(device)

        # self.model = CNN_Regressor(n_channels=input_dim, output_dim=output_dim).to(device)

        # print(f"self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)", float(lr))


        # self.loss_fn = nn.MSELoss()
        self.loss_fn = nn.SmoothL1Loss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        # self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)

        

        # 保存最佳权重
        self.best_state_dict = None
        self.best_val_r2 = -999


    # -----------------------------------------------------
    # 训练流程：保存验证集 R² 最佳的参数
    # -----------------------------------------------------
    def fit(self, X, y):

        
        # 只取最后一个时间步
        y = y[:, -1, :]   # (N, 2)

        X = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.float32)

        # 划分训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
        val_dataset = torch.utils.data.TensorDataset(X_val, y_val)

        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.batch_size, shuffle=False)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=self.batch_size)

        # ---------------- Training Loop ----------------
        for epoch in range(self.epochs):
            self.model.train()

            for xb, yb in train_loader:
                xb = xb.to(self.device)
                yb = yb.to(self.device)

                pred = self.model(xb)
                loss = self.loss_fn(pred, yb)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            # ---------------- Validation ----------------
            val_r2 = self.evaluate(val_loader)

            if val_r2 > self.best_val_r2:
                self.best_val_r2 = val_r2
                self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

            print(f"Epoch {epoch+1}/{self.epochs}, Val R2 = {val_r2:.4f}")

        print(f"\n Best Validation R2 = {self.best_val_r2:.4f}\n")


    # -----------------------------------------------------
    # 验证函数：返回 R²
    # -----------------------------------------------------
    def evaluate(self, loader):
        self.model.eval()
        preds = []
        labels = []

        with torch.no_grad():
            for xb, yb in loader:
                xb = xb.to(self.device)
                out = self.model(xb).cpu().numpy()

                preds.append(out)
                labels.append(yb.numpy())

        preds = np.concatenate(preds).squeeze()
        labels = np.concatenate(labels).squeeze()

        return r2_score(labels, preds)


    # -----------------------------------------------------
    # 预测：使用训练中验证集 R² 最好时的权重
    # -----------------------------------------------------
    def predict(self, X_test):

        if self.best_state_dict is not None:
            self.model.load_state_dict(self.best_state_dict)
        else:
            print("Warning: No best weights stored, did you run fit()?")

        X_test = torch.tensor(X_test, dtype=torch.float32).to(self.device)

        self.model.eval()
        with torch.no_grad():
            out = self.model(X_test)

        return out.cpu().numpy().squeeze()
    
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

    # ======================================================
    # ✔ 严格模式 build_model
    # ======================================================
    @staticmethod
    def build_model(model_params: dict, path=None):
    # def build_model(path: str):
        """
        Build LSTM_ClassificationDecoder from config dict.
        `input_dim` and `num_classes` are REQUIRED.
        """

        # with open(path, "r") as f:
        #     model_params = yaml.safe_load(f)

        # ---------- 必须参数 ----------
        if "input_dim" not in model_params:
            raise KeyError(
                "[LSTM_ClassificationDecoder] Missing required parameter: `input_dim`"
            )

        if "num_classes" not in model_params and "output_dim" not in model_params:
            raise KeyError(
                "[LSTM_ClassificationDecoder] Missing required parameter: "
                "`num_classes` or `output_dim`"
            )

        # 统一类别参数名
        num_classes = (
            model_params["num_classes"]
            if "num_classes" in model_params
            else model_params["output_dim"]
        )

        # ---------- 构建模型 ----------
        return LSTM_RegressionDecoder(
            input_dim=int(model_params["input_dim"]),
            output_dim=int(num_classes),
            hidden_dim=int(model_params.get("hidden_dim", 64)),
            num_layers=int(model_params.get("num_layers", 2)),
            lr=float(model_params.get("lr", 1e-3)),
            batch_size=int(model_params.get("batch_size", 64)),
            epochs=int(model_params.get("epochs", 100)),
            device=model_params.get("device", "cuda:0"),
        )
    

            
    

# -----------------------------------------------------
# CNN 回归解码器
# -----------------------------------------------------
class CNN_RegressionDecoder:
    def __init__(
            self,
            input_dim,
            output_dim=1,
            channels=[64, 128],
            kernel_sizes=[5,5],
            batch_size=128,
            epochs=100,
            lr=1e-3,
            device="cuda:0"
    ):

        self.device = device
        self.batch_size = batch_size
        self.epochs = epochs

        # 模型
        # self.model = LSTMRegressor(
        #     input_dim=input_dim,
        #     hidden_dim=hidden_dim,
        #     num_layers=num_layers,
        #     output_dim=output_dim
        # ).to(device)

        self.model = CNN_Regressor(n_channels=input_dim, output_dim=output_dim, channels=channels, kernel_sizes=kernel_sizes).to(device)


        # self.loss_fn = nn.MSELoss()
        self.loss_fn = nn.SmoothL1Loss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        # 保存最佳权重
        self.best_state_dict = None
        self.best_val_r2 = -999


    # -----------------------------------------------------
    # 训练流程：保存验证集 R² 最佳的参数
    # -----------------------------------------------------
    def fit(self, X, y):

        
        # 只取最后一个时间步
        y = y[:, -1, :]   # (N, 2)

        X = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.float32)

        # 划分训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
        val_dataset = torch.utils.data.TensorDataset(X_val, y_val)

        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=self.batch_size, shuffle=False)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=self.batch_size)

        # ---------------- Training Loop ----------------
        for epoch in range(self.epochs):
            self.model.train()

            for xb, yb in train_loader:
                xb = xb.to(self.device)
                yb = yb.to(self.device)

                pred = self.model(xb)
                loss = self.loss_fn(pred, yb)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            # ---------------- Validation ----------------
            val_r2 = self.evaluate(val_loader)

            if val_r2 > self.best_val_r2:
                self.best_val_r2 = val_r2
                self.best_state_dict = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

            print(f"Epoch {epoch+1}/{self.epochs}, Val R2 = {val_r2:.4f}")

        print(f"\n🔥 Best Validation R2 = {self.best_val_r2:.4f}\n")


    # -----------------------------------------------------
    # 验证函数：返回 R²
    # -----------------------------------------------------
    def evaluate(self, loader):
        self.model.eval()
        preds = []
        labels = []

        with torch.no_grad():
            for xb, yb in loader:
                xb = xb.to(self.device)
                out = self.model(xb).cpu().numpy()

                preds.append(out)
                labels.append(yb.numpy())

        preds = np.concatenate(preds).squeeze()
        labels = np.concatenate(labels).squeeze()

        return r2_score(labels, preds)


    # -----------------------------------------------------
    # 预测：使用训练中验证集 R² 最好时的权重
    # -----------------------------------------------------
    def predict(self, X_test):

        if self.best_state_dict is not None:
            self.model.load_state_dict(self.best_state_dict)
        else:
            print("⚠️ Warning: No best weights stored, did you run fit()?")

        X_test = torch.tensor(X_test, dtype=torch.float32).to(self.device)

        self.model.eval()
        with torch.no_grad():
            out = self.model(X_test)

        return out.cpu().numpy().squeeze()


    
import numpy as np

def generate_regression_mock_data(N=2000, seq_len=50, x_dim=16):
    """
    模拟 LSTM 回归任务的数据：
    X: (N, 50, x_dim)
    y: (N, 50, 2)
    
    y 的规则为：
    y[t] = [ sum(X[t]), mean(X[t]) ] + noise
    """
    X = np.random.randn(N, seq_len, x_dim).astype(np.float32)

    y = np.zeros((N, seq_len, 2), dtype=np.float32)
    for i in range(N):
        for t in range(seq_len):
            s = X[i, t].sum()
            m = X[i, t].mean()
            y[i, t, 0] = s + 0.1*np.random.randn()       # 第1个输出
            y[i, t, 1] = m + 0.1*np.random.randn()       # 第2个输出

    return X, y

import numpy as np

def generate_synthetic_classification_data(
        N=1000,     # 样本数量
        T=50,       # 时间步
        C=16,       # 通道数
        num_classes=3,  # 分类类别
        noise_level=0.1 # 噪声水平
    ):
    """
    生成 EEG 风格的分类模拟数据 X, y
    X shape = (N, T, C)
    y shape = (N,)
    """
    X = np.zeros((N, T, C), dtype=np.float32)
    y = np.zeros((N,), dtype=np.int64)

    for i in range(N):
        label = np.random.randint(0, num_classes)
        y[i] = label

        # -------- 不同类别具有不同的频率模式 --------
        freq = 1 + label   # 类别 0 → 1Hz, 类别 1 → 2Hz, 类别 2 → 3Hz

        t = np.linspace(0, 1, T)

        # 每个通道都有轻微变化
        signal = np.sin(2 * np.pi * freq * t)[..., None]  # (T, 1)
        signal = np.repeat(signal, C, axis=1)

        # 加一些随机的权重扰动
        signal *= (1 + 0.1 * np.random.randn(C))

        # 添加噪声
        noise = noise_level * np.random.randn(T, C)

        X[i] = signal + noise

    return X, y






if __name__ == "__main__":
    # 简单测试
    # X_dummy = np.random.rand(1000, 10, 16)  # (samples, time_steps, features)
    # y_dummy = np.random.randint(0, 5, size=(1000,))  # 5 classes

    # 测试一下
    X, y = generate_synthetic_classification_data()
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    print("Class distribution:", np.bincount(y))

    decoder = LSTM_ClassificationDecoder(
        input_dim=16,
        num_classes=3,
        hidden_dim=32,
        num_layers=1,
        lr=1e-3,
        batch_size=32,
        epochs=10,
        device="cuda:0"
    )

    decoder.fit(X[:800,:,:], y[:800])
    preds = decoder.predict(X[800:,:,:])

    acc = accuracy_score(y[800:], preds)
    print(f"Test Accuracy: {acc:.4f}")




    # 生成模拟数据
    X, y = generate_regression_mock_data(N=2000, seq_len=50, x_dim=16)

    decoder = LSTM_RegressionDecoder(
        input_dim=16,
        output_dim=2,
        device="cuda:0"
    )



    decoder.fit(X, y)

    # 预测最后一个时间步
    y_pred = decoder.predict(X[:10])
    print("Pred:", y_pred.shape)






