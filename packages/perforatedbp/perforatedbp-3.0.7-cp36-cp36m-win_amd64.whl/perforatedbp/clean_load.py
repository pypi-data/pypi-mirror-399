from perforatedai import globals_perforatedai as GPA

from safetensors.torch import load_file
import copy

import torch.nn as nn
import torch
import pdb


"""
import modules_perforatedai as PA
import utils_perforatedai as UPA
import cleanPAI as CPAI

net = UPA.load_system('sigmoid_linear', 'system') 
net = CPAI.obfusicate_network(net)

import torch
torch.save(net, 'temp/temp.pt')

import clean_load as CL
import torch

net = torch.load('temp/temp.pt')
net = CL.refresh_net(net)

import torch
net.forward(torch.ones(128,1,29,29).to('cuda'))




import modules_perforatedai as PA
import utils_perforatedai as UPA
import cleanPAI as CPAI
from transformers.models.wav2vec2.modeling_wav2vec2 import *

net = UPA.load_system('temp', 'system')    
net = CPAI.obfusicate_network(net)
import torch
torch.save(net, 'temp/temp.pt')

import clean_load as CL
import torch

net = torch.loadB('temp/temp.pt')
net = CL.refresh_net(net)

import torch
net.forward(torch.ones(8,16000).to('cuda'))
"""

# function to convert layers which had to be customized back into their original form. eg Wav2Vec2Projector back to just using a regular projector and not wprojector

# from now on when creating a module to replace, also need to make a backward replacement function to put things back.

from threading import Thread


doing_threading = False
loaded_full_print = False


class PAIModulePyThread(nn.Module):
    def __init__(self, original_module):
        super(PAIModulePyThread, self).__init__()
        self.layer_array = original_module.layer_array
        self.processor_array = original_module.processor_array
        # Remove the unused first index (skip_weights[0] is never used)
        if hasattr(original_module, 'skip_weights') and len(original_module.skip_weights) > 1:
            self.skip_weights = original_module.skip_weights[1:]
        elif hasattr(original_module, 'skip_weights') and len(original_module.skip_weights) == 1:
            # Only one element, don't create skip_weights
            pass
        self.register_buffer("node_index", original_module.node_index.clone().detach())
        self.register_buffer("module_id", original_module.module_id.clone().detach())
        self.register_buffer("num_cycles", original_module.num_cycles)
        self.register_buffer("view_tuple", original_module.view_tuple)

    # this was to hide that modules are wrapped but now thats part of instructions
    """
    def __str__(self):
        if(loaded_full_print):
            total_string = 'PAILayer(\n\t'
            total_string += self.layer_array[-1].__str__().replace('\n','\n\t')
            total_string += '\n)'
        else:
            total_string = 'PAILayer('
            total_string += self.layer_array[-1].__class__.__name__
            total_string += ')'
        return total_string
    def __repr__(self):
        return self.__str__()
    """

    def process_and_forward(self, *args2, **kwargs2):
        c = args2[0]
        dendrite_outs = args2[1]
        args2 = args2[2:]
        if self.processor_array[c] != None:
            args2, kwargs2 = self.processor_array[c].pre(*args2, **kwargs2)
        out_values = self.layer_array[c](*args2, **kwargs2)
        if self.processor_array[c] != None:
            out = self.processor_array[c].post(out_values)
        else:
            out = out_values
        dendrite_outs[c] = out

    def process_and_pre(self, *args, **kwargs):
        dendrite_outs = args[0]
        args = args[1:]
        out = self.layer_array[-1].forward(*args, **kwargs)
        if not self.processor_array[-1] is None:
            out = self.processor_array[-1].pre(out)
        dendrite_outs[len(self.layer_array) - 1] = out

    def forward(self, *args, **kwargs):
        # this is currently false anyway, just remove the doing multi idea
        doing_multi = doing_threading
        dendrite_outs = [None] * len(self.layer_array)
        threads = {}
        for c in range(0, len(self.layer_array) - 1):
            args2, kwargs2 = args, kwargs
            if doing_multi:
                threads[c] = Thread(
                    target=self.process_and_forward,
                    args=(c, dendrite_outs, *args),
                    kwargs=kwargs,
                )
            else:
                self.process_and_forward(c, dendrite_outs, *args2, **kwargs2)
        if doing_multi:
            threads[len(self.layer_array) - 1] = Thread(
                target=self.process_and_pre, args=(dendrite_outs, *args), kwargs=kwargs
            )
        else:
            self.process_and_pre(dendrite_outs, *args, **kwargs)
        if doing_multi:
            for i in range(len(dendrite_outs)):
                threads[i].start()
            for i in range(len(dendrite_outs)):
                threads[i].join()
        for out_index in range(0, len(self.layer_array)):
            current_out = dendrite_outs[out_index]
            if len(self.layer_array) > 1 and hasattr(self, 'skip_weights'):
                for in_index in range(0, out_index):
                    skip_weight = self.skip_weights[out_index - 1][in_index, :]
                    # Use cached Python tuple instead of .tolist() during forward
                    skip_weight = skip_weight.view(self.view_tuple.tolist())
                    current_out = current_out + (
                        skip_weight.to(current_out.device)
                        * dendrite_outs[in_index]
                    )
                if out_index < len(self.layer_array) - 1:
                    current_out = GPA.pc.get_pai_forward_function()(current_out)
            dendrite_outs[out_index] = current_out
        if not self.processor_array[-1] is None:
            current_out = self.processor_array[-1].post(current_out)
        return current_out


