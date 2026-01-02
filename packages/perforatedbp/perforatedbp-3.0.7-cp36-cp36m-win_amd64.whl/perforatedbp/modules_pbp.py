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
from itertools import chain

from datetime import datetime
from perforatedai import globals_perforatedai as GPA
from perforatedai import modules_perforatedai as MPA
from perforatedbp import check_license
import copy
import random
import traceback


# This is the list of values that get added to each dendrite module for each dendrite
def update_dendrite_tensor_values(DENDRITE_TENSOR_VALUES):
    return DENDRITE_TENSOR_VALUES + [
        "prev_dendrite_candidate_correlation",
        "covariance_for_parallel",
        "best_score",
        "previous_best_score",
        "prev_dendrite_candidate_average",
        "main_grad_average_for_scaling",
        "candidate_grad_average_for_scaling",
        "indexes_of_best",
        "nodes_best_improved_this_epoch",
        "parents_average_d_vector",
        "normal_pass_average_d",
    ]


# Same as above but these are single value tensors
def update_dendrite_single_values(DENDRITE_SINGLE_VALUES):
    return DENDRITE_SINGLE_VALUES + [
        "breaking",
        "locked",
        "best_score_improved_this_time_step",
        "best_score_improved_this_epoch",
        "running_scalar",
    ]


# These are included above, they just get skipped for reinit if not live
NON_LIVE_SKIP_VALUES = [
    "normal_pass_average_d",
]


if GPA.pc.get_doing_thing():
    DENDRITE_SINGLE_VALUES = GPA.DENDRITE_SINGLE_VALUES + [
        "normal_pass_max_mean_act",
        "parent_max_mean_act",
    ]
    NON_LIVE_SKIP_VALUES = NON_LIVE_SKIP_VALUES + ["normal_pass_max_mean_act"]


def update_value_tracker_arrays(VALUE_TRACKER_ARRAYS):
    return VALUE_TRACKER_ARRAYS + ["current_parent_d"]


def get_tuples_and_mult(val, values):
    """
    This function uses this_node_index to create returned values
        math_tuple - tuple of dimensions to do math over
        view_tuple - tuple of dimensions to view with -1 at this_node_index
        full_mult - product of all dimensions except this_node_index
    """
    math_tuple = []
    view_tuple = []
    full_mult = 1
    for i in range(len(val.size())):
        if i == values.this_node_index:
            view_tuple.append(-1)
            continue
        full_mult *= val.shape[i]
        math_tuple.append(i)
        view_tuple.append(1)
    return math_tuple, view_tuple, full_mult


def filter_backward_pb(val, values):
    # TODO: move torch.no_grad to modules_perforatedai
    with torch.no_grad():
        math_tuple, view_tuple, full_mult = get_tuples_and_mult(val, values[0])
        if GPA.pai_tracker.member_vars["mode"] == "p":
            for i in range(0, GPA.pc.get_global_candidates()):
                # this is where the grad_in is actually set for the tagger
                if val.device.type == "cpu":
                    device_index = 0
                else:
                    device_index = val.device.index
                if (
                    GPA.pc.get_debugging_memory_leak()
                    and len(values[i].current_parent_d[device_index]) != 0
                ):
                    print(
                        "%s called backward but didn't clear the previous error.\n"
                        "This can cause a memory leak.\n"
                        "If it is, make sure you are calling optimizer.step() and zero_grad() each iteration.\n"
                        "You may need to reduce the total batches in gradient accumulation if this is intentional.\n"
                        % values[i].layer_name
                    )
                    a = len(values[i].dendrite_outs[0])
                    b = len(values[i].current_parent_d[0])
                    print(
                        "Dendrite outs and neuron errors are currently stacked (%d/%d) times"
                        % (a, b)
                    )

                # For now dendrite_learn_mode just means doing Cascor.
                if GPA.pc.get_dendrite_learn_mode():
                    if GPA.pc.get_extra_verbose():
                        print("%s appending parent d" % values[i].layer_name)
                    # This line will set current_parent_d to be the current error - the average error
                    values[i].current_parent_d[device_index].append(val.detach())
                    values[i].device = device_index
    if GPA.pc.get_extra_verbose():
        print("%s completing backward" % values[0].layer_name)


"""
def set_grad_params(model, to_set):
    "" "Set requires_grad for all parameters in a model"" "
    for p in model.parameters():
        if not p.dtype is torch.uint8:
            p.requires_grad = True  # to_set
"""


def set_module_n_pb(neuron_module):
    return

    """Set the module to n mode - this means the main module learns and the dendrites do not"""
    """
    set_grad_params(neuron_module.main_module, True)
    # pb to top [x] is a nodes_x_dendrite_module array, dont need to loop since older ones arent used
    if neuron_module.dendrite_modules_added > 0:
        neuron_module.dendrites_to_top[
            neuron_module.dendrite_modules_added - 1
        ].requires_grad = True
    for param in neuron_module.dendrite_module.dendrites_to_dendrites:
        # TODO: after checking that exact values passes this should be GPA.pc.get_dendrite_update_mode()
        param.requires_grad = False
    """


