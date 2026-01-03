import numpy as np
from sklearn.preprocessing import StandardScaler

def generate_cross_day_data(
    n_samples=2000, n_features=20, n_classes=5, drift_strength=1.5
):
    """
    跨天模拟数据：
    Day1 = Day0 * RandomRotation + noise
    """

    # Day0 数据
    X0 = np.random.randn(n_samples, n_features)
    y0 = np.random.randint(0, n_classes, n_samples)

    # ----------------------
    # 构造跨天漂移：线性旋转 + 加性偏移
    # ----------------------
    Q, _ = np.linalg.qr(np.random.randn(n_features, n_features))  # 正交矩阵（旋转）
    drift = drift_strength * np.random.randn(1, n_features)       # 平移

    X1 = X0 @ Q + drift + 0.05 * np.random.randn(*X0.shape)
    y1 = y0.copy()

    # 标准化
    scaler = StandardScaler()
    X0 = scaler.fit_transform(X0)
    X1 = scaler.transform(X1)

    return X0, y0, X1, y1



class IdentityAligner:
    def fit(self, X_src, X_tgt):
        return self
    
    def transform(self, X):
        return X


import numpy as np

class LinearAligner:
    def fit(self, X_src, X_tgt):
        # X_tgt * W ≈ X_src
        self.W, _, _, _ = np.linalg.lstsq(X_tgt, X_src, rcond=None)
        return self

    def transform(self, X):
        return X @ self.W


import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

class MLPDecoder(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.net(x)


class DecoderWrapper:
    def __init__(self, model, lr=1e-3, device="cuda:0"):
        self.model = model.to(device)
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        self.loss_fn = nn.CrossEntropyLoss()
        self.device = device
        self.best_state = None
        self.best_val_acc = -1

    # -----------------------------
    # 训练 + 保存最佳权重
    # -----------------------------
    def fit(self, X, y):
        X = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.long)

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, stratify=y
        )

        train_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(X_train, y_train), 
            batch_size=128, shuffle=True
        )
        val_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(X_val, y_val), 
            batch_size=128
        )

        for epoch in range(20):
            self.model.train()
            for xb, yb in train_loader:
                xb, yb = xb.to(self.device), yb.to(self.device)

                pred = self.model(xb)
                loss = self.loss_fn(pred, yb)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            acc = self.evaluate(val_loader)
            if acc > self.best_val_acc:
                self.best_val_acc = acc
                self.best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}

            print(f"Epoch {epoch+1}: val acc = {acc:.4f}")

    # -----------------------------
    def evaluate(self, loader):
        self.model.eval()
        preds, labels = [], []
        with torch.no_grad():
            for xb, yb in loader:
                out = self.model(xb.to(self.device))
                pred = out.argmax(1).cpu().numpy()

                preds.append(pred)
                labels.append(yb.numpy())

        return accuracy_score(np.concatenate(labels), np.concatenate(preds))

    # -----------------------------
    def predict(self, X):
        self.model.load_state_dict(self.best_state)
        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            out = self.model(X)
            return out.argmax(1).cpu().numpy()



class CrossDayDecoder:
    def __init__(self, aligner, decoder):
        self.aligner = aligner      # 如 LinearAligner()
        self.decoder = decoder      # 如 DecoderWrapper(MLPDecoder(...))

    # -------------------------------------
    # 训练：训练 Day0 解码器 + Day1→Day0 对齐器
    # -------------------------------------
    def fit(self, X0, y0, X1):
        print("Training decoder on Day0...")
        self.decoder.fit(X0, y0)

        print("Training aligner Day1 → Day0...")
        self.aligner.fit(X0, X1)

    # -------------------------------------
    # 预测：对齐 Day1 → 用 Day0 模型解码
    # -------------------------------------
    def predict(self, X1):
        X1_aligned = self.aligner.transform(X1)
        return self.decoder.predict(X1_aligned)
    


    
from models.wiener_filter import format_data_from_trials, train_wiener_filter, test_wiener_filter
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score

# from wiener_filter import format_data_from_trials, train_wiener_filter, test_wiener_filter
# from sklearn.model_selection import KFold
# from sklearn.metrics import r2_score

