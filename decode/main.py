import decode.decode_analysis
import decode.organizer
from decode import experiment_configs
import analysis
import filter
import reduce
import plot
from analysis import add_aligned_days
from tools import experiment_tools
import os
from behavior.behavior_analysis import get_days_per_mouse
import behavior.behavior_analysis
import copy
import numpy as np
from _CONSTANTS.config import Config
import _CONSTANTS.conditions as experimental_conditions
import matplotlib.pyplot as plt
from collections import defaultdict
from reduce import chain_defaultdicts

#
experiments = [
    # 'vary_neuron_odor',
    'vary_decoding_style_odor',
    # 'test_odor_across_days'
    # 'vary_decoding_style_days',
    # 'plot_vary_neuron_pir_ofc_bla'
]
EXPERIMENT = True
ANALYZE = True
argTest = True

#inputs
condition = experimental_conditions.OFC
data_path = os.path.join(Config.LOCAL_DATA_PATH, Config.LOCAL_DATA_TIMEPOINT_FOLDER, condition.name)

#load files from matlab
# init.load_matlab.load_condition(condition)

fill_args = {'zorder': 0, 'lw': 0, 'alpha': 0.3}
line_args = {'alpha': 1, 'linewidth': .5, 'marker': 'o', 'markersize': 1.5}
bar_args = {'alpha': .6, 'fill': False}
ax_args = {'yticks': [0, .2, .4, .6, .8, 1.0], 'ylim': [-.05, 1.05]}
error_args = {'fmt':'.', 'capsize':2, 'elinewidth':1, 'markersize':2, 'alpha': .5}

if 'test_odor_across_days' in experiments:
    experiment_path = os.path.join(Config.LOCAL_EXPERIMENT_PATH, 'DECODING','decoding_test_across_days', condition.name)
    save_path = os.path.join(Config.LOCAL_FIGURE_PATH, 'DECODING', 'decoding_test_across_days', condition.name)

    style = ['identity', 'csp_identity', 'csm_identity','valence']
    no_end_time = True
    if condition.name == 'PIR':
        neurons = 40
    elif condition.name == 'PIR_NAIVE':
        neurons = 40
        style = ['identity']
    elif condition.name == 'OFC':
        neurons = 40
        no_end_time = False
    elif condition.name == 'BLA':
        neurons = 20
        no_end_time = False
    elif condition.name == 'MPFC_COMPOSITE':
        neurons = 40
        no_end_time = False
    else:
        neurons = 40
        no_end_time = False

    if EXPERIMENT:
        experiment_tools.perform(experiment=decode.organizer.organizer_test_odor_across_day,
                                 condition=condition,
                                 experiment_configs=experiment_configs.test_across_days(
                                     argTest=argTest, neurons=neurons, style = style, no_end_time=no_end_time),
                                 data_path=data_path,
                                 save_path=experiment_path)

    if ANALYZE:
        res = decode.decode_analysis.load_results_train_test_scores(experiment_path)
        summary_res = reduce.new_filter_reduce(res, filter_keys=['decode_style', 'Test Day', 'Training Day'], reduce_key='top_score')

        for style in np.unique(summary_res['decode_style']):
            temp = filter.filter(summary_res, {'decode_style': style})
            x_key = 'Test Day'
            y_key = 'Training Day'
            val_key = 'top_score'
            title = 'Decoding ' + style +  ' Across Days'
            vmax = 1
            if style == 'csm_identity' or style == 'csp_identity' or style == 'valence':
                vmin = 0.5
            elif style == 'identity':
                vmin = .25
            else:
                vmin = 0
            plot.plot_weight(temp, x_key, y_key, val_key, title, vmin, vmax, text= True,
                             save_path=os.path.join(save_path, temp['decode_style'][0]))

