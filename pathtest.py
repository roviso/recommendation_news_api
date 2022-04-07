from pathlib import Path

PRE_PKL_PATH: Path = Path(
    Path(__file__).parent,'repository','data-processing','processed_data','train_data','pre.pkl'
).resolve()

TRAIN_CSV_PATH: Path = Path(
    Path(__file__).parent,'repository','data','train.csv'
).resolve()

MODEL_PATH: Path = Path(
    Path(__file__).parent,'repository','trained_models','NCF_checkpoint_cuda.pth.tar'
).resolve()


print(f"PRE_PKL_PATH-> {PRE_PKL_PATH}: {PRE_PKL_PATH.is_file()}")

print(f"TRAIN_CSV_PATH-> {TRAIN_CSV_PATH}: {TRAIN_CSV_PATH.is_file()}")
print(f"MODEL_PATH-> {MODEL_PATH}: {MODEL_PATH.is_file()}")