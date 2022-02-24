import pickle
def load_pkl(pkl_file):
    with open(pkl_file, 'rb') as inp:
        pickled_obj = pickle.load(inp)
    return pickled_obj

def save_pkl(obj, filename):
    with open(filename, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)