if 'vary_decoding_style_odor' in experiments:
    experiment_path = os.path.join(Config.LOCAL_EXPERIMENT_PATH, 'DECODING', 'vary_decoding_style', condition.name)

    save_path = os.path.join(Config.LOCAL_FIGURE_PATH, 'DECODING','vary_decoding_style', condition.name)
    if EXPERIMENT:
        if condition.name == 'PIR':
            style = ['identity','csp_identity','csm_identity']
        elif condition.name == 'PIR_NAIVE':
            style = ['identity']
        elif condition.name == 'OFC' or condition.name == 'BLA' or condition.name == 'OFC_LONGTERM' or condition.name == 'MPFC_COMPOSITE':
            style = ['identity','csp_identity', 'csm_identity','valence']
        else:
            raise ValueError('condition name not recognized')
        experiment_tools.perform(experiment=decode.organizer.organizer_decode_odor_within_day,
                                 condition=condition,
                                 experiment_configs=experiment_configs.vary_decode_style(argTest=argTest, style=style),
                                 data_path=data_path,
                                 save_path=experiment_path)
    if ANALYZE:
        learned_day_per_mouse, last_day_per_mouse = get_days_per_mouse(data_path, condition)
        res = decode.decode_analysis.load_results_cv_scores(experiment_path)
        analysis.add_indices(res)
        analysis.add_time(res)
        decode.decode_analysis.add_decode_stats(res, condition)
        add_aligned_days(res, last_days=last_day_per_mouse, learned_days=learned_day_per_mouse)
        filter.assign_composite(res, ['mouse', 'shuffle'])
        filter.assign_composite(res, ['decode_style', 'shuffle'])
        if condition.name == 'PIR' or condition.name == 'PIR_NAIVE':
            day_use = last_day_per_mouse
        else:
            day_use = last_day_per_mouse
        days_per_mouse = behavior.behavior_analysis._get_days_per_condition(data_path, condition, 'CS+')
        res_final_day = filter.filter_days_per_mouse(res, [len(x) - 1 for x in days_per_mouse])
        decode_styles = np.unique(res['decode_style'])

        # #decoding, plot for each condition: mouse + decode style
        # loopkey = ['shuffle','day']
        # mice = np.unique(res['mouse'])
        # for i, mouse in enumerate(mice):
        #     for j, dc in enumerate(decode_styles):
        #         select_dict = {'mouse':mouse, 'decode_style': dc}
        #         plot.plot_results(res, x_key='time', y_key='mean', loop_keys=loopkey,
        #                           plot_function= plt.fill_between, error_key= 'sem',
        #                           select_dict=select_dict, path=save_path, ax_args=ax_args, plot_args=fill_args,
        #                           save=False)
        #         plot.plot_results(res, x_key='time', y_key='mean', loop_keys=loopkey,
        #                           select_dict=select_dict, path=save_path, ax_args=ax_args, plot_args=line_args,
        #                           reuse=True, save=True)

        # summary of performance for each day, line plot
        loopkey = ['mouse']
        mice = np.unique(res['mouse'])
        for j, decode_style in enumerate(decode_styles):
            select_dict = {'decode_style': decode_style, 'shuffle':False}
            plot.plot_results(res, x_key='day', y_key='max', loop_keys=loopkey,
                              colors= ['Black'] * mice.size,
                              select_dict= select_dict, path=save_path,
                              ax_args=ax_args, plot_args=line_args)

        #summary for last day of each mouse, with shuffle
        nMouse = np.unique(res['mouse']).size
        res_first_final_day = filter.filter_days_per_mouse(res, days_per_mouse=[0] * mice.size)
        chain_defaultdicts(res_first_final_day, res_final_day)
        for i, decode_style in enumerate(decode_styles):
            if i == 0:
                reuse_arg = False
            else:
                reuse_arg = True
            temp = filter.filter(res_final_day, {'decode_style': decode_style})
            plot.plot_results(temp, x_key='decode_style_shuffle', y_key='max', loop_keys='mouse',
                              colors=['Black']*temp['max'].size,
                              path = save_path, plot_args= line_args, ax_args=ax_args,
                              save=False, reuse=reuse_arg)

        res_nonshuffle = filter.filter(res_final_day, filter_dict={'shuffle':False})
        summary_res_nonshuffle = reduce.filter_reduce(res_nonshuffle, 'decode_style', 'max')
        res_shuffle = filter.filter(res_final_day, filter_dict={'shuffle':True})
        summary_res_shuffle = reduce.filter_reduce(res_shuffle, 'decode_style', 'max')
        chain_defaultdicts(summary_res_shuffle, summary_res_nonshuffle)
        plot.plot_results(summary_res_shuffle, x_key='decode_style_shuffle', y_key='max',
                          path = save_path, plot_function=plt.bar, plot_args=bar_args, ax_args=ax_args,
                          save=True, reuse=True, sort=True)


