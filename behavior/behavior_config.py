class behaviorConfig(object):
    def __init__(self):
        #extra time (seconds) given to CS- odors after water onset for quantification.
        self.extra_csm_time = 0
        self.smoothing_window = 5
        self.smoothing_window_boolean = 9
        self.polynomial_degree = 1

        self.halfmax_up_threshold = 50
        self.halfmax_down_threshold = 50

        self.fully_learned_threshold_up = 100
        self.fully_learned_threshold_down = 10