class WienerFilterDecoder:
    def __init__(self, n_lags=4, l2=1.0):
        self.n_lags = n_lags
        self.l2 = l2

        self.H = None   # 最终的 Wiener 权重
        self.best_H = None
        self.best_r2 = -1e9

    # -----------------------------------------------------
    # Fit：可以输入 trial 列表（跨天解码 X0, y0 也能兼容）
    # -----------------------------------------------------
    def fit(self, X_list, Y_list, X_val_list=None, Y_val_list=None):
        """
        X_list : list of (T, C)
        Y_list : list of (T, D)

        如果给定 val，会在验证集上选择 best_H
        """

        # --- 训练集处理 ---
        X_train, Y_train = format_data_from_trials(X_list, Y_list, self.n_lags)
        self.H = train_wiener_filter(X_train, Y_train, l2=self.l2)

        # --- 无验证集：直接返回 ---
        if X_val_list is None:
            self.best_H = self.H
            return

        # --- 验证集 ---
        X_val, Y_val = format_data_from_trials(X_val_list, Y_val_list, self.n_lags)
        Y_pred = test_wiener_filter(X_val, self.H)

        r2 = r2_score(Y_val, Y_pred, multioutput="variance_weighted")

        if r2 > self.best_r2:
            self.best_r2 = r2
            self.best_H = self.H

    # -----------------------------------------------------
    # Predict：使用 best_H
    # -----------------------------------------------------
    def predict(self, X_list):
        if self.best_H is None:
            print("⚠ Warning: best_H is None, using H")
            self.best_H = self.H

        X_test, _ = format_data_from_trials(X_list, X_list, self.n_lags)  # y dummy
        return test_wiener_filter(X_test, self.best_H)

    # -----------------------------------------------------
    # Evaluate：R²
    # -----------------------------------------------------
    def evaluate(self, X_list, Y_list):
        X_test, Y_test = format_data_from_trials(X_list, Y_list, self.n_lags)
        Y_pred = test_wiener_filter(X_test, self.best_H)

        mr2 = r2_score(Y_test, Y_pred, multioutput="variance_weighted")
        # r2_each = r2_score(Y_test, Y_pred, multioutput="raw_values")
        return mr2
    
    # # -----------------------------------------------------
    # # 加载最佳权重（例如 *.npy 文件）
    # # -----------------------------------------------------
    # def load_weights(self, weight_matrix):
    #     """
    #     weight_matrix: numpy array of shape (C*n_lags+1, D)
    #                    通常是 np.load('day0_decoder.npy')

    #     用于跨天时直接加载 day-0 decoder 权重。
    #     """
    #     # weight_matrix = np.array(weight_matrix)
    #     self.best_H = weight_matrix
    #     print(f"✓ Loaded external Wiener weights, shape={self.best_H.shape}")


    # -----------------------------------------------------
    # Load best weights from .npy
    # -----------------------------------------------------
    def load_weights(self, path):
        """
        加载最优 Wiener 权重
        """
        self.best_H = np.load(path)
        print(f"✓ Loaded Wiener weights from {path}, shape={self.best_H.shape}")

    # -----------------------------------------------------
    # Save best weights to .npy
    # -----------------------------------------------------
    def save_weights(self, path):
        """
        保存最优 Wiener 权重到文件
        path : 文件路径，例如 'day0_decoder.npy'
        """
        if self.best_H is None:
            raise ValueError("best_H is None, cannot save.")
        np.save(path, self.best_H)
        print(f"✓ Saved Wiener weights to {path}, shape={self.best_H.shape}")


    
import torch
import torch.nn as nn

# from wiener_filter import train_cycle_gan_aligner, test_cycle_gan_aligner, train_cycle_gan_aligner_Merge, train_cycle_gan_aligner_Merge_Pth
from models.wiener_filter import train_cycle_gan_aligner, test_cycle_gan_aligner, train_cycle_gan_aligner_Merge, train_cycle_gan_aligner_Merge_Pth, train_cycle_gan_aligner_Merge_Pth_LSTM, train_cycle_gan_aligner_Merge_Pth_LSTM_Classifier

