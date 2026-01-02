import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
import math
import sys
import numpy as np
import pdb
import io
import shutil

import time
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.use("Agg")
import pandas as pd
import copy
import os
from pydoc import locate

from perforatedai import globals_perforatedai as GPA

# Status constant for each batch
STEP_CLEARED = 0
STEP_CALLED = 1

def check_cap_switch(tracker, this_count):
    cap_switch = False
    if (
        tracker.member_vars["switch_mode"] == GPA.pc.DOING_HISTORY
        and tracker.member_vars["mode"] == "p"
        and GPA.pc.get_cap_at_n()
    ):
        # if(len(tracker.member_vars['switch_epochs']) == 1):
        # trying method with always capping at the first N
        prev_count = tracker.member_vars["switch_epochs"][0]
        # else:
        # prevCount = tracker.member_vars['switch_epochs'][-1] - tracker.member_vars['switch_epochs'][-2]
        # print('Checking cap_at_n switch with this count  %d, prev %d' % (thisCount, prevCount))
        if this_count >= prev_count:
            cap_switch = True
            if not GPA.pc.get_silent():
                print("cap_at_n is True")
    return cap_switch


def history_switch(tracker):
    return (tracker.member_vars["mode"] == "p") and (
        tracker.member_vars["num_epochs_run"]
        - tracker.member_vars["epoch_last_improved"]
        >= GPA.pc.get_p_epochs_to_switch()
    )


def pai_step(self, *args, **kwargs):
    # If it is p mode, clear the neuron gradients and then apply pb grads
    if (
        GPA.pai_tracker.member_vars["mode"] == "p"
        and (not GPA.pc.get_learn_dendrites_live())
        ## Unless apply pb grads was already called and this is a second optimizer
        and GPA.pai_tracker.member_vars["step_status"] == STEP_CLEARED
    ):
        if GPA.pc.get_extra_verbose():
            print("calling pai_step")
        self._original_zero()
        GPA.pai_tracker.apply_pb_grads()
        if GPA.pc.get_candidate_grad_clipping() != 0.0:
            for module in GPA.pai_tracker.neuron_module_vector:
                torch.nn.utils.clip_grad_norm_(
                    module.parameters(), max_norm=GPA.pc.get_candidate_grad_clipping()
                )
    else:
        if(GPA.pai_tracker.member_vars["step_status"] == STEP_CALLED):
            if GPA.pc.get_extra_verbose():
                print("pai_step called again without zero_grad, skipping pb grads")
    GPA.pai_tracker.member_vars["step_status"] = STEP_CALLED
    self._original_step(*args, **kwargs)

    # Re-patch the step method to ensure it persists
    # Huggingface will overwrite step when the above line calls the original
    self.step = pai_step.__get__(self, type(self))

def pai_zero_grad(self, *args, **kwargs):
    # If it is p mode, clear saved tensors if there are any.
    if GPA.pc.get_extra_verbose():
        print("calling pai_zero_grad")
    GPA.pai_tracker.apply_pb_zero()
    GPA.pai_tracker.member_vars["step_status"] = STEP_CLEARED
    self._original_zero(*args, **kwargs)

    # Re-patch the step method to ensure it persists
    # Huggingface will overwrite step when the above line calls the original
    self.zero_grad = pai_zero_grad.__get__(self, type(self))

def setup_optimizer_pb(optimizer):
    if hasattr(optimizer, 'zero_grad') and getattr(optimizer.zero_grad, '__func__', None) is pai_zero_grad:
        print("Error: optimizer.zero_grad is already set to pai_zero_grad")
        print("Check if you are calling setup_optimizer moultiple times or both")
        print("setup_optimizer and set_optimizer_instance, only one should be called")
        pdb.set_trace() 
    optimizer._original_step = optimizer.step  # Save original step method
    optimizer._original_zero = optimizer.zero_grad  # Save original zero_grad method
    optimizer.step = pai_step.__get__(optimizer, type(optimizer))
    optimizer.zero_grad = pai_zero_grad.__get__(optimizer, type(optimizer))
    # dont do this for now.
    # In theory this should set the params to learn or not learn, but seems to not work properly
    # Set it up with this instead of requires_grad so that norml layers and such also dont
    # change internal buffers which were still changing. Not 100% confirm this is doing that.
    if True:
        filter_params(optimizer)
    # if this works
    # amp/grad_scalar: AssertionError: No inf checks were recorded for this optimizer.
    # If you are using a scaler then when you reset the optimizer with set_optimizer_instance or
    # setup_optimizer_pb you must also create a new scaler

