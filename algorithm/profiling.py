import torch
import torch.nn as nn
import time
import argparse
import numpy as np

import torchvision
import torchvision.transforms as transforms

import src.Model

parser = argparse.ArgumentParser(description="Split learning framework")
parser.add_argument('--device', type=str, required=False, help='Device of client')
parser.add_argument('--round', type=int, required=False, help='Profiling round')
parser.add_argument('--batch_size', type=int, required=False, help='Batch size')

args = parser.parse_args()

device = None

if args.device is None:
    if torch.cuda.is_available():
        device = "cuda"
        print(f"Using device: {torch.cuda.get_device_name(device)}")
    else:
        device = "cpu"
        print(f"Using device: CPU")
else:
    device = args.device
    print(f"Using device: {device}")

model = src.Model.VGG16().to(device)
batch_size = 128
test_round = 100
if args.round:
    test_round = args.round

full_model = []
for sub_model in nn.Sequential(*nn.ModuleList(model.children())):
    full_model.append(sub_model)

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

testset = torchvision.datasets.CIFAR10(
    root='./data', train=False, download=False, transform=transform_test)
test_loader = torch.utils.data.DataLoader(
    testset, batch_size=batch_size, shuffle=False, num_workers=2)

data_size = []
forward_time = []

train_data = None

for (data, target) in test_loader:
    data = data.to(device)
    train_data = data
    break

if __name__ == '__main__':
    for i in range(test_round):
        data = train_data
        times = []
        for sub_model in full_model:
            sub_model.train()
            start = time.time_ns()
            data = sub_model(data)
            end = time.time_ns()
            if i == 0:
                data_size.append(data.nelement() * data.element_size())
            times.append(end-start)
        forward_time.append(times)

    forward_time = np.array(forward_time)
    forward_time = np.average(forward_time, axis=0)
    forward_time = forward_time.tolist()

    print(f"List of forward training time = {forward_time} nano second")
    print(f"List of data size = {data_size} bytes")
