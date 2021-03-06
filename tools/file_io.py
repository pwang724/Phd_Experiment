import json
import os
import pickle
import numpy as np
import copy


def save_pickle(save_path, save_name, data):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_pathname = os.path.join(save_path, save_name + '.pkl')
    with open(save_pathname, "wb") as f:
        pickle.dump(data, f)
        print(save_pathname)

def load_pickle(pickle_path):
    with open(pickle_path, "rb") as f:
        e = pickle.load(f)
    return e

def save_text(save_path, save_name, data):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_pathname = os.path.join(save_path, save_name + '.txt')
    np.savetxt(save_pathname, data, "%.4f")

def load_text(pathname):
    data = np.loadtxt(pathname)
    return data

def save_numpy(save_path, save_name, data):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_pathname = os.path.join(save_path, save_name + '.npy')
    np.save(save_pathname, data)

def load_numpy(pathname):
    data = np.load(pathname)
    return data

def save_json(save_path, save_name, config):
    '''
    TODO: JSON cannot save ndarrays
    :param save_path:
    :param save_name:
    :param config:
    :return:
    '''
    config = copy.copy(config)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_pathname = os.path.join(save_path, save_name + '.json')
    config_dict = config.__dict__
    for k, v in config_dict.items():
        if np.issubdtype(type(v), np.integer):
            config_dict[k] = int(v)
        if isinstance(v, list) or isinstance(v, (np.ndarray)):
            config_dict[k] = ','.join([str(x) for x in v])
    with open(save_pathname, 'w') as f:
        json.dump(config_dict, f)

def load_json(pathname):
    """Load config."""
    with open(pathname, 'r') as f:
        config_dict = json.load(f)
    return config_dict