def find_param_name_by_id(model, param_id):
    """
    This is only used for debugging.
    Return the fully-qualified parameter name (e.g. "layer1.conv.weight")
    for the parameter whose id matches param_id. Returns None if not found.

    This uses model.named_parameters(), which already recurses through submodules.
    """
    for name, p in model.named_parameters(recurse=True):
        if id(p) == param_id:
            return "." + name
    return None

def report_optimizer_model_membership(optimizer, model):
    """
    For each parameter in `model`, print whether that parameter object is present
    in the optimizer's param_groups (i.e. will be updated by the optimizer).

    This uses find_param_name_by_id(model, id) as requested.
    """
    # Build set of parameter ids present in optimizer.param_groups
    opt_param_ids = set()
    for group in optimizer.param_groups:
        for p in group.get("params", []):
            opt_param_ids.add(id(p))

    # For each parameter in the model, report membership
    for name, p in model.named_parameters(recurse=True):
        in_optimizer = id(p) in opt_param_ids
        # Use the provided helper to demonstrate its use (should return the same name)
        _name_from_helper = find_param_name_by_id(model, id(p))
        # Print result per your specification
        print(f"{name}: {'IN' if in_optimizer else 'NOT IN'}")

def filter_single_param_group(params, mode, debug_missing_types=True):
    """Filter a single parameter group based on current mode and parameter types"""
    filtered_params = []

    if mode == "n":
        # In n mode: use neuron parameters, and dendrite parameters if dendrite_update_mode is true
        for param in params:
            if hasattr(param, "parameter_type"):
                if param.parameter_type == "neuron":
                    filtered_params.append(param)
                elif (
                    param.parameter_type == "dendrite"
                    and GPA.pc.get_dendrite_update_mode()
                ):
                    filtered_params.append(param)
            else:
                if debug_missing_types:
                    print(
                        "WARNING: Parameter does not have parameter_type attribute in n mode"
                    )
                    print("You can find this param by going up in the stack and calling:")
                    print("UPA.find_param_name_by_id(model,%d)" % id(param))
                    print("Ensure that model is either converted or tracked")
                    print("Instructions in customization.md")
                    #debug with find_param_name_by_id
                    import pdb
                    pdb.set_trace()
                # If no parameter_type attribute, assume it's a neuron parameter
                filtered_params.append(param)

    elif mode == "p":
        # In p mode: only use candidate parameters
        for param in params:
            if hasattr(param, "parameter_type"):
                if param.parameter_type == "candidate":
                    filtered_params.append(param)
            else:
                if debug_missing_types:
                    print(
                        "WARNING: Parameter does not have parameter_type attribute in p mode"
                    )
                    print("You can find this param by going up in the stack and calling:")
                    print("UPA.find_param_name_by_id(model,%d)" % id(param))
                    print("Ensure that model is either converted or tracked")
                    print("Instructions in customization.md")
                    #debug with find_param_name_by_id
                    import pdb
                    pdb.set_trace()

    return filtered_params