class CycleGANAligner:
    """
    Wrap the original CycleGAN-based aligner into a pluggable aligner class.

    Required external functions:
        - train_cycle_gan_aligner()
        - test_cycle_gan_aligner()

    Goal: same interface as CEBRAAligner, LinearAligner, etc.
    """

    def __init__(self, 
                 D_params,
                 G_params,
                 training_params,
                 day0_decoder,
                 n_lags,
                 decoder_path,
                 device="cuda"):
        
        self.D_params = D_params
        self.G_params = G_params
        self.training_params = training_params
        self.day0_decoder = day0_decoder
        self.n_lags = n_lags
        self.decoder_pth = decoder_path
        self.device = device

        # The actual CycleGAN network (to be set after training)
        self.model = None


    # ---------------------- FIT ---------------------- #
    def fit(self, X0, y0, Xk, yk):
        """ 
        X0: day0 spike trials
        Xk: dayK spike trials
        yk: dayK labels  (required by original cycleGAN training)
        """
        print("🔧 Training CycleGANAligner ...")

        # 75% training split (follow the original script)
        # n_train = int(len(X0) * 0.75)

        # X0_train = X0[:n_train]
        # Xk_train = Xk[:n_train]
        # yk_train = yk[:n_train]

        X0_train = X0
        y0_train = y0
        Xk_train = Xk
        yk_train = yk

        # ---- train CycleGAN aligner ----
        self.model, self.decoder, self.dayk_on_day0 = train_cycle_gan_aligner_Merge_Pth(
            X0_train,
            y0_train,
            Xk_train,
            yk_train,
            self.D_params,
            self.G_params,
            self.training_params,
            self.day0_decoder,
            self.n_lags,
            self.decoder_pth
        )

        print("🎉 Aligner training finished!")
        return self.model, self.decoder, self.dayk_on_day0


    # ---------------------- TRANSFORM ---------------------- #
    def transform(self, Xk):
        """
        Apply trained aligner to day-k spike data.
        """
        if self.model is None:
            raise ValueError("Aligner has not been trained. Call fit() first.")

        print("🔄 Running CycleGANAligner.transform ...")

        # In the original script:
        # dayk_spike_aligned = test_cycle_gan_aligner(aligner, dayk_spike_)
        aligned = test_cycle_gan_aligner(self.model, Xk)

        return aligned
    
    def predict(self, Xk):

        return self.transform(Xk)
    



class CycleGANLSTMAligner:
    """
    Wrap the original CycleGAN-based aligner into a pluggable aligner class.

    Required external functions:
        - train_cycle_gan_aligner()
        - test_cycle_gan_aligner()

    Goal: same interface as CEBRAAligner, LinearAligner, etc.
    """

    def __init__(self, 
                 D_params,
                 G_params,
                 training_params,
                 day0_decoder,
                 n_lags,
                 decoder_path,
                 device="cuda"):
        
        self.D_params = D_params
        self.G_params = G_params
        self.training_params = training_params
        self.day0_decoder = day0_decoder
        self.n_lags = n_lags
        self.decoder_pth = decoder_path
        self.device = device

        # The actual CycleGAN network (to be set after training)
        self.model = None


    # ---------------------- FIT ---------------------- #
    def fit(self, X0, y0, Xk, yk):
        """ 
        X0: day0 spike trials
        Xk: dayK spike trials
        yk: dayK labels  (required by original cycleGAN training)
        """
        print("🔧 Training CycleGANAligner ...")

        # 75% training split (follow the original script)
        # n_train = int(len(X0) * 0.75)

        # X0_train = X0[:n_train]
        # Xk_train = Xk[:n_train]
        # yk_train = yk[:n_train]

        X0_train = X0
        y0_train = y0
        Xk_train = Xk
        yk_train = yk

        # ---- train CycleGAN aligner ----
        self.model, self.decoder, self.dayk_on_day0 = train_cycle_gan_aligner_Merge_Pth_LSTM(
            X0_train,
            y0_train,
            Xk_train,
            yk_train,
            self.D_params,
            self.G_params,
            self.training_params,
            self.day0_decoder,
            self.n_lags,
            self.decoder_pth
        )

        print("🎉 Aligner training finished!")
        return self.model, self.decoder, self.dayk_on_day0


    # ---------------------- TRANSFORM ---------------------- #
    def transform(self, Xk):
        """
        Apply trained aligner to day-k spike data.
        """
        if self.model is None:
            raise ValueError("Aligner has not been trained. Call fit() first.")

        print("🔄 Running CycleGANAligner.transform ...")

        # In the original script:
        # dayk_spike_aligned = test_cycle_gan_aligner(aligner, dayk_spike_)
        aligned = test_cycle_gan_aligner(self.model, Xk)

        return aligned
    
    def predict(self, Xk):

        return self.transform(Xk)
    

    # ======================================================
    # ✔ 严格模式 build_model
    # ======================================================
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

        from models.LSTM_Decoder import LSTM_RegressionDecoder

        decoder = LSTM_RegressionDecoder(
                input_dim=model_params.get("LSTM_RegressionDecoder").get("input_dim"),
                output_dim=model_params.get("LSTM_RegressionDecoder").get("output_dim"),
                hidden_dim=model_params.get("LSTM_RegressionDecoder").get("hidden_dim", 64),
                num_layers=model_params.get("LSTM_RegressionDecoder").get("num_layers", 2),
                lr=model_params.get("LSTM_RegressionDecoder").get("lr", 1e-3),
                batch_size=model_params.get("LSTM_RegressionDecoder").get("batch_size", 64),
                epochs=model_params.get("LSTM_RegressionDecoder").get("epochs", 100),
                device=model_params.get("LSTM_RegressionDecoder").get("device", "cuda:0")
            )

        model = CycleGANLSTMAligner(
                model_params.get("D_params"),
                model_params.get("G_params"),
                model_params.get("training_params"),
                decoder,
                n_lags=model_params.get("n_lags", 4),
                decoder_path=model_params.get("decoder_path", ""),
                device=model_params.get("device", "cuda:0")
            )


        # ---------- 构建模型 ----------
        return model
    

