import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
import math
import sys
import numpy as np
import pdb
import os
import time
import warnings
from perforatedai import globals_perforatedai as GPA
from perforatedai import utils_perforatedai as UPA
from perforatedbp import check_license
from perforatedbp import clean_load as CL
from perforatedbp import blockwise_pbp as BPA

import copy

from safetensors.torch import load_file
from safetensors.torch import save_file


## CLOSED ONLY
def check_requires_grad(module):
    for param in module.parameters():
        if param.requires_grad:
            return True
    return False


def debug_print_grad_modules(net, depth, name_so_far):
    print("%s: has req grads: %d" % (name_so_far, check_requires_grad(net)))
    all_members = net.__dir__()
    if issubclass(type(net), nn.Sequential) or issubclass(type(net), nn.ModuleList):
        for submodule_id, layer in net.named_children():
            sub_name = name_so_far + "." + str(submodule_id)
            if net != net.get_submodule(submodule_id):
                debug_print_grad_modules(
                    net.get_submodule(submodule_id), depth + 1, sub_name
                )
    else:
        for member in all_members:
            sub_name = name_so_far + "." + member
            try:
                getattr(net, member, None)
            except:
                continue
            if issubclass(type(getattr(net, member, None)), nn.Module):
                # pdb.set_trace()
                if net != getattr(net, member):
                    debug_print_grad_modules(getattr(net, member), depth + 1, sub_name)


### END CLOSED ONLY


def initialize_pb():
    license_file = "./license.yaml"
    status = check_license.valid_license(license_file)

    if not status:
        print("License Invalid. Quiting...")
        sys.exit(1)


"""
def string_to_tensor(string):
    ords = list(map(ord, string))
    return torch.tensor(ords)
    
def string_from_tensor(string_tensor):
    # Convert tensor to python list.
    ords = string_tensor.tolist()
    # Convert ordinal values to characters and join them into a string.
    return "".join(map(chr, ords))
"""


# add a flag to ignore all warnings
def add_future_warning():
    warnings.filters.insert(0, ("ignore", None, Warning, None, 0))


# delete the warning we just set
def remove_future_warning():
    del warnings.filters[0]


def load_net(net, folder, name):
    save_point = folder + "/"
    if GPA.pc.get_using_safe_tensors():
        if(GPA.pc.get_weight_tying_experimental()):
            return UPA.load_model_with_weight_tying(net, save_point + name + ".pt")
        else:
            state_dict = load_file(save_point + name + ".pt")
    else:
        add_future_warning()
        # Different versions of torch require this change
        try:
            state_dict = torch.load(
                save_point + name + ".pt",
                map_location=torch.device("cpu"),
                weights_only=False,
            ).state_dict()
        except:
            state_dict = torch.load(
                save_point + name + ".pt", map_location=torch.device("cpu")
            ).state_dict()
        remove_future_warning()
    return UPA.load_net_from_dict(net, state_dict)


# This returns a clean version of the network for parameter counting and inference
def clean_net(net):
    net2 = BPA.blockwise_network(net)
    net2 = UPA.deep_copy_pai(net2)
    net2 = CL.refresh_net(net2)
    return net2


def pb_save_net(net, folder, name):
    # if running a DDP only save with first thread
    if "RANK" in os.environ:
        if int(os.environ["RANK"]) != 0:
            return

    # print('calling save: %s' % name)
    # GPA.pai_tracker.archive_layer()
    # These deep copys are required or the real model will also have its layers replaced
    net = UPA.deep_copy_pai(net)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    save_point = folder + "/"
    if not os.path.isdir(save_point):
        os.mkdir(save_point)
    net = BPA.blockwise_network(net)
    net = UPA.deep_copy_pai(net)
    net = CL.refresh_net(net)
    # for _pai versions tracker_string is not needed
    del net.tracker_string
    for param in net.parameters():
        param.data = param.data.contiguous()

    if GPA.pc.get_using_safe_tensors():
        if(GPA.pc.get_weight_tying_experimental()):
            UPA.save_model_with_weight_tying(net, save_point + name + "_pai.pt")
        else:
            save_file(net.state_dict(), save_point + name + "_pai.pt")
    else:
        torch.save(net, save_point + name + "_pai.pt")


def pb_count_params(net):
    if not GPA.pc.get_count_training_params():
        net = UPA.deep_copy_pai(net)
        cleaned = clean_net(net)
        parameters = list(cleaned.named_parameters())
    else:
        parameters = net.named_parameters()
    unique_params = {p.data_ptr(): p for name, p in parameters if 'parent_module' not in name}.values()
    return sum(p.numel() for p in unique_params)