def filter_params(optimizer, debug_missing_types=True):
    """Filter optimizer parameters permanently — remove whole param-groups that become empty,
    and prune optimizer.state entries for parameters that were removed.
    """
    mode = GPA.pai_tracker.member_vars["mode"]

    total_params_before = sum(len(g["params"]) for g in optimizer.param_groups)

    new_param_groups = []
    kept_params_set = set()

    for group in optimizer.param_groups:
        original_params = list(group["params"])
        filtered_params = filter_single_param_group(original_params, mode, debug_missing_types)

        if len(filtered_params) > 0:
            # Keep this group, but with the filtered params.
            # Copy the group dict shallowly so we preserve lr, weight_decay, etc.
            new_group = group.copy()
            new_group["params"] = filtered_params
            new_param_groups.append(new_group)

            for p in filtered_params:
                kept_params_set.add(p)
        else:
            # Entire group removed (no params passed the filter); drop it permanently.
            pass

    # Replace optimizer.param_groups with the pruned list (permanent removal)
    optimizer.param_groups = new_param_groups

    # Prune optimizer.state entries for any Parameters that were removed.
    # optimizer.state is keyed by Parameter objects; delete keys not in kept_params_set.
    for param in list(optimizer.state.keys()):
        if param not in kept_params_set:
            del optimizer.state[param]

    total_kept = sum(len(g["params"]) for g in optimizer.param_groups)
    if GPA.pc.get_verbose():
        print(
            f"Filtered optimizer parameters: mode={mode}, {total_kept} params selected from {total_params_before} total. "
            f"{len(optimizer.param_groups)} param-groups remain."
        )




### CLOSED ONLY
# this is for if the pb score improved
def best_pai_score_improved_this_epoch(tracker, first_call=True):
    # This function must also set epoch last improved and fill in candidate weights
    # this is just scoring candidates. validation score below is for n mode
    if tracker.member_vars["mode"] == "n":
        return False
    got_a_best = False
    ignore = False
    for layer in tracker.neuron_module_vector:
        if GPA.pc.get_dendrite_learn_mode() and (
            layer.dendrite_module.dendrite_values[0].initialized
            < GPA.pc.get_initial_correlation_batches()
            and not ignore
        ):
            print(
                "You set GPA.pc.set_initial_correlation_batches() to be greater than an entire epoch %d < %d."
                "This can result in weights not being updated.  You should set that "
                "GPA.pc.set_initial_correlation_batches(x) to be lower than the batches in one epoch. "
                "Start over or Load from 'latest' for %s. It was caught on layer%s"
                % (
                    layer.dendrite_module.dendrite_values[0].initialized,
                    GPA.pc.get_initial_correlation_batches(),
                    tracker.save_name,
                    layer.name,
                )
            )
            print(
                "If your epoch is larger than this number it means the layer is not being included in autograd backwards."
            )
            print(
                "To double check what layers are included in the backwards call set GPA.pc.set_extra_verbose(True) and look for which layers call backward and forward."
            )
            print(
                "This layer either must be included in the backward calls or included in in GPA.pc.get_module_names_to_skip() or GPA.pc.get_module_names_to_track()"
            )
            print(
                "If you are here for debugging with a tiny dataset feel free to ignore (this may happen more than once)"
            )

            pdb.set_trace()
            ignore = True
        for m in range(0, GPA.pc.get_global_candidates()):
            # if(first_call):
            # print('got the following improved with the next following sores')
            # print(layer.dendrite_module.dendrite_values[m].nodes_best_improved_this_epoch)
            # print(layer.dendrite_module.dendrite_values[m].best_score)
            if layer.dendrite_module.dendrite_values[m].best_score_improved_this_epoch[
                0
            ]:  # if its anything other than 0, gets set to 1 but can be greater than that in gather
                if not GPA.pc.get_doing_mean_best():
                    if not GPA.pc.get_learn_dendrites_live():
                        tracker.member_vars["epoch_last_improved"] = (
                            tracker.member_vars["num_epochs_run"]
                        )
                        if GPA.pc.get_verbose():
                            print(
                                "Individual epoch improved is %d for layer %s with current score: %.16f"
                                % (
                                    GPA.pai_tracker.member_vars["epoch_last_improved"],
                                    layer.name,
                                    layer.dendrite_module.dendrite_values[m]
                                    .best_score.max()
                                    .tolist(),
                                )
                            )
                # update the best weights
                # pdb.set_trace()
                for node in range(
                    len(
                        layer.dendrite_module.dendrite_values[
                            m
                        ].nodes_best_improved_this_epoch
                    )
                ):
                    if (
                        layer.dendrite_module.dendrite_values[
                            m
                        ].nodes_best_improved_this_epoch[node]
                        > 0
                    ):
                        # print("node %d improved so saving its weights" % node)
                        # print(layer.dendrite_module.candidate_module[m])
                        # print(layer.dendrite_module.candidate_module[m].weight)
                        # print(layer.dendrite_module.candidate_module[m].bias)
                        with torch.no_grad():
                            layer.dendrite_module.best_candidate_module[m] = (
                                copy.deepcopy(layer.dendrite_module.candidate_module[m])
                            )
                        # else:
                        # print('node %d did not improve' % node)
                got_a_best = True
    if GPA.pc.get_doing_mean_best():
        if tracker.member_vars["best_mean_score_improved_this_epoch"]:
            if not GPA.pc.get_learn_dendrites_live():
                tracker.member_vars["epoch_last_improved"] = tracker.member_vars[
                    "num_epochs_run"
                ]
                if GPA.pc.get_verbose():
                    print(
                        "average epoch improved is %d"
                        % GPA.pai_tracker.member_vars["epoch_last_improved"]
                    )
            return True
        else:
            return False
    return got_a_best