def get_pretrained_pai_attr(pretrained_dendrite, member):
    if pretrained_dendrite is None:
        return None
    else:
        return getattr(pretrained_dendrite, member)


def get_pretrained_pai_var(pretrained_dendrite, submodule_id):
    if pretrained_dendrite is None:
        return None
    else:
        return pretrained_dendrite.get_submodule(submodule_id)


"""
This is to set if want to try doing threading or not
"""

ModuleType = PAIModulePyThread
doing_threading = False


def make_module(module):
    # if(ModuleType is PAIModuleJitThread):
    # torch.jit.script(ModuleType(module))
    # else:
    return ModuleType(module)


def refresh_pai(net, depth, name_so_far, converted_list):
    if GPA.pc.get_extra_verbose():
        print("CL calling convert on %s depth %d" % (net, depth))
        print(
            "CL calling convert on %s: %s, depth %d"
            % (name_so_far, type(net).__name__, depth)
        )
    if type(net) is ModuleType:
        if GPA.pc.get_extra_verbose():
            print(
                "this is only being called because something in your model is pointed to twice by two different variables.  Highest thing on the list is one of the duplicates"
            )
        return net
    all_members = net.__dir__()
    if (
        issubclass(type(net), nn.Sequential)
        or issubclass(type(net), nn.ModuleList)
        or issubclass(type(net), list)
    ):
        for submodule_id, layer in net.named_children():
            if net != net.get_submodule(submodule_id):
                converted_list += [name_so_far + "[" + str(submodule_id) + "]"]
                setattr(
                    net,
                    submodule_id,
                    refresh_pai(
                        net.get_submodule(submodule_id),
                        depth + 1,
                        name_so_far + "[" + str(submodule_id) + "]",
                        converted_list,
                    ),
                )
            # else:
            # print('%s is a self pointer so skipping' % (name_so_far + '[' + str(submodule_id) + ']'))
            if type(net.get_submodule(submodule_id)).__name__ == "PAILayer":
                # print('Seq sub is in conversion list so initing PAI for: %s' % name_so_far + '[' + str(submodule_id) + ']')
                setattr(
                    net,
                    submodule_id,
                    make_module(get_pretrained_pai_var(net, submodule_id)),
                )
    elif type(net) in GPA.pc.get_modules_to_track():
        # print('skipping type for returning from call to: %s' % (name_so_far))
        return net
    else:
        for member in all_members:
            try:
                getattr(net, member, None)
            except:
                continue
            sub_name = name_so_far + "." + member

            if member == "device" or member == "dtype":
                continue
            if sub_name in GPA.pc.get_module_names_to_not_save():
                continue
            if name_so_far == "":
                if (
                    sub_name in GPA.pc.get_module_names_to_not_save()
                    or sub_name in converted_list
                ):
                    if GPA.pc.get_extra_verbose():
                        print("Skipping %s during save" % sub_name)
                    continue

            if (
                issubclass(type(getattr(net, member, None)), nn.Module)
                or member == "layer_array"
            ):
                converted_list += [sub_name]
                # pdb.set_trace()
                if net != getattr(net, member):
                    setattr(
                        net,
                        member,
                        refresh_pai(
                            getattr(net, member), depth + 1, sub_name, converted_list
                        ),
                    )
                # else:
                # print('%s is a self pointer so skipping' % (name_so_far + '.' + member))
            if type(getattr(net, member, None)).__name__ == "PAILayer":
                # print('sub is in conversion list so initing PAI for: %s' % name_so_far + '.' + member)
                setattr(net, member, make_module(get_pretrained_pai_attr(net, member)))
    # print('returning from call to: %s' % (name_so_far))
    if type(net).__name__ == "PAILayer":
        net = make_module(net)
    # pdb.set_trace()
    return net


# putting pretrainedNormal, pretrained_dendrite as a flag here becqause might want to replace modules
# pretraiend PAI is required isntead of just loading in case a system needs to do any specific instantiation stuff
# that PAI conflicts with and then convert network needs to be called after that is setup
def refresh_net(pretrained_dendrite):

    net = refresh_pai(pretrained_dendrite, 0, "", [])
    # del net.tracker_string
    return net