def set_module_p_pb(neuron_module):
    """Set the module to p mode - this means the dendrites learn and the main module does not"""
    if GPA.pc.get_learn_dendrites_live():
        # If learning live the candidates need to also connect to top so add them here
        neuron_module.candidate_to_top = nn.Parameter(
            torch.zeros(
                (1, neuron_module.out_channels),
                device=GPA.pc.get_device(),
                dtype=GPA.pc.get_d_type(),
            )
            .detach()
            .clone(),
            requires_grad=True,
        )
        neuron_module.register_parameter(
            "current_candidate_to_top", neuron_module.candidate_to_top
        )
        """
        set_grad_params(neuron_module.main_module, True)
        # pb to top [x] is a nodes_x_dendrite_module array, no loop required since
        if neuron_module.dendrite_modules_added > 0:
            neuron_module.dendrites_to_top[
                neuron_module.dendrite_modules_added - 1
            ].requires_grad = True
            for param in neuron_module.dendrite_module.dendrites_to_dendrites:
                param.requires_grad = True

    # Set all parameters in established network to no longer learn
    else:
        set_grad_params(neuron_module.main_module, False)
        if neuron_module.dendrite_modules_added > 0:
            neuron_module.dendrites_to_top[
                neuron_module.dendrite_modules_added - 1
            ].requires_grad = False
            for param in neuron_module.dendrite_module.dendrites_to_dendrites:
                param.requires_grad = False
        """


def load_tagger_values(neuron_module):
    neuron_module.dendrite_module.load_tagger_values()


def set_parameters(module, parameter_type):
    """
    Initialize parameters PB by setting parameter_type for all parameters
    """
    for name, param in module.named_parameters():
        param.parameter_type = parameter_type


def set_neuron_parameters(module):
    """
    Neuron parameters train during n mode
    """
    set_parameters(module, "neuron")


def set_dendrite_parameters(module):
    """
    dendrite parameters train during n mode if learn_dendrites_live is true
    """
    set_parameters(module, "dendrite")


def set_candidate_parameters(module):
    """
    candidate parameters train during p mode
    """
    set_parameters(module, "candidate")


def set_ignored_parameters(module):
    """
    ignored parameters never train
    """
    set_parameters(module, "ignored")


def covariance_loss(current_cov, error, average_error, output):
    return output * current_cov.sign() * (error - average_error)


def update_running_averages(
    new_neuron_error, dendrite_outs, loss, values, math_tuple, full_mult, covariance
):
    try:
        # update the running average with the current error
        with torch.no_grad():
            values.normal_pass_average_d.copy_(
                (values.normal_pass_average_d * 0.99)
                + ((new_neuron_error.detach().sum(math_tuple) * 0.01) / full_mult)
            )
        if GPA.pc.get_dpp_verbose():
            print("no error with")
            print(new_neuron_error.shape)
            print(values.this_node_index)
            print(math_tuple)
            print(full_mult)
    except Exception as e:
        print(e)
        print("Error with type shape in %s" % values.layer_name)
        print(new_neuron_error.shape)
        print(values.this_node_index)
        print(math_tuple)
        print(full_mult)
        import pdb

        pdb.set_trace()
        sys.exit(0)
    # Should get rid of the below comments (and others here) after CC is verified

    # values[0].normal_pass_average_d_mags *= 0.99
    # values[0].normal_pass_average_d_mags += (val.abs().sum(math_tuple) * 0.01) / full_mult
    # values[0].normal_pass_average_d_std = values[0].normal_pass_average_d_std * 0.99 + val.std((math_tuple))*0.01

    # this is **2 after everything because it is a scalar to scale the final grad_in.  The final gradient that actually gets applied is gradient.sum(math_tuple)
    # final weight adjustment/actual grad value is net.module.main_module[0].PAINeuronModule.current_d.sum(math_tuple)
    # You can tell this by looking at the bias values in grad.  It will be similar for the convolution kernel weight values in grad
    """
    values[0].normal_pass_average_d_sq *= 0.99
    if(GPA.pc.get_grad_sum_first()):
        values[0].normal_pass_average_d_sq += ((val)**2).sum(math_tuple) * 0.01# / full_mult #if changing here change previous in data parallel
    else:
        values[0].normal_pass_average_d_sq += ((val)).sum(math_tuple)**2 * 0.01# / full_mult
    """

    # if trying to do cascor with dendrites while also updating neurons
    # the parents average d needs to be a running average as well isntead of a final average
    # TODO: if not doing this, perhaps we could save compute costs by not doing all this summing and averaging
    # during the 100 training iterations, and isntead just do it once in between N and P switches
    """
    This is currently not operational in this version of the code.  Need to add a part where the candidate output is clone.detached and thena dded
    to the neuron as if it was just a normal input that can be learned.
    there is also currently a memory leak that is happening with it.
    """

    if GPA.pc.get_learn_dendrites_live():

        # Keep these values updated on the fly  if this works, might only need to do mean, above and will stay the same and be faster.
        # Use copy_ instead of .data = to avoid potential autograd issues
        with torch.no_grad():
            new_value = values.normal_pass_average_d.detach().clone() / (full_mult)
            values.parents_average_d_vector.copy_(new_value)
            values.parents_average_d_vector.requires_grad = False
    if values.initialized.item() < GPA.pc.get_initial_correlation_batches():
        update_saved_values_averages_initial(
            values,
            dendrite_outs,
            covariance,
            loss,
            new_neuron_error,
            math_tuple,
        )
    else:
        update_saved_values_averages(
            values,
            dendrite_outs,
            covariance,
            loss,
            new_neuron_error,
            math_tuple,
        )

    if GPA.pc.get_extra_verbose() and False:
        print_correlation_values(
            values, dendrite_outs, covariance, loss, new_neuron_error
        )


