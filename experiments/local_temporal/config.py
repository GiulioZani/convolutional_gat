import torch
import torch.nn as nn

# from convolutional_gat.model import TemporalModel, SpatialModel

MODEL_TYPE = "temporal"
PREPROCESSED_FOLDER = "/mnt/kmni_dataset/20_latest"
MAPPING_TYPE = "linear"
DATASET = "kmni"
EPOCHS = 10
TRAIN_BATCH_SIZE = 32
TEST_BATCH_SIZE = 64
LEARNING_RATE = 0.001
LR_STEP = 1
GAMMA = 0.95
PLOT = False
CRITERION = nn.MSELoss()
OPTIMIZER = torch.optim.Adam
DOWNSAMPLE_SIZE = (20, 20)
REDUCE_LR_ON_PLATEAU = True
N_HEADS_PER_LAYER = (1,)
