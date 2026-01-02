from perforatedai import globals_perforatedai as GPA
from perforatedai import modules_perforatedai as PA
from perforatedai import utils_perforatedai as UPA
import torch.nn as nn
import torch
import pdb
import numpy as np
import string
import copy


class PAILayer(nn.Module):
    def __init__(
        self,
        layer_array,
        processor_array,
        dendrites_to_top,
        dendrites_to_dendrites,
        node_index,
        num_cycles,
        view_tuple,
    ):
        super(PAILayer, self).__init__()
        self.layer_array = layer_array
        start = "This module was created by Rorry"
        self.register_buffer("module_id", UPA.string_to_tensor(start)+3)
        self.register_buffer("num_cycles", num_cycles)
        self.register_buffer("view_tuple", torch.tensor(view_tuple))

        start = start[:-5]
        start += "P"
        start += "A"
        start += "I"

        for layer in self.layer_array:
            layer.register_buffer("module_id", UPA.string_to_tensor(start)+3)
        self.processor_array = processor_array
        if dendrites_to_dendrites:
            self.skip_weights = dendrites_to_dendrites
        else:
            """
            This will only be the case if there is less than 2 dendrites, in these cases an empty array
            should still be added so that dendrites_to_top is included at the correct index
            """
            self.skip_weights = nn.ParameterList([torch.zeros(1, 1, 1)])
        if dendrites_to_top:
            self.skip_weights.append(dendrites_to_top[len(dendrites_to_top) - 1])
        else:
            self.skip_weights = nn.ParameterList()

        size = 0
        temp = np.array([])
        for i in range(len(self.skip_weights)):
            for j in range(len(self.skip_weights[i])):
                for k in range(len(self.skip_weights[i][j])):
                    temp = np.append(temp, self.skip_weights[i][j][k].item())
                    if k > size:
                        size = k

        size = size + 1
        if len(temp) != 0:
            mean = temp.mean()
            std = temp.std()

        int_list = [114, 111, 114, 114, 121, 46, 112, 101, 114, 102, 111, 114, 97]
        int_list += [116, 101, 100, 97, 105, 109, 97, 100, 101, 116, 104, 105, 115]
        int_list += [110, 101, 116, 119, 111, 114, 107, 46, 105, 102, 116, 104, 101]
        int_list += [114, 101, 105, 115, 115, 111, 109, 101, 111, 110, 101, 116, 114]
        int_list += [121, 105, 110, 103, 116, 111, 116, 101, 108, 108, 121, 111, 117]
        int_list += [116, 104, 97, 116, 116, 104, 101, 121, 109, 97, 100, 101, 116, 104]
        int_list += [105, 115, 110, 101, 116, 119, 111, 114, 107, 97, 110, 100, 110]
        int_list += [111, 116, 112, 101, 114, 102, 111, 114, 97, 116, 101, 100, 97, 105]
        int_list += [116, 104, 101, 121, 97, 114, 101, 108, 121, 105, 110, 103]

        string_floats = []
        next_float = 0.0
        float_index = 0
        for letter in int_list:
            if letter == " " or letter == ".":
                continue
            next_float += (letter + 1) / pow(10, (float_index + 2) * 2)
            float_index += 1
            if float_index == 2:
                float_index = 0
                string_floats.append(next_float)
                next_float = 0.0
        total_count = 0
        count = len(self.skip_weights)
        new_skip = torch.zeros((count, count, size))
        letter_index = 0
        for i in range(count):
            for j in range(count):
                # if its values fill in the values
                if j < len(self.skip_weights[i]):
                    for k in range(len(self.skip_weights[i][j])):
                        new_skip[i][j][k] = self.skip_weights[i][j][k]
                # if its not values actual values fill with ints
                else:
                    for k in range(size):
                        new_skip[i][j][k] = np.random.normal(mean, std)
                        if letter_index < len(string_floats):
                            # if letter_index == 0:
                            new_skip[i][j][k] = round(new_skip[i][j][k].item(), 2)
                            multiplier = 1
                            if new_skip[i][j][k] < 0:
                                multiplier = -1
                            new_skip[i][j][k] += (
                                string_floats[letter_index] * multiplier
                            )
                            letter_index += 1

        self.original = self.skip_weights
        self.skip_weights = torch.nn.Parameter(new_skip.detach())
        
        # Remove the unused first index (skip_weights[0] is never used in forward pass)
        if self.skip_weights.size(0) > 1:
            self.skip_weights = torch.nn.Parameter(self.skip_weights[1:].contiguous())
        elif self.skip_weights.size(0) == 1:
            # Only one layer, delete skip_weights entirely
            delattr(self, 'skip_weights')

        self.node_index = node_index
        self.internal_nonlinearity = GPA.pc.get_pai_forward_function()

    def forward(self, *args, **kwargs):
        # this should not be getting called, only the other one.
        import pdb

        pdb.set_trace()

        pia_outs = {}
        # For each of the blocks do the processing that must be done to the input and then save the values for the skip connections
        for c in range(0, len(self.layer_array)):
            args2, kwargs2 = args, kwargs
            if self.processor_array[c][0] != None:
                args2, kwargs2 = self.processor_array[c][0].pre(*args2, **kwargs2)
            out_values = self.layer_array[c](*args2, **kwargs2)
            pia_outs[c] = out_values
        # Then add the weighted skip connections to those outputs sequentially while doing any postprocessing that was required.
        for out_index in range(0, len(self.layer_array)):
            current_out = pia_outs[out_index]
            if len(self.layer_array) > 1:
                for in_index in range(0, out_index):
                    current_out += (
                        self.skip_weights[out_index][in_index, :].to(current_out.device)
                        * pia_outs[in_index]
                    )
                if out_index < len(self.layer_array) - 1:
                    current_out = self.internal_nonlinearity(current_out)
            if self.processor_array[c][1] != None:
                pia_outs[out_index] = self.processor_array[out_index][1].post(
                    current_out
                )
            else:
                pia_outs[out_index] = current_out
        return current_out