def print_correlation_values(values, dendrite_outs, covariance, loss, new_neuron_error):
    print("Correlation Values:")
    print("Last Dendrite Outs:", dendrite_outs)
    print("New Neuron Error:", new_neuron_error)
    print("Current Correlations:", covariance)
    print("Loss:", loss)
    print("Initialized:", values.initialized)
    if (
        (dendrite_outs).isnan().any()
        or (covariance).isnan().any()
        or (loss).isnan().any()
        or (new_neuron_error).isnan().any()
    ):
        print("got a nan in correlation function")
        import pdb

        pdb.set_trace()


def update_saved_values_averages_initial(
    saved_values, dendrite_outs, covariance, loss, last_parent_d, math_tuple
):
    # for the first x iterations average out the initial conditions a little bit
    # at the beginning have it equal the actual average, not the abs average
    # this is because the best is the abs of running best
    # but running best is average of a bunch of positives and negatives
    # so to just initialize as a single value it it a high positive or negative
    with torch.no_grad():
        # Use .copy_() to avoid creating new tensors that might interfere with autograd
        saved_values.candidate_grad_average_for_scaling.copy_(
            (
                saved_values.candidate_grad_average_for_scaling
                * saved_values.initialized
                + loss.detach().clone().sum(math_tuple)
            )
            / (saved_values.initialized + 1.0)
        )

        saved_values.main_grad_average_for_scaling.copy_(
            (
                saved_values.main_grad_average_for_scaling * saved_values.initialized
                + last_parent_d.detach().clone().sum(math_tuple)
            )
            / (saved_values.initialized + 1.0)
        )

        saved_values.prev_dendrite_candidate_average.copy_(
            (
                saved_values.prev_dendrite_candidate_average * saved_values.initialized
                + dendrite_outs.detach().clone().mean(math_tuple)
            )
            / (saved_values.initialized + 1.0)
        )
        saved_values.prev_dendrite_candidate_correlation.copy_(
            (
                saved_values.prev_dendrite_candidate_correlation
                * saved_values.initialized
                + covariance.detach().clone()
            )
            / (saved_values.initialized + 1.0)
        )
        # If not initialized yet, maintain best scores as 0
        saved_values.best_score.copy_(saved_values.best_score.detach() * 0)
        saved_values.previous_best_score.copy_(
            saved_values.previous_best_score.detach() * 0
        )

        saved_values.running_scalar.fill_(1.0)

        saved_values.initialized.copy_(saved_values.initialized.detach() + 1.0)


def update_saved_values_averages(
    saved_values, dendrite_outs, covariance, loss, last_parent_d, math_tuple
):
    # for the first x iterations average out the initial conditions a little bit
    # at the beginning have it equal the actual average, not the abs average
    # this is because the best is the abs of running best
    # but running best is average of a bunch of positives and negatives
    # so to just initialize as a single value it it a high positive or negative
    factor = 0.99
    with torch.no_grad():
        # Use .copy_() to avoid creating new tensors that might interfere with autograd
        saved_values.candidate_grad_average_for_scaling.copy_(
            factor * saved_values.candidate_grad_average_for_scaling.detach().clone()
            + (loss.detach().clone().sum(math_tuple) * (1.0 - factor))
        )

        saved_values.main_grad_average_for_scaling.copy_(
            factor * saved_values.main_grad_average_for_scaling.detach().clone()
            + (last_parent_d.detach().clone().sum(math_tuple) * (1.0 - factor))
        )
        saved_values.prev_dendrite_candidate_average.copy_(
            factor * saved_values.prev_dendrite_candidate_average.detach().clone()
            + (dendrite_outs.detach().clone().mean(math_tuple) * (1.0 - factor))
        )
        """
        saved_values.prev_dendrite_candidate_correlation.copy_(
            factor * saved_values.prev_dendrite_candidate_correlation.detach().clone()
            + (covariance.detach().clone() * (1.0 - factor))
        )
        """
        new_correlation = (
            factor * saved_values.prev_dendrite_candidate_correlation.detach().clone()
            + covariance.detach().clone() * (1.0 - factor)
        ).clone()

        # Reassign outside of any computation graph
        saved_values.prev_dendrite_candidate_correlation.data = new_correlation.data


def check_new_best_score(saved_values):
    new_best_score, best_indices = new_best(saved_values)
    saved_values.best_score.copy_(new_best_score)

    beat_best = dendrite_score_beats_current_best(
        saved_values.best_score, saved_values.previous_best_score
    )
    # If that best score has improved enough or this is the very first iteration
    if (beat_best) or saved_values.initialized.item() == 0:

        if saved_values.best_score_improved_this_epoch[0] == 0 and GPA.pc.get_verbose():
            print(
                "Score from %.16f to %.16f for %s with initialized %d"
                % (
                    saved_values.previous_best_score.mean(),
                    saved_values.best_score.mean(),
                    saved_values.layer_name,
                    saved_values.initialized.item(),
                )
            )
        # say that best score did improve this epoch and time step
        saved_values.best_score_improved_this_epoch[0].copy_(torch.tensor(1))
        saved_values.best_score_improved_this_time_step[0].copy_(torch.tensor(1))
        # set the indexes of the best nodes
        saved_values.indexes_of_best.copy_(best_indices)

        ##check where temp_abs = best_score and save the weights for those candidates in forward for the layer next iteration
        # this is where that saveBest function was maybe called?
        # [values, indexes] = torch.max(saved_values.indexes_of_best, 0)
        # TODO: this is supposed to be setting flags for which node indexes improved their max correlations
        # But I'm not sure thats still whats happening 9.25.2025
        saved_values.nodes_best_improved_this_epoch += saved_values.indexes_of_best
        # only replace the ones that are bigger
        saved_values.previous_best_score.copy_(
            torch.max(
                saved_values.best_score,
                saved_values.previous_best_score,
            ).detach()
        )
    else:
        # If dendrites did not improve their scores set that flag
        saved_values.best_score_improved_this_time_step[0].copy_(torch.tensor(0))
        saved_values.indexes_of_best.copy_(saved_values.indexes_of_best * 0)


def apply_pb_grads(self):

    values = self.dendrite_values[0]
    # This will only happen if optimizer.step is called before a forward and backward
    # For some reason PyTorch Lightning does this
    if GPA.pc.get_extra_verbose():
        print("calling apply pb grads for %s" % values.layer_name)
        print('with %d/%d tensors'%(len(values.current_parent_d[values.device]), len(values.dendrite_outs[values.device])))
    if getattr(values, "device", None) is None:
        return
    if GPA.pc.get_extra_verbose():
        print("And cleared device")
    # loop over it here.  If this actually is whats causing better scores see if theres a way to do also do this during n mode.
    # loop over all outs and d's.  this will only be one if non a recurrent layer.
    while (len(values.current_parent_d[values.device]) > 0) and (
        len(values.dendrite_outs[values.device]) > 0
    ):
        # Get loss and capture data needed for running averages update
        loss, update_data = get_cc_loss(self.dendrite_values[0])
        """
        TODO: look into how to make a valuable scalar again.  Setting max of 100 was doing nan,
        and 10 was actually making results worse.  Maybe just not needed with this new version?
        scalar = (
            values.main_grad_average_for_scaling.abs().mean()
            / values.candidate_grad_average_for_scaling.abs().mean()
        )
        if scalar.isnan() or scalar.isinf():
            scalar = 0.0
        if scalar > GPA.pc.get_max_scalar_multiplier():
            scalar = GPA.pc.get_max_scalar_multiplier()

        factor = 0.99
        # Update running scalar (this is safe since it's a scalar, not a tensor in the computational graph)
        values.running_scalar = values.running_scalar * factor + scalar * (1.0 - factor)
        loss = loss * values.running_scalar
        """
        loss.backward()
        (
            new_neuron_error,
            dendrite_outs,
            loss,
            values,
            math_tuple,
            full_mult,
            view_tuple,
        ) = update_data

        # After loss.backward(), before optimizer.step()
        with torch.no_grad():
            if GPA.pc.get_correlations_by_mean():
                func = torch.mean
            else:
                func = torch.sum

            dendrite_outs_clean = dendrite_outs.detach().clone()
            parent_d_clean = new_neuron_error.detach().clone()

            # Compute averages from clean tensors
            average_parent_d = parent_d_clean.mean(math_tuple)
            average_dendrite_outs = dendrite_outs_clean.mean(math_tuple)

            # Compute covariance from clean tensors
            centered_dendrites = dendrite_outs_clean - average_dendrite_outs.view(
                view_tuple
            )
            centered_parent = parent_d_clean - average_parent_d.view(view_tuple)
            covariance = func((centered_dendrites * centered_parent).abs(), math_tuple)

            # maybe next try getting rid of dendrite outs here?
            # nuclear option to be absolutely certain covariance is not in the graph

            covariance = covariance.detach().clone()

            if covariance.isnan().any() or covariance.isinf().any():
                print("Covariance contains NaN values.")
                print("For layer: %s" % values.layer_name)
                print(
                    "Try not adding dendrites here with GPA.pc.append_module_ids_to_track(['"
                    + values.layer_name
                    + "'])"
                )
                import pdb

                pdb.set_trace()

        # Now safe to update running averages after backward pass
        with torch.no_grad():
            update_running_averages(
                new_neuron_error,
                dendrite_outs,
                loss,
                values,
                math_tuple,
                full_mult,
                covariance,
            )
        # Clear out the current parent_d and dendrite_outs
        if GPA.pc.get_extra_verbose():
            print("%s applied grads and clearing first tensor" % values.layer_name)
            print("with %d tensors" % len(values.current_parent_d[values.device]))
        del values.current_parent_d[values.device][0]
        del values.dendrite_outs[values.device][0]


def get_cc_loss(dendrite_values):
    # Check license every 0.000001% of the time, this should also have been checked in convert network
    if random.random() < 0.000001:
        license_file = "./license.yaml"
        status = check_license.valid_license(license_file)
        if not status:
            print("License Invalid. Quiting...")
            sys.exit(1)
    values = dendrite_values
    device_index = values.device
    with torch.no_grad():
        check_dendrite_outs(values, device_index)
        # current neuron errors
        parent_d = values.current_parent_d[device_index][0].detach().clone()
        # Candidate outputs
        dendrite_outs = values.dendrite_outs[device_index][0]

        math_tuple, view_tuple, full_mult = get_tuples_and_mult(parent_d, values)

        # Get average for neurons just within a batch
        average_parent_d = parent_d.detach().clone().mean(math_tuple)
        # Get average of candidates just within a batch
        average_dendrite_outs = dendrite_outs.detach().clone().mean(math_tuple)
        """
        if we want to keep a cumulative average then it should be done here and in update_running_averages
        instead of just doing average over current batch
        if GPA.pc.get_learn_dendrites_live():
        values[0].parents_average_d_vector.copy_(
                values[0].normal_pass_average_d.detach().clone() / (full_mult)
            )
        """

    # calculate the covariance loss and backpropagate it.
    # Dendrite out here is already after the sigmoid has been applied
    loss = covariance_loss(
        values.prev_dendrite_candidate_correlation.view(view_tuple),
        parent_d,
        average_parent_d.view(view_tuple),
        dendrite_outs,
    )

    # Capture data for running averages update (to be done after backward pass)
    # Create completely detached copies to avoid autograd conflicts
    with torch.no_grad():
        update_data = (
            parent_d.detach().clone(),
            dendrite_outs.detach().clone(),
            loss.detach().clone(),
            dendrite_values,
            math_tuple,
            full_mult,
            view_tuple,
        )

        # Check if there is a new best correlation score
        check_new_best_score(dendrite_values)
    # loss has to be a single number for backward, so sum across the batch
    loss = loss.sum()
    # print("Loss:", loss)  # Debugging line
    return loss, update_data


def apply_pb_zero(self):
    values = self.dendrite_values[0]
    # If device is not set yet than nothing to clear because this is before an actual step
    if getattr(values, "device", None) is None:
        return
    if GPA.pc.get_extra_verbose():
        print("clearing out values in zero_grad")
    cleared = ""
    """
    If current parent d has values here it means backwards was called
    but optimizer.step was not called.  If zeroing then everything
    about the previous step should be cleared
    """
    if len(values.current_parent_d[values.device]) > 0:
        """
        If they're the same length then zero is being called before forward
        so clear both of them.
        """
        if len(values.current_parent_d[values.device]) == len(
            values.dendrite_outs[values.device]
        ):
            # Clear out the current parent_d and dendrite_outs
            if len(values.current_parent_d[values.device]) > 0:
                cleared += "1" * len(values.current_parent_d[values.device])
                values.current_parent_d[values.device].clear()  # Clear the entire list

            if len(values.dendrite_outs[values.device]) > 0:
                cleared += "2" * len(values.dendrite_outs[values.device])
                values.dendrite_outs[values.device].clear()  # Clear the entire list
        """
        If they are different lengths than zero is being called after forward
        so retain the most recent dendrite_outs value
        """
        if len(values.current_parent_d[values.device]) < len(
            values.dendrite_outs[values.device]
        ):
            cleared += "1" * len(values.current_parent_d[values.device])
            values.current_parent_d[values.device].clear()  # Clear the entire list
            cleared += "2" * (len(values.dendrite_outs[values.device]) - 1)
            first_item = values.dendrite_outs[values.device][-1]
            values.dendrite_outs[values.device].clear()
            values.dendrite_outs[values.device].append(first_item)
            if GPA.pc.get_verbose():
                print("%s retaining::dendrite_outs" % (values.layer_name))
    if GPA.pc.get_verbose():
        print("%s cleared:: %s" % (values.layer_name, cleared))
        a = len(values.dendrite_outs[values.device])
        b = len(values.current_parent_d[values.device])
        print('lens are now: %d/%d' % (a,b))



def create_extra_tensors(dendrite_module):
    """
    for DendriteModules this creates the extra tensors needed for Cascor
    """
    # Saved tensors for recurrent modules
    dendrite_module.current_recurrent_pass_tensors = []
    dendrite_module.current_recurrent_pass_candidate_tensors = []
    # PAI VALUES
    dendrite_module.normal_learning_taggers = {}

    dendrite_module.random_pai_to_candidates = (
        GPA.pc.get_default_random_pai_to_candidates()
    )


def init_candidates(dendrite_module, j):
    license_file = "./license.yaml"
    status = check_license.valid_license(license_file)
    if not status:
        print("License Invalid. Quiting...")
        sys.exit(1)
    """
    Randomizes the candidates to dendrites weights
    TODO: Should this also include the same dendrite multiplier?
    """
    dendrite_module.dendrites_to_candidates[j].data.pai_wrapped = True
    if dendrite_module.random_pai_to_candidates:
        with torch.no_grad():
            dendrite_module.dendrites_to_candidates[j].normal_(
                0, math.sqrt(2.0 / dendrite_module.out_channels)
            )
    # dendrite_module.register_parameter(('dendrites_to_candidates'+str(j)), dendrite_module.dendrites_to_candidates[j])


def set_pb_mode(dendrite_module, mode):
    if mode == "n":
        if GPA.pc.get_verbose():
            print("so calling all the things to add to layers")
        for i in range(0, GPA.pc.get_global_candidates()):
            dendrite_module.dendrite_values[i].locked[0] = 1