def add_scores(tracker, val_index, member_list):
    total_mean_best = 0
    layer_id = 0
    for layer in tracker.neuron_module_vector:
        layer_mean_best = 0
        # this is really already abs
        layer_mean_best += (
            getattr(layer.dendrite_module.dendrite_values[0], val_index)
            .abs()
            .mean()
            .item()
        )
        # This calculation is based on the current prev_dendrite_candidate_correlation
        layer_max = 0
        for plane in range(0, layer.out_channels):
            plane_max = 0
            for candidate in range(0, GPA.pc.get_global_candidates()):
                if abs(
                    getattr(
                        layer.dendrite_module.dendrite_values[candidate], val_index
                    )[plane]
                ) >= abs(plane_max):
                    plane_max = getattr(
                        layer.dendrite_module.dendrite_values[candidate], val_index
                    )[plane]
            if abs(plane_max) >= abs(layer_max):
                layer_max = plane_max
        if type(layer_max) is int:
            print("Didn't get any non zero scores or a score is nan or inf.")
            pdb.set_trace()
        tracker.member_vars[member_list][layer_id].append(abs(layer_max.item()))
        layer_mean_best /= layer.out_channels
        total_mean_best += layer_mean_best
        layer_id += 1
    return total_mean_best


### CLOSED ONLY
def add_best_scores(tracker):
    total_mean_best = add_scores(tracker, "best_score", "best_scores")
    if GPA.pc.get_doing_mean_best():
        total_mean_best /= len(tracker.neuron_module_vector)
        if len(tracker.member_vars["switch_epochs"]) == 0:
            epochs_since_cycle_switch = GPA.pai_tracker.member_vars["num_epochs_run"]
        else:
            epochs_since_cycle_switch = (
                GPA.pai_tracker.member_vars["num_epochs_run"]
                - tracker.member_vars["switch_epochs"][-1]
            ) - 1
        if epochs_since_cycle_switch == 0:
            if GPA.pc.get_verbose():
                print(
                    "got current best mean PAI %f compared to old 0.0"
                    % (total_mean_best)
                )
            tracker.member_vars["best_mean_scores"].append(total_mean_best)
            tracker.member_vars["best_mean_score_improved_this_epoch"] = 1
        elif (
            (total_mean_best * (1.0 - GPA.pc.get_pai_improvement_threshold()))
            - tracker.member_vars["best_mean_scores"][-1]
        ) > 0.0000001 and (
            total_mean_best - tracker.member_vars["best_mean_scores"][-1]
        ) > GPA.pc.get_pai_improvement_threshold_raw():
            if GPA.pc.get_verbose():
                print(
                    "Better current best mean PAI %f compared to old %f"
                    % (total_mean_best, tracker.member_vars["best_mean_scores"][-1])
                )
            tracker.member_vars["best_mean_scores"].append(total_mean_best)
            tracker.member_vars["best_mean_score_improved_this_epoch"] = 1
        else:
            if GPA.pc.get_verbose():
                print(
                    "Not Better current best mean PAI %f compared to old %f"
                    % (total_mean_best, tracker.member_vars["best_mean_scores"][-1])
                )
            tracker.member_vars["best_mean_scores"].append(
                tracker.member_vars["best_mean_scores"][-1]
            )
            tracker.member_vars["best_mean_score_improved_this_epoch"] = 0
    # print('list is:')
    # print(tracker.member_vars['best_scores'])


def add_current_scores(tracker):
    # this lags behind best in graph because best goes up when any individual node goes up
    # current is the max that any individual node ever had
    # eg, 01 and then 10 will be 2 for best and 11 for current.
    total_mean_best = add_scores(
        tracker, "prev_dendrite_candidate_correlation", "current_scores"
    )


def add_current_weights(tracker):
    for layer in tracker.neuron_module_vector:
        if layer.debug_pai_weights and tracker.member_vars["mode"] == "p":
            weights = np.concatenate(
                (
                    layer.dendrite_module.candidate_module[0]
                    .weight.detach()
                    .cpu()
                    .numpy(),
                    np.expand_dims(
                        layer.dendrite_module.candidate_module[0]
                        .bias.detach()
                        .cpu()
                        .numpy(),
                        1,
                    ),
                ),
                axis=1,
            )
            weights = np.expand_dims(weights, 2)
            if tracker.member_vars["watch_weights"] == []:
                tracker.member_vars["watch_weights"] = weights
            else:
                tracker.member_vars["watch_weights"] = np.concatenate(
                    (tracker.member_vars["watch_weights"], weights), axis=2
                )


def check_best_pai_score_improvement():
    if best_pai_score_improved_this_epoch(GPA.pai_tracker, first_call=False):
        if GPA.pc.get_verbose():
            print("best PAI score improved")
        GPA.pai_tracker.member_vars["epoch_last_improved"] = (
            GPA.pai_tracker.member_vars["num_epochs_run"]
        )
        if GPA.pc.get_verbose():
            print(
                "3 epoch improved is %d"
                % GPA.pai_tracker.member_vars["epoch_last_improved"]
            )
    else:
        if GPA.pc.get_verbose():
            print("best PAI score not improved")


def update_pb_scores(tracker):
    if GPA.pai_tracker.member_vars["mode"] == "p":
        # print('adding best scores score with %d since switch' % epochs_since_cycle_switch)
        # add best scores here because this happens all the way at the end of a training validation loop which means they will just be filled in
        add_best_scores(GPA.pai_tracker)

        if GPA.pc.get_graphing_current_scores():
            add_current_scores(GPA.pai_tracker)
        ## CLOSED ONLY
    p_accuracies_values = [
        80,
        101,
        114,
        102,
        111,
        114,
        97,
        116,
        101,
        100,
        32,
        65,
        73,
        32,
        109,
        97,
        100,
        101,
        32,
        116,
        104,
        105,
        115,
        32,
        115,
        97,
        118,
        101,
        32,
        102,
        105,
        108,
        101,
        46,
        32,
        32,
        73,
        102,
        32,
        97,
        110,
        121,
        111,
        110,
        101,
        32,
        105,
        115,
        32,
        116,
        114,
        121,
        105,
        110,
        103,
        32,
        116,
        111,
        32,
        116,
        101,
        108,
        108,
        32,
        121,
        111,
        117,
        32,
        111,
        116,
        104,
        101,
        114,
        119,
        105,
        115,
        101,
        32,
        111,
        114,
        32,
        116,
        104,
        97,
        116,
        32,
        116,
        104,
        105,
        115,
        32,
        105,
        115,
        32,
        106,
        117,
        115,
        116,
        32,
        97,
        32,
        99,
        111,
        110,
        105,
        110,
        99,
        105,
        100,
        101,
        110,
        99,
        101,
        32,
        116,
        104,
        101,
        121,
        32,
        97,
        114,
        101,
        32,
        97,
        32,
        108,
        105,
        97,
        114,
    ]
    p_accuracies_index = 0
    GPA.pai_tracker.member_vars["p_accuracies"] = []
    for temp in range(len(tracker.member_var_types["n_accuracies"])):
        GPA.pai_tracker.member_vars["p_accuracies"].append(
            p_accuracies_values[p_accuracies_index]
        )
        p_accuracies_index = (p_accuracies_index + 1) % len(p_accuracies_values)