if 'vary_neuron_odor' in experiments:
    experiment_path = os.path.join(Config.LOCAL_EXPERIMENT_PATH, 'DECODING', 'vary_neuron', condition.name)
    save_path = os.path.join(Config.LOCAL_FIGURE_PATH, 'DECODING','vary_neuron', condition.name)

    if EXPERIMENT:
        if condition.name == 'PIR':
            style = ['identity','csp_identity', 'csm_identity']
        elif condition.name == 'PIR_NAIVE':
            style = ['identity']
        elif condition.name == 'OFC' or condition.name == 'BLA' or condition.name == 'MPFC_COMPOSITE':
            style = ['csp_identity','csm_identity','valence']
        else:
            raise ValueError('condition name not recognized')

        experiment_tools.perform(experiment=decode.organizer.organizer_decode_odor_within_day,
                                 condition=condition,
                                 experiment_configs=experiment_configs.vary_neuron(
                                     argTest=argTest, neurons=condition.min_neurons, style=style),
                                 data_path=data_path,
                                 save_path=experiment_path)

    if ANALYZE:
        res = decode.decode_analysis.load_results_cv_scores(experiment_path)
        analysis.add_indices(res)
        analysis.add_time(res)
        decode.decode_analysis.add_decode_stats(res, condition)
        if condition.name == 'PIR':
            learned_day_per_mouse, last_day_per_mouse = get_days_per_mouse(data_path, condition)
            day_use = last_day_per_mouse
            colors = ['Red', 'Green', 'Orange'] * 2
        elif condition.name == 'PIR_NAIVE':
            days_per_mouse = behavior.behavior_analysis._get_days_per_condition(data_path, condition)
            day_use = [x[-1] for x in days_per_mouse]
            colors = ['Orange'] * 2
        elif condition.name == 'OFC' or condition.name == 'MPFC_COMPOSITE':
            days_per_mouse = behavior.behavior_analysis._get_days_per_condition(data_path, condition, 'CS+')
            day_use = [len(x)-1 for x in days_per_mouse]
            colors = ['Red', 'Green', 'Gray'] * 2
        else:
            raise ValueError('condition name not recognized')
        res_final_day = filter.filter_days_per_mouse(res, days_per_mouse=day_use)

        # # decoding performance wrt time for each mouse, comparing 1st and last day
        # # plot separately for each mouse and each decode style
        # xkey = 'time'
        # ykey = 'mean'
        # loopkey = 'day'
        # decode_styles = np.unique(res['decode_style'])
        # mice = np.unique(res['mouse'])
        # for i, mouse in enumerate(mice):
        #     for j, dc in enumerate(decode_styles):
        #         select_dict = {'decode_style': dc, 'shuffle': False,
        #                        'neurons': 20,
        #                        'mouse': mouse, 'day': [0, last_day_per_mouse[i]]}
        #         plot.plot_results(res, x_key=xkey, y_key=ykey, loop_keys=loopkey, select_dict=select_dict,
        #                           path=save_path, ax_args=ax_args)

        #comparing all decode conditions on a per mouse basis

        line_args_ = copy.copy(line_args)
        line_args_.update({'linestyle':'dotted'})
        decode_styles = np.unique(res_final_day['decode_style'])
        mice = np.unique(res['mouse'])
        for mouse in enumerate(mice):
            select_dict = {'mouse': mouse}
            plot.plot_results(res_final_day, x_key='neurons', y_key='max', loop_keys=['decode_style','shuffle'],
                              select_dict=select_dict,
                              colors = colors,
                              ax_args= ax_args, plot_args=line_args,
                              path=save_path)


        #comparing all decode conditions, averaged across mice
        decode_styles = np.unique(res_final_day['decode_style'])
        summary_all = defaultdict(list)
        for j, decode_style in enumerate(decode_styles):
            temp_res = filter.filter(res_final_day, filter_dict={'decode_style': decode_style})
            summary_res = reduce.new_filter_reduce(temp_res, filter_keys=['neurons','shuffle'], reduce_key='max')
            chain_defaultdicts(summary_all, summary_res)
        plot.plot_results(summary_all, x_key='neurons', y_key='max', loop_keys='decode_style',
                          select_dict={'shuffle': False},
                          plot_function=plt.fill_between, error_key='max_sem',
                          colors= colors,
                          path=save_path, ax_args=ax_args, plot_args=fill_args,
                          save=False, reuse=False)
        plot.plot_results(summary_all, x_key='neurons', y_key='max', loop_keys='decode_style',
                          select_dict={'shuffle': True},
                          colors= colors,
                          path=save_path, ax_args=ax_args, plot_args=line_args_,
                          save=False, reuse=True)
        plot.plot_results(summary_all, x_key='neurons', y_key='max', loop_keys='decode_style',
                          select_dict={'shuffle': False},
                          colors= colors,
                          path=save_path, ax_args=ax_args, plot_args=line_args,
                          save=True, reuse=True)