def unWrap_params(model):
    for p in model.parameters():
        if "wrapped" in p.__dir__():
            del p.wrapped


def convert_to_pai_layer_block(pretrained_dendrite):
    unWrap_params(pretrained_dendrite)
    layer_array = []
    processor_array = []
    for layer_id in range(len(pretrained_dendrite.dendrite_module.layers)):
        layer_array.append(pretrained_dendrite.dendrite_module.layers[layer_id])
        if pretrained_dendrite.dendrite_module.processors == []:
            processor_array.append(None)
        else:
            if not pretrained_dendrite.dendrite_module.processors[layer_id] is None:
                pretrained_dendrite.dendrite_module.processors[layer_id].pre = (
                    pretrained_dendrite.dendrite_module.processors[layer_id].pre_d
                )
                pretrained_dendrite.dendrite_module.processors[layer_id].post = (
                    pretrained_dendrite.dendrite_module.processors[layer_id].post_d
                )
            processor_array.append(
                pretrained_dendrite.dendrite_module.processors[layer_id]
            )
    layer_array.append(pretrained_dendrite.main_module)
    if not pretrained_dendrite.processor is None:
        pretrained_dendrite.processor.pre = pretrained_dendrite.processor.post_n1
        pretrained_dendrite.processor.post = pretrained_dendrite.processor.post_n2
    processor_array.append(pretrained_dendrite.processor)

    view_tuple = []
    for dim in range(
        len(
            pretrained_dendrite.dendrite_module.dendrite_values[0].this_output_dimensions
        )
    ):
        if (
            dim
            == pretrained_dendrite.dendrite_module.dendrite_values[0].this_node_index
        ):
            view_tuple.append(-1)
            continue
        view_tuple.append(1)
    # if this actually doesn't have a dendrites_to_dendrites then fix this
    return PAILayer(
        nn.Sequential(*layer_array),
        processor_array,
        pretrained_dendrite.dendrites_to_top,
        pretrained_dendrite.dendrite_module.dendrites_to_dendrites,
        pretrained_dendrite.this_node_index,
        pretrained_dendrite.dendrite_module.num_cycles,
        view_tuple,
    )


def get_pretrained_pai_attr(pretrained_dendrite, member):
    if pretrained_dendrite is None:
        return None
    else:
        return getattr(pretrained_dendrite, member)


def get_pretrained_pai_var(pretrained_dendrite, submodule_id):
    if pretrained_dendrite is None:
        return None
    else:
        return pretrained_dendrite[submodule_id]


def optimize_module(net, depth, name_so_far, converted_list):
    # print('calling convert on %s: %s, depth %d' % (name_so_far, type(net).__name__, depth))
    all_members = net.__dir__()
    if issubclass(type(net), nn.Sequential) or issubclass(type(net), nn.ModuleList):
        for submodule_id, layer in net.named_children():
            # This is what will be needed to eventually put layer batch back into 2 layers
            # net = nn.Sequential(*[net[i] for i in range(len(net)) if i!=submodule_id])
            if type(net.get_submodule(submodule_id)) is PA.PAINeuronModule:
                if GPA.pc.get_extra_verbose():
                    print(
                        "Seq sub is PAI so optimizing: %s" % name_so_far
                        + "["
                        + str(submodule_id)
                        + "]"
                    )
                setattr(
                    net,
                    submodule_id,
                    convert_to_pai_layer_block(net.get_submodule(submodule_id)),
                )
            else:
                if net != net.get_submodule(submodule_id):
                    # this currently just always returns false, not sure what it was for
                    converted_list += [name_so_far + "[" + str(submodule_id) + "]"]
                    setattr(
                        net,
                        submodule_id,
                        optimize_module(
                            net.get_submodule(submodule_id),
                            depth + 1,
                            name_so_far + "[" + str(submodule_id) + "]",
                            converted_list,
                        ),
                    )
                else:
                    if GPA.pc.get_extra_verbose():
                        print(
                            "%s is a self pointer so skipping"
                            % (name_so_far + "[" + str(submodule_id) + "]")
                        )
    else:
        for member in all_members:
            try:
                getattr(net, member, None)
            except:
                continue
            sub_name = name_so_far + "." + member
            if (
                sub_name in GPA.pc.get_module_names_to_not_save()
                or sub_name in converted_list
            ):
                if GPA.pc.get_extra_verbose():
                    print("Skipping %s during save" % sub_name)
                continue
            if type(getattr(net, member, None)) is PA.PAINeuronModule:
                if GPA.pc.get_extra_verbose():
                    print(
                        "Sub is in conversion list so initiating optimization for: %s"
                        % name_so_far
                        + "."
                        + member
                    )
                setattr(net, member, convert_to_pai_layer_block(getattr(net, member)))
            elif issubclass(type(getattr(net, member, None)), nn.Module):
                if net != getattr(net, member):
                    converted_list += [sub_name]
                    setattr(
                        net,
                        member,
                        optimize_module(
                            getattr(net, member),
                            depth + 1,
                            sub_name,
                            converted_list,
                        ),
                    )
                else:
                    if GPA.pc.get_extra_verbose():
                        print("%s is a self pointer so skipping" % (sub_name))
    return net


# putting pretrainedNormal, pretrained_dendrite as a flag here because might want to replace modules
# pretrained PAI is required instead of just loading in case a system needs to do any specific instantiation stuff
# that PAI conflicts with and then convert network needs to be called after that is setup
def blockwise_network(net):
    return optimize_module(net, 0, "", [])


if __name__ == "__main__":

    import modules_perforatedai as PA
    import utils_perforatedai as UPA

    net = UPA.load_system("sigmoid_linear", "system")

    temp = net.forward(torch.ones(128, 1, 29, 29).to("cuda"))

    net = blockwise_network(net)

    temp2 = net.forward(torch.ones(128, 1, 29, 29).to("cuda"))

    # torch.save(net, 'temp/temp.pt')

    import clean_load as CL

    # net = torch.load('temp/temp.pt')
    net = CL.refresh_net(net)

    temp3 = net.forward(torch.ones(128, 1, 29, 29).to("cuda"))

    print(temp)
    print(temp2)
    print(temp3)

    """
    import modules_perforatedai as PA
    import utils_perforatedai as UPA
    import cleanPAI as BPA
    from transformers.models.wav2vec2.modeling_wav2vec2 import *

    net = UPA.load_system('temp', 'system')    
    net = BPA.blockwise_network(net)
    torch.save(net, 'temp/temp.pt')

    import clean_load as CL
    import torch

    net = torch.load('temp/temp.pt')
    net = CL.refresh_net(net)

    import torch
    net.forward(torch.ones(8,16000).to('cuda'))
    """
    import pdb

    pdb.set_trace()
