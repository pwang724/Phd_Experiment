from tools import file_io


class Config:
    save_mat_f = file_io.save_text
    load_mat_f = file_io.load_text

    save_cons_f = file_io.save_pickle
    load_cons_f = file_io.load_pickle

    LOCAL_DATA_PATH = 'C:/Users/Peter/PycharmProjects/phd_project/DATA'
    LOCAL_DATA_SINGLE_FOLDER = 'single'
    LOCAL_DATA_TIMEPOINT_FOLDER = 'timepoint'

    LOCAL_FIGURE_PATH = 'C:/Users/Peter/PycharmProjects/phd_project/FIGURES'
    LOCAL_EXPERIMENT_PATH = 'C:/Users/Peter/PycharmProjects/phd_project/EXPERIMENTS'
    LOCAL_ANALYSIS_PATH = 'C:/Users/Peter/PycharmProjects/phd_project/ANALYSIS'