if 'plot_vary_neuron_pir_ofc_bla' in experiments:
    decode_styles = ['csp_identity','csm_identity']
    conditions = [experimental_conditions.PIR, experimental_conditions.OFC, experimental_conditions.BLA]

    for decode_style in decode_styles:
        summary_all = defaultdict(list)
        save_path = os.path.join(Config.LOCAL_FIGURE_PATH, 'vary_neuron', 'PIR_OFC_BLA__' + decode_style)
        for condition in conditions:
            data_path = os.path.join(Config.LOCAL_DATA_PATH, Config.LOCAL_DATA_TIMEPOINT_FOLDER, condition.name)
            experiment_path = os.path.join(Config.LOCAL_EXPERIMENT_PATH, 'vary_neuron', condition.name)

            learned_day_per_mouse, last_day_per_mouse = get_days_per_mouse(data_path, condition)

            res = decode.decode_analysis.load_results_cv_scores(experiment_path)
            analysis.add_indices(res)
            analysis.add_time(res)
            decode.decode_analysis.add_decode_stats(res, condition)

            res_learned_day = filter.filter_days_per_mouse(res, days_per_mouse=learned_day_per_mouse)
            # last_day_per_mouse = filter.get_last_day_per_mouse(res)
            # res_final_day = filter.filter_days_per_mouse(res, days_per_mouse=last_day_per_mouse)

            temp_res = filter.filter(res_learned_day, filter_dict={'decode_style': decode_style})
            summary_res = reduce.filter_reduce(temp_res, filter_keys='neurons', reduce_key='max')
            summary_res['condition_name'] = [condition.name] * len(summary_res['max'])
            chain_defaultdicts(summary_all, summary_res)

        plot.plot_results(summary_all, x_key='neurons', y_key='max', loop_keys='condition_name',
                          path=save_path, ax_args=ax_args)



if 'vary_decoding_style_days' in experiments:
    experiment_path = os.path.join(Config.LOCAL_EXPERIMENT_PATH, 'vary_decoding_style_days', condition.name)
    save_path = os.path.join(Config.LOCAL_FIGURE_PATH, 'vary_decoding_style_days', condition.name)

    if EXPERIMENT:
        if condition.name == 'PIR' or condition.name == 'PIR_NAIVE':
            style = ['identity']
        elif condition.name == 'OFC':
            style = ['identity','csp_identity','csm_identity']
        else:
            raise ValueError('condition name not recognized')

        experiment_tools.perform(experiment=decode.organizer.organizer_decode_day,
                                 condition=condition,
                                 experiment_configs=experiment_configs.vary_decode_style(argTest=argTest, style=style),
                                 data_path=data_path,
                                 save_path=experiment_path)

    if ANALYZE:
        res = decode.decode_analysis.load_results_cv_scores(experiment_path)
        analysis.add_indices(res)
        analysis.add_time(res)
        decode.decode_analysis.add_decode_stats(res, condition)
        decode_styles = np.unique(res['decode_style'])

        #decoding, plot for each condition: mouse + decode style
        loopkey = ['shuffle']
        mice = np.unique(res['mouse'])
        for i, mouse in enumerate(mice):
            for j, dc in enumerate(decode_styles):
                select_dict = {'mouse':mouse, 'decode_style': dc}
                plot.plot_results(res, x_key='time', y_key='mean', loop_keys=loopkey,
                                  select_dict=select_dict, path=save_path, ax_args=ax_args)

        #summary for last day of each mouse
        nMouse = np.unique(res['mouse']).size
        cur_ax_args = copy.copy(ax_args)
        cur_ax_args['xticks'] = [0, 1]
        for decode_style in decode_styles:
            cur_res = filter.filter(res, {'decode_style': decode_style})
            summary_res = reduce.filter_reduce(cur_res, 'shuffle','max')
            plot.plot_results(summary_res, x_key='shuffle', y_key='max',
                              path = save_path, plot_function=plt.bar, plot_args=bar_args, ax_args=ax_args,
                              save=False)

            plot.plot_results(res, x_key='shuffle', y_key='max', loop_keys='mouse',
                              select_dict={'decode_style': decode_style},
                              colors = ['Black'] * nMouse,
                              path = save_path, plot_args= line_args, ax_args= cur_ax_args,
                              save=True, reuse=True)