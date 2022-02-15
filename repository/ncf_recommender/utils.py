

# Configer converts a dictionary to class:
class configer(object):
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])