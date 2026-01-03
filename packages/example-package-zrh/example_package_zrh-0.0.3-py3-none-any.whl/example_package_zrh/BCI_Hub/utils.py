from models.NER_Decoder import *
from models.LSTM_Decoder import *
from models.CrossDayDecoder_Merge_Pth import *
from models.KF_Decoder import * 
# from models.Language_Decoder import *
from models.CrossDayDecoder_Merge_Pth import WienerFilterDecoder, CycleGANAligner
# from models.GRUDecoder import *
# from models.Language_Decoder import *

def get_model(Task_name="Single_Day_Cls", 
              model_name="NER", 
              model_params=None):
    """
    根据任务类型、模型名称与参数字典自动获取模型实例
    """

    if model_params is None:
        model_params = {}

    # ========== 分类任务 ==========
    if "Classifier" in Task_name:

        if model_name == "NER":

            # 1. 创建模型（带默认参数）
            model = NER_ClassificationDecoder(
                iterations=model_params.get("iterations", 5000),
                output_dimension=model_params.get("output_dimension", 8),
                batch_size=model_params.get("batch_size", 512),
                device=model_params.get("device", "cuda:0")
            )

        elif model_name == "LSTM":

            model = LSTM_ClassificationDecoder(
                input_dim=model_params.get("input_dim"),
                num_classes=model_params.get("num_classes"),
                hidden_dim=model_params.get("hidden_dim", 64),
                num_layers=model_params.get("num_layers", 2),
                lr=model_params.get("lr", 1e-3),
                batch_size=model_params.get("batch_size", 64),
                epochs=model_params.get("epochs", 100),
                device=model_params.get("device", "cuda:0")
            )

        else:
            raise ValueError(f"未知分类模型: {model_name}")


    # ========== 回归任务 ==========
    elif "Reg" in Task_name:

        if model_name == "NER":
            model = NER_RegressionDecoder(
                iterations=model_params.get("iterations", 5000),
                output_dimension=model_params.get("output_dimension", 8),
                batch_size=model_params.get("batch_size", 512),
                device=model_params.get("device", "cuda:0")
            )

        elif model_name == "LSTM":
            model = LSTM_RegressionDecoder(
                input_dim=model_params.get("input_dim"),
                output_dim=model_params.get("output_dim"),
                hidden_dim=model_params.get("hidden_dim", 64),
                num_layers=model_params.get("num_layers", 2),
                lr=model_params.get("lr", 1e-3),
                batch_size=model_params.get("batch_size", 64),
                epochs=model_params.get("epochs", 100),
                device=model_params.get("device", "cuda:0")
            )

        elif model_name == "CycleGAN":
            decoder = WienerFilterDecoder(n_lags=4, l2=1.0)


            model = CycleGANAligner(
                    model_params["D_params"],
                    model_params["G_params"],
                    model_params["training_params"],
                    decoder,
                    n_lags=4,
                    decoder_path=model_params.get("decoder_path"),
                    device=model_params.get("device", "cuda:0")
                )
            
            # model = CycleGANAligner(
            #         model_params,
            #         model_params,
            #         model_params,
            #         decoder,
            #         n_lags=4,
            #         decoder_path=model_params.get("decoder_path"),
            #         device=model_params.get("device", "cuda:0")
            #     )

        elif model_name == "KF":
            model = KalmanFilterDecoder(model_params.get("C", 1))
            

        else:
            raise ValueError(f"未知回归模型: {model_name}")

    else:
        raise ValueError(f"未知 Task_name: {Task_name}")

    # ======================================================
    # 🔥 自动更新模型参数（如果 decoder 内部支持 update_params）
    # ======================================================
    if hasattr(model, "update_params"):
        model.update_params(model_params)

    return model



