## ------------------------------------- PICKLE LOADER ------------------------------------ ##
import torch
import pickle

def load_pkl(pkl_file):
    with open(pkl_file, 'rb') as inp:
        pickled_obj = pickle.load(inp)
    return pickled_obj

def save_pkl(obj, filename):
    with open(filename, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)


## ------------------------------------- MODEL CHECKPOINT LOADER ------------------------------------ ##

def save_checkpoint(state, filename):
    print("=> Saving checkpoint")
    torch.save(state, f"../trained_models/{filename}")
    print("=> Done Saving checkpoint")


def load_checkpoint(checkpoint, model, optimizer):
    print("=> Loading checkpoint")
    model.load_state_dict(checkpoint["state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer"])
    print("=> Done Loading checkpoint")