def killer_recursive(in_vals, killing):
    """
    If killing is true go through in_vals and kill all of the tensor gradients
    If killing is false, this function is still required to return the correct device
    """
    # Check license every 0.000001% of the time, this should also have been checked in convert network
    # Checking additionally here since check can be easily removed from convert network in open source
    if random.random() < 0.000001:
        license_file = "./license.yaml"
        status = check_license.valid_license(license_file)
        if not status:
            print("License Invalid. Quiting...")
            sys.exit(1)
    # Go through the in_vals of various types and either continue recursing
    # or kill the gradients if it is a tensor
    device = None
    if type(in_vals) is list:
        if len(in_vals) == 0:
            return in_vals, None
        for index in range(len(in_vals)):
            in_vals[index], device2 = killer_recursive(in_vals[index], killing)
            if not device2 is None:
                device = device2
    elif type(in_vals) is tuple:
        if len(in_vals) == 0:
            return in_vals, None
        for index in range(len(in_vals)):
            in_vals = list(in_vals)
            in_vals[index], device2 = killer_recursive(in_vals[index], killing)
            if not device2 is None:
                device = device2
            in_vals = tuple(in_vals)
    elif type(in_vals) is dict:
        if len(in_vals.keys()) == 0:
            return in_vals, None
        for index in in_vals.keys():
            in_vals[index], device2 = killer_recursive(in_vals[index], killing)
            if not device2 is None:
                device = device2
    elif issubclass(torch.Tensor, type(in_vals)):
        with torch.cuda.device_of(in_vals):
            if killing:
                to_return = grad_killer(in_vals).detach().clone()
            else:
                to_return = in_vals
            return to_return, in_vals.device
    else:
        return in_vals, None
    return in_vals, device


def preprocess_pb(*args, **kwargs):
    """
    Applies killer to args and kwargs
    """
    args2, device = killer_recursive(args, GPA.pc.get_dendrite_graph_mode())
    kwargs2, device2 = killer_recursive(kwargs, GPA.pc.get_dendrite_graph_mode())
    return args2, kwargs2


def add_dendrite_inputs(dendrite_module, i, candidate_outs, outs, view_tuple, device):
    for in_index in range(dendrite_module.num_dendrites):
        # This is only the case when passing a single datapoint rather than a batch
        if view_tuple == [1]:
            candidate_outs = (
                candidate_outs.to(device)
                + dendrite_module.dendrites_to_candidates[i][in_index, :].to(device)
                * outs[in_index]
            )
        else:
            candidate_outs = (
                candidate_outs.to(device)
                + dendrite_module.dendrites_to_candidates[i][in_index, :]
                .view(view_tuple)
                .to(device)
                * outs[in_index]
            )
    return candidate_outs


