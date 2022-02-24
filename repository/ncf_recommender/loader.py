## ------------------------------------- PICKLE LOADER ------------------------------------ ##
import torch
import pickle
# from preprocessor import preprocessor

class MyCustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "__main__":
            module = "preprocessor"
        return super().find_class(module, name)

# with open('out.pkl', 'rb') as f:
#     unpickler = MyCustomUnpickler(f)
#     obj = unpickler.load()



def load_pkl(pkl_file):
    with open(pkl_file, 'rb') as inp:
        print('pkl file is being used: ', pkl_file)
        # pickled_obj = pickle.load(inp)
        unpickler = MyCustomUnpickler(inp)
        pickled_obj = unpickler.load()
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