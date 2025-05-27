from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

import fedscale.cloud.config_parser as parser
from fedscale.dataloaders.femnist import FEMNIST
from fedscale.dataloaders.utils_data import get_data_transform
from fedscale.dataloaders.divide_data import DataPartitioner

# Load transforms
train_transform, test_transform = get_data_transform('mnist')

# Load datasets
train_dataset = FEMNIST('./benchmark/dataset/data/femnist', dataset='train', transform=train_transform)

# Partition the data
parser.args.task = 'cv'
training_sets = DataPartitioner(data=train_dataset, args=parser.args, numOfClass=62)
training_sets.partition_data_helper(num_clients=None, data_map_file='./benchmark/dataset/data/femnist/client_data_mapping/train.csv')

# Explore
print(f'Total number of data samples: {training_sets.getDataLen()}')
print(f'Total number of clients: {training_sets.getClientLen()}')

# Plot distributions
fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
size_dist = training_sets.getSize()['size']
n_bins = 20
axs[0].hist(size_dist, bins=n_bins)
axs[0].set_title('Client data size distribution')

label_dist = training_sets.getClientLabel()
axs[1].hist(label_dist, bins=n_bins)
axs[1].set_title('Client label distribution')

plt.show()
