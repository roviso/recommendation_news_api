import os
from pathlib import Path


class PathConfig:
    PRE_PKL_PATH: Path = Path(
        Path(__file__).parent,'..','data-processing','processed_data','train_data','pre.pkl'
    ).resolve()

    TRAIN_CSV_PATH: Path = Path(
        Path(__file__).parent,'..','data','train.csv'
    ).resolve()

    MODEL_PATH: Path = Path(
        Path(__file__).parent,'..','trained_models','NCF_checkpoint_cuda.pth.tar'
    ).resolve()

pathconfig = PathConfig()