def build_model(Task_name="Single_Day_Cls", 
              model_name="NER", 
              model_params=None):
    """
    根据任务类型、模型名称与参数字典自动获取模型实例
    """

    if model_params is None:
        model_params = {}

    # ========== 分类任务 ==========
    if "Classifier" in Task_name:

        if model_name == "NER":

            # 1. 创建模型（带默认参数）
            model = NER_ClassificationDecoder(
                iterations=model_params.get("iterations", 5000),
                output_dimension=model_params.get("output_dimension", 8),
                batch_size=model_params.get("batch_size", 512),
                device=model_params.get("device", "cuda:0")
            )

        elif model_name == "LSTM":

            model = LSTM_ClassificationDecoder(
                input_dim=model_params.get("input_dim"),
                num_classes=model_params.get("num_classes"),
                hidden_dim=model_params.get("hidden_dim", 64),
                num_layers=model_params.get("num_layers", 2),
                lr=model_params.get("lr", 1e-3),
                batch_size=model_params.get("batch_size", 64),
                epochs=model_params.get("epochs", 100),
                device=model_params.get("device", "cuda:0")
            )

        else:
            raise ValueError(f"未知分类模型: {model_name}")


    # ========== 回归任务 ==========
    elif "Reg" in Task_name:

        if model_name == "NER_RegressionDecoder":
            model = NER_RegressionDecoder(
                iterations=model_params.get("iterations", 5000),
                output_dimension=model_params.get("output_dimension", 8),
                batch_size=model_params.get("batch_size", 512),
                device=model_params.get("device", "cuda:0")
            )

        elif model_name == "LSTM_RegressionDecoder":
            model = LSTM_RegressionDecoder(
                input_dim=model_params.get("input_dim"),
                output_dim=model_params.get("output_dim"),
                hidden_dim=model_params.get("hidden_dim", 64),
                num_layers=model_params.get("num_layers", 2),
                lr=model_params.get("lr", 1e-3),
                batch_size=model_params.get("batch_size", 64),
                epochs=model_params.get("epochs", 100),
                device=model_params.get("device", "cuda:0")
            )

        elif model_name == "CycleGAN":
            decoder = WienerFilterDecoder(n_lags=model_params.get("n_lags", 4), l2=model_params.get("l2", 1.0))
            # decoder = WienerFilterDecoder(n_lags=4, l2=1.0)
            model = CycleGANAligner(
                    model_params.get("D_params"),
                    model_params.get("G_params"),
                    model_params.get("training_params"),
                    decoder,
                    n_lags=model_params.get("n_lags", 4),
                    decoder_path=model_params.get("decoder_path", ""),
                    device=model_params.get("device", "cuda:0")
                )

        elif model_name == "KalmanFilterDecoder":
            model = KalmanFilterDecoder(model_params.get("C", 1))
            

        else:
            raise ValueError(f"未知回归模型: {model_name}")

    else:
        raise ValueError(f"未知 Task_name: {Task_name}")

    # ======================================================
    # 🔥 自动更新模型参数（如果 decoder 内部支持 update_params）
    # ======================================================
    if hasattr(model, "update_params"):
        model.update_params(model_params)

    return model


def build_model_language(
              model_name, args, 
              model_params=None):
    """
    根据任务类型、模型名称与参数字典自动获取模型实例
    """

    if model_params is None:
        model_params = {}



    if model_name == "Language_GRUDecoder":

        # 1. 创建模型（带默认参数）
        model = DecoderGRUModel_args(
            args=args,
            model_params=model_params
        )

    elif model_name == "Language_LSTMDecoder":

        model = DecoderLSTMModel_args(
            args=args,
            model_params=model_params
        )

    elif model_name == "Language_LSTMGRUDecoder":

        model = DecoderLSTMGRUModel_args(
            args=args,
            model_params=model_params
        )

    elif model_name == "Language_CNNDecoder":

        model = DecoderCNNModel_args(
            args=args,
            model_params=model_params
        )

    else:
        raise ValueError(f"未知分类模型: {model_name}")



    # ======================================================
    # 🔥 自动更新模型参数（如果 decoder 内部支持 update_params）
    # ======================================================
    if hasattr(model, "update_params"):
        model.update_params(model_params)

    return model