def forward_candidates(dendrite_module, view_tuple, dendrite_outs, *args, **kwargs):
    """
    This is the main forward function to process dendrite candidates
    """
    # candidate_outs is a dict for the outs which have already been zeroed and nonlinearity applied
    candidate_outs = {}
    # candidate_nonlinear_outs is a dict for the output values after the nonlinearity
    candidate_nonlinear_outs = {}
    # candidate_non_zeroed is a dict for the outputs which have not been zeroed but not yet had nonlinearity applied
    candidate_non_zeroed = {}

    for i in range(0, GPA.pc.get_global_candidates()):
        # dendrite_module.mode will only not also be p if this is not learning
        if GPA.pai_tracker.member_vars["mode"] == "p" and dendrite_module.mode == "p":
            # first apply killer to the inputs and get the device
            args2, device = killer_recursive(args, GPA.pc.get_candidate_graph_mode())
            kwargs2, device2 = killer_recursive(
                kwargs, GPA.pc.get_candidate_graph_mode()
            )
            dendrite_outs, _ = killer_recursive(
                dendrite_outs, GPA.pc.get_candidate_graph_mode()
            )
            if device is None:
                device = device2

            """
            DEBUG: if you\'re here this layer should have PAI nodes which means
            candidate processors should have been initialized.  If its not you are likely
            still pointing to the old model that doesn\'t have PAI nodes added.  make sure
            when you call add validation score you are properly setting the model
            """
            # Call processors on the killed inputs
            if dendrite_module.candidate_processors != []:
                try:
                    args2, kwargs2 = dendrite_module.candidate_processors[i].pre_d(
                        *args2, **kwargs2
                    )
                except Exception as e:
                    traceback.print_exc(limit=None, chain=True)
                    print(
                        f"Your candidate pre_d processor for {dendrite_module.name} caused this error"
                    )
                    print(
                        f"You must check how this is defined and ensure that it is properly"
                    )
                    print(
                        f"accepting inputs to the PAIModule and returning what will then be"
                    )
                    print(f"the input to the dendrite module")
                    sys.exit()

            """
            DEBUG:
            If you are getting a cpu vs gpu issue on this line its because the model is receiving args that are on the wrong device,
            but within the forward function it gets passed to the correct spot.  
            don't ever call to() in the forward function, call it before it gets passed in.
            """
            # Pass the inputs through the candidate module
            candidate_out_values = dendrite_module.candidate_module[i].to(device)(
                *args2, **kwargs2
            )

            # Post process the candidates output
            if dendrite_module.candidate_processors != []:
                try:
                    candidate_outs[i] = dendrite_module.candidate_processors[i].post_d(
                        candidate_out_values
                    )
                except Exception as e:
                    traceback.print_exc(limit=None, chain=True)
                    print(
                        f"Your post_d processor for {dendrite_module.name} caused this error"
                    )
                    print(
                        f"You must check how this is defined and ensure that it is properly"
                    )
                    print(
                        f"accepting outputs from the dendrite module and returning the"
                    )
                    print(
                        f"single tensor to be combined with the neurons output tensor"
                    )
                    sys.exit()
            else:
                candidate_outs[i] = candidate_out_values

            # Add to the candidate output the dendrite outputs * dendrite_to_candidates weights
            candidate_outs[i] = add_dendrite_inputs(
                dendrite_module, i, candidate_outs[i], dendrite_outs, view_tuple, device
            )

            # Tag the candidate out so it will be passed to the Cascor backward function
            # With the associated dendrite_values
            """
            if GPA.pc.get_dendrite_learn_mode():
                candidate_outs[i] = pai_tagger(
                    candidate_outs[i], dendrite_module.dendrite_values[i].to(device)
                )
            """
            # Apply nonlinearity
            candidate_nonlinear_outs[i] = GPA.pc.get_pai_forward_function()(
                candidate_outs[i]
            ).to(device)

            # candidate_nonlinear_outs chosen randomly, just generally saying dont do this during inference, only training.
            if dendrite_module.training:
                # no it seems like this should be cleared on the main module so when its replicated it should work properly.
                if device.type == "cpu":
                    device_index = 0
                else:
                    device_index = device.index
                if (
                    GPA.pc.get_debugging_memory_leak()
                    and len(
                        dendrite_module.dendrite_values[i].dendrite_outs[device_index]
                    )
                    != 0
                ):
                    # this is a flag that can be set to debug memory leaks
                    # it should not be required but for incorrect implementations this sometimes fixes issues without downside.
                    # Just deletes additional tensors that have been incorrectly accumulated to the list
                    if GPA.pc.get_no_backward_workaround():
                        if GPA.pc.get_verbose():
                            print(
                                "%s clearing values in workaround"
                                % dendrite_module.dendrite_values[i].layer_name
                            )

                        del dendrite_module.dendrite_values[i].dendrite_outs[
                            device_index
                        ][-1]
                        # Following may also be required for no_backward_workaround.  Found it earlier, but didn't have a noBackwards problem to debug with
                        # del dendrite_module.dendrite_values[i].current_parent_d[device_index][-1]
                    else:
                        print(
                            "%s is in backwards graph multiple times."
                            % dendrite_module.name
                        )
                        a = len(dendrite_module.dendrite_values[0].dendrite_outs[dendrite_module.dendrite_values[0].device])
                        b = len(dendrite_module.dendrite_values[0].current_parent_d[dendrite_module.dendrite_values[0].device])
                        print(
                            "This will cause a memory leak unless it is a recurrent layer."
                        )
                        print(
                            "Dendrite outs and neuron errors are currently stacked (%d/%d) times"
                            % (a, b)
                        )

                        print(
                            "If this is coming up before a memory leak that happens anywhere "
                            + "other than the first batch of an epoch you NEED to debug this."
                        )
                        print("Check the Memory Leak section of the debugging MD file.")
                        print(
                            "If this is just being printed but there is not a memory leak"
                            + " you can set GPA.pc.set_debugging_memory_leak(False)"
                        )
                        print(
                            "If you don't have any recurrent layers you can also clear this by"
                            + " in a more memory efficient way by setting GPA.pc.set_no_backward_workaround(True)"
                        )
                        print(
                            "If you set GPA.pc.set_no_backward_workaround(True) and it causes a"
                            + " IndexError: list index out of range error, that means you do have a recurrent layer"
                        )
                        print(
                            "If this comes up just once or twice and not every single batch you are likely using\n"
                            "a library or method that sometime does forwards and backwards without optimizer.step()\n"
                            "In this cases we now handle this properly and you can just set GPA.pc.set_debugging_memory_leak(False)"
                        )
                # if doing CC learning add the nonlinear outs to the dendrite values for access during backward
                if GPA.pc.get_dendrite_learn_mode():
                    if GPA.pc.get_extra_verbose():
                        print(
                            "%s appending dendrite_outs"
                            % dendrite_module.dendrite_values[i].layer_name
                        )

                    dendrite_module.dendrite_values[i].dendrite_outs[
                        device_index
                    ].append(candidate_nonlinear_outs[i])
                    if (
                        GPA.pc.get_extra_verbose() or GPA.pc.get_verbose()
                    ) and candidate_nonlinear_outs[i].isnan().any():
                        print("got candidate out nan")
                        import pdb

                        pdb.set_trace()
            # Save the non zeroed version and zero the main version
            candidate_non_zeroed[i] = (
                candidate_nonlinear_outs[i].detach().clone().to(device)
            )
            # candidate_outs[i] = no_forward(candidate_nonlinear_outs[i])

    # Debug check for NaN values in candidate outputs
    if GPA.pc.get_debugging_backwards_nan():
        got_nan = False
        for i, tensor in candidate_outs.items():
            if tensor.isnan().any() or tensor.isinf().any():
                got_nan = True

        for i, tensor in candidate_nonlinear_outs.items():
            if tensor.isnan().any() or tensor.isinf().any():
                got_nan = True
        for i, tensor in candidate_non_zeroed.items():
            if tensor.isnan().any() or tensor.isinf().any():
                got_nan = True
        if got_nan:
            print(
                "Got a NaN or inf in candidate outputs in layer %s"
                % dendrite_module.name
            )
            print(
                "Try using GPA.pc.set_candidate_grad_clipping(1.0) to prevent large candidate gradients"
            )
            # if this doesnt work try also doing weight clipping or other types of clipping
            import pdb

            pdb.set_trace()
    return candidate_outs, candidate_nonlinear_outs, candidate_non_zeroed