class CycleGANLSTMClassificationAligner:
    """
    Wrap the original CycleGAN-based aligner into a pluggable aligner class.

    Required external functions:
        - train_cycle_gan_aligner()
        - test_cycle_gan_aligner()

    Goal: same interface as CEBRAAligner, LinearAligner, etc.
    """

    def __init__(self, 
                 D_params,
                 G_params,
                 training_params,
                 day0_decoder,
                 n_lags,
                 decoder_path,
                 device="cuda"):
        
        self.D_params = D_params
        self.G_params = G_params
        self.training_params = training_params
        self.day0_decoder = day0_decoder
        self.n_lags = n_lags
        self.decoder_pth = decoder_path
        self.device = device

        # The actual CycleGAN network (to be set after training)
        self.model = None


    # ---------------------- FIT ---------------------- #
    def fit(self, X0, y0, Xk, yk):
        """ 
        X0: day0 spike trials
        Xk: dayK spike trials
        yk: dayK labels  (required by original cycleGAN training)
        """
        print("🔧 Training CycleGANAligner ...")

        # 75% training split (follow the original script)
        # n_train = int(len(X0) * 0.75)

        # X0_train = X0[:n_train]
        # Xk_train = Xk[:n_train]
        # yk_train = yk[:n_train]

        X0_train = X0
        y0_train = y0
        Xk_train = Xk
        yk_train = yk

        # ---- train CycleGAN aligner ----
        self.model, self.decoder, self.dayk_on_day0 = train_cycle_gan_aligner_Merge_Pth_LSTM_Classifier(
            X0_train,
            y0_train,
            Xk_train,
            yk_train,
            self.D_params,
            self.G_params,
            self.training_params,
            self.day0_decoder,
            self.n_lags,
            self.decoder_pth
        )

        print("🎉 Aligner training finished!")
        return self.model, self.decoder, self.dayk_on_day0


    # ---------------------- TRANSFORM ---------------------- #
    def transform(self, Xk):
        """
        Apply trained aligner to day-k spike data.
        """
        if self.model is None:
            raise ValueError("Aligner has not been trained. Call fit() first.")

        print("🔄 Running CycleGANAligner.transform ...")

        # In the original script:
        # dayk_spike_aligned = test_cycle_gan_aligner(aligner, dayk_spike_)
        aligned = test_cycle_gan_aligner(self.model, Xk)

        return aligned
    
    def predict(self, Xk):

        return self.transform(Xk)
    

    # ======================================================
    # ✔ 严格模式 build_model
    # ======================================================
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

        from models.LSTM_Decoder import LSTM_ClassificationDecoder

        decoder = LSTM_ClassificationDecoder(
                input_dim=model_params.get("LSTM_ClassificationDecoder").get("input_dim"),
                num_classes=model_params.get("LSTM_ClassificationDecoder").get("num_classes"),
                # num_classes = output_dim,
                hidden_dim=model_params.get("LSTM_ClassificationDecoder").get("hidden_dim", 64),
                num_layers=model_params.get("LSTM_ClassificationDecoder").get("num_layers", 2),
                lr=model_params.get("LSTM_ClassificationDecoder").get("lr", 1e-3),
                batch_size=model_params.get("LSTM_ClassificationDecoder").get("batch_size", 64),
                epochs=model_params.get("LSTM_ClassificationDecoder").get("epochs", 100),
                device=model_params.get("LSTM_ClassificationDecoder").get("device", "cuda:0")
            )

        model = CycleGANLSTMClassificationAligner(
                model_params.get("D_params"),
                model_params.get("G_params"),
                model_params.get("training_params"),
                decoder,
                n_lags=model_params.get("n_lags", 4),
                decoder_path=model_params.get("decoder_path", ""),
                device=model_params.get("device", "cuda:0")
            )


        # ---------- 构建模型 ----------
        return model
    



