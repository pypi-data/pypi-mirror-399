import torch
from example_package_zrh import example

result = example.add_one(5)

print(f"result--------:{result}")

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") ### select either 0 or 1
print(f'Using device: {device}')
# from example_package_zrh.BCI_Hub.models import NER_Decoder
from example_package_zrh.BCI_Hub.models.LSTM_Decoder import LSTM_RegressionDecoder

model = LSTM_RegressionDecoder(input_dim=96, output_dim=2, batch_size=2, device=device)