"""
def fix_batchnorm_nans(module, min_var=1e-8, max_var=1000.0):
    "" "Fix NaN values and cap variance in BatchNorm statistics
    
    Args:
        module: PyTorch module to fix
        min_var: Minimum allowed variance (default: 1e-8)
        max_var: Maximum allowed variance (default: 1000.0)
    "" "
    for name, layer in module.named_modules():
        if isinstance(
            layer, (torch.nn.BatchNorm1d, torch.nn.BatchNorm2d, torch.nn.BatchNorm3d)
        ):
            with torch.no_grad():
                # Fix NaN values in running_mean
                if layer.running_mean.isnan().any():
                    print(f"Fixing NaN in BatchNorm running_mean in {name}")
                    fixed_mean = torch.where(
                        torch.isnan(layer.running_mean.detach()),
                        torch.zeros_like(layer.running_mean.detach()),
                        layer.running_mean.detach(),
                    )
                    layer.running_mean.copy_(fixed_mean)
                
                # Fix NaN values in running_var and clamp to [min_var, max_var]
                if layer.running_var.isnan().any() or \
                   layer.running_var.min() < min_var or \
                   layer.running_var.max() > max_var:
                    
                    if layer.running_var.isnan().any():
                        print(f"Fixing NaN in BatchNorm running_var in {name}")
                    if layer.running_var.min() < min_var:
                        print(f"Clamping low variance ({layer.running_var.min():.2e}) in {name}")
                    if layer.running_var.max() > max_var:
                        print(f"Clamping high variance ({layer.running_var.max():.2e}) in {name}")
                    
                    # Replace NaN with 1.0, then clamp to valid range
                    fixed_var = torch.where(
                        torch.isnan(layer.running_var.detach()),
                        torch.ones_like(layer.running_var.detach()),
                        layer.running_var.detach(),
                    )
                    clamped_var = torch.clamp(fixed_var, min=min_var, max=max_var)
                    layer.running_var.copy_(clamped_var)
"""


def check_dendrite_outs(values, device_index):
    """
    This function checks that the outputs and current parent d lists are the correct length
    """
    if len(values.dendrite_outs[device_index]) == 0:
        print("Dendrite does not have output Value for layer %s" % values.layer_name)
        print(
            "This can be caused by your model being in eval mode when you call loss.backwards()"
        )
        import pdb

        pdb.set_trace()


def new_best(saved_values):
    """
    This function checks if the new correlation is better than the previous best
    and returns the updated best score and indexes of best scores
    """
    temp_abs = saved_values.prev_dendrite_candidate_correlation.detach().clone().abs()
    # best score is the max score of the previous best score and the current recently averaged correlation
    [best_score, best_indices] = torch.max(
        torch.cat(
            (
                saved_values.best_score.unsqueeze(0),
                temp_abs.unsqueeze(0),
            ),
            0,
        ),
        0,
    )
    return best_score, best_indices


def dendrite_score_beats_current_best(new_score, old_score):
    """
    Returns if any neurons new score is better than the old score by the required percentage and raw amount
    """
    return (
        ((new_score * (1.0 - GPA.pc.get_pai_improvement_threshold()))) > old_score
    ).any() and (
        (new_score - GPA.pc.get_pai_improvement_threshold_raw()) > old_score
    ).any()


def grad_killer(inp):
    """
    Kills the gradient for the input tensor but keeps forward
    """

    class Killer(torch.autograd.Function):
        # Potentially add staticmethod back later, but this doesnt work in compiled version
        # @staticmethod
        def forward(ctx, inp):
            return inp

        # Potentially add staticmethod back later, but this doesnt work in compiled version
        # @staticmethod
        def backward(ctx, grad_out):
            return grad_out * 0, None

    return Killer.apply(inp)


def reinitialize_for_pb(dendrite_module):
    """
    When filling from n mode to p mode this function reinitializes the dendrite module variables
    And copies over the accumulated averages so Cascor has access to them
    """
    for val_name in MPA.DENDRITE_REINIT_VALUES:
        if (not val_name in NON_LIVE_SKIP_VALUES) or GPA.pc.get_learn_dendrites_live():
            setattr(dendrite_module, val_name, getattr(dendrite_module, val_name) * 0)

    if GPA.pc.get_doing_thing():
        dendrite_module.parent_max_mean_act.copy_(
            dendrite_module.normal_pass_max_mean_act.detach().clone()
        )
        dendrite_module.parent_max_mean_act.requires_grad = False
    dendrite_module.parents_average_d_vector.copy_(
        dendrite_module.normal_pass_average_d.detach().clone()
    )
    dendrite_module.parents_average_d_vector.requires_grad = False
    # dendrite_module.parents_average_d_mags.copy_(dendrite_module.normal_pass_average_d_mags.double().detach().clone())
    # dendrite_module.parents_average_d_sq.copy_(dendrite_module.normal_pass_average_d_sq.double().mean().detach().clone())
    # dendrite_module.parents_average_d_sq.requires_grad = False
    # dendrite_module.parents_average_d_mags.requires_grad = False