class CrossDayDecoderCycleGAN:
    def __init__(self, aligner, decoder):
        self.aligner = aligner
        self.decoder = decoder

    # def fit(self, X0, y0):
    #     print("Training decoder on Day 0...")
    #     self.decoder.fit(X0, y0)

    def fit(self, X0, Xk, yk):
        print("Training aligner on Day k...")
        # self.decoder.fit(X0, y0)
        self.aligner.fit(X0, Xk, yk)

    

    def predict_after_alignment(self, yk):
        # 1) align Xk → aligned
        Xk_aligned = self.aligner.transform(yk)

        # 2) decode using day0 decoder
        # return self.decoder.predict(Xk_aligned)
        return Xk_aligned




if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # -------------------------
    # 1. 生成跨天模拟数据
    # -------------------------
    X0, y0, X1, y1 = generate_cross_day_data(
        n_samples=3000, n_features=20, n_classes=5, drift_strength=2.0
    )

    # -------------------------
    # 2. 创建 Aligner + Decoder
    # -------------------------
    aligner = LinearAligner()
    decoder_model = MLPDecoder(input_dim=20, num_classes=5)
    decoder = DecoderWrapper(decoder_model, lr=1e-3)

    cross_day = CrossDayDecoder(aligner, decoder)

    # -------------------------
    # 3. 训练（只用 Day0 训练分类器）
    # -------------------------
    cross_day.fit(X0, y0, X1)

    # -------------------------
    # 4. Day1 → Day0 对齐后解码
    # -------------------------


    y_pred = cross_day.predict(X1)

    acc = (y_pred == y1).mean()
    print("\n🌟 Cross-day decoding ACC:", acc)


    data = np.load('/media/Disk_BCIJelly/datasets/invasive/Jango_force/Jango_20150730_001.npz', allow_pickle=True)
    day0_spike_ = data['features']  # 2020-02-22.npz
    day0_label_ = data['labels']

    data = np.load('/media/Disk_BCIJelly/datasets/invasive/Jango_force/Jango_20150731_001.npz', allow_pickle=True)
    dayk_spike_ = data['features']  # 2020-02-22.npz
    dayk_label_ = data['labels']


    day0_spike_list = []
    for i in range(len(day0_spike_)):
        day0_spike_list.append(day0_spike_[i])

    day0_label_list = []
    for i in range(len(day0_label_)):
        day0_label_list.append(day0_label_[i])

    
    day0_spike_ = day0_spike_list
    day0_label_ = day0_label_list


    dayk_spike_list = []
    for i in range(len(dayk_spike_)):
        dayk_spike_list.append(dayk_spike_[i])

    dayk_label_list = []
    for i in range(len(dayk_label_)):
        dayk_label_list.append(dayk_label_[i])


    dayk_spike_ = dayk_spike_list
    dayk_label_ = dayk_label_list

    


    #====================== These parameters controls the architecture of the discriminators =============================
    D_params = {}
    D_params['hidden_dim'] = int(day0_spike_[0].shape[1])

    #============================= These parameters controls the architecture of the generators =============================
    G_params = {}
    G_params['hidden_dim'] = int(day0_spike_[0].shape[1])

    #============================= These parameters are for the training process =============================
    training_params = {}
    training_params['loss_type'] = 'L1'
    training_params['optim_type'] = 'Adam'
    training_params['epochs'] = 100
    training_params['batch_size'] = 256
    training_params['D_lr'] = 0.001*10
    training_params['G_lr'] = 0.001
    training_params['ID_loss_p'] = 5
    training_params['cycle_loss_p'] = 5
    training_params['drop_out_D'] = 0.2
    training_params['drop_out_G'] = 0.2
    training_params['n_lags'] = 4
    n_lags = 4




    # decoder = WienerFilterDecoder(n_lags=4, l2=1.0)

    # decoder.fit(day0_spike_[:int(0.75*len(day0_spike_))], day0_label_[:int(0.75*len(day0_label_))] ,day0_spike_[int(0.75*len(day0_spike_)):], day0_label_[int(0.75*len(day0_label_)):] )
    # mr2, r2_channels = decoder.evaluate(day0_spike_[int(0.75*len(day0_spike_)):], day0_label_[int(0.75*len(day0_label_)):])

    # print("Day0 training R2:", mr2)

    # mr2, r2_channels = decoder.evaluate(dayk_spike_[int(0.75*len(dayk_spike_)):], dayk_label_[int(0.75*len(dayk_label_)):])

    # print("Dayk R2 eval on Day0:", mr2)

    
    # day0_decoder = decoder.best_H

    # day0_decoder = decoder



    # # -------------------- Construct aligner -------------------- #
    # aligner = CycleGANAligner(
    #     D_params,
    #     G_params,
    #     training_params,
    #     day0_decoder,
    #     n_lags=4,
    # )

    # # ------------------- Construct decoder -------------------- #
    # # decoder = MLPDecoder(...)   # or CNNDecoder, LSTMDecoder, etc.

    # # ------------------- Construct cross-day system ----------- #
    # cross_decoder = CrossDayDecoderCycleGAN(aligner, decoder)

    # # ------------------- Train Day0 decoder ------------------- #
    # # cross_decoder.fit(day0_label_, day0_label_)

    # # ------------------- Train aligner ------------------------ #
    # # aligner.fit(day0_spike_, dayk_spike_, dayk_label_)

    # cross_decoder.fit(day0_spike_[:int(0.75*len(day0_spike_))], dayk_spike_[:int(0.75*len(dayk_spike_))], dayk_label_[:int(0.75*len(dayk_label_))])

    # # ------------------- Predict on aligned DayK -------------- #
    # y_pred = cross_decoder.predict_after_alignment(dayk_spike_[int(0.75*len(dayk_spike_)):])

    # mr2, r2_channels = decoder.evaluate(y_pred, dayk_label_[int(0.75*len(dayk_label_)):])

    # print("Day0 training R2:", mr2)

    decoder_path = "./day0_decoder_pth.npy"





    decoder = WienerFilterDecoder(n_lags=4, l2=1.0)
        # -------------------- Construct aligner -------------------- #
    aligner = CycleGANAligner(
        D_params,
        G_params,
        training_params,
        decoder,
        n_lags=4,
        decoder_path=decoder_path,
        device=device
    )

    _, decoder_pt, dayk_on_day0 = aligner.fit(day0_spike_, day0_label_ ,dayk_spike_, dayk_label_)

    dayk_aligner = aligner.transform(dayk_spike_[int(0.75*len(dayk_spike_)):])

    # decoder.best_H = decoder_pth

    # mr2, r2_channels = decoder.evaluate(dayk_aligner, dayk_label_[int(0.75*len(dayk_label_)):])

    decoder.save_weights(decoder_path)

    decoder.load_weights(decoder_path)
    mr2 = decoder.evaluate(dayk_aligner, dayk_label_[int(0.75*len(dayk_label_)):])


    # mr2 = r2_score(dayk_label_[int(0.75*len(dayk_label_)):], dayk_aligner, multioutput="variance_weighted")
    
    print("dayk_on_day0:", dayk_on_day0)

    print("dayk_on_day0 Dayk training R2:", mr2)
















