import os
import glob
import numpy as np
from xml.dom import minidom
from skimage import io
import time
import scipy.io as sio

class baseCons(object):
    def __init__(self):
        pass

    def update(self, new_config):
        self.__dict__.update(new_config.__dict__)

    def __str__(self):
        print('[***] CONFIG[***]')
        dict = self.__dict__
        s= ''
        for key, val in dict.items():
            if key == 'DAQ_DATA':
                s += "{0:<20s}: {1:<100s}".format(key, str(val.shape)) + '\n'
            else:
                val = str(val)
                s += "{0:<20s}: {1:<100s}".format(key, val) + '\n'
        s += '[***]/CONFIG[***]'
        return s

class ConstantCons(baseCons):
    def __init__(self):
        super(ConstantCons, self).__init__()

        self.FOLDER_ANALYSIS = 'E:\IMPORTANT DATA\DATA_X'
        self.DIR_STORAGE_EFTY = 'E:\IMPORTANT DATA\STORAGE_EFTY'
        self.DIR_STORAGE_ROI = 'E:\IMPORTANT DATA\STORAGE_ROI'
        self.DIR_STORAGE_DATA = 'E:\IMPORTANT DATA\STORAGE_DATA'
        self.DIR_VIZ_PICS = 'E:\IMPORTANT DATA\VIZ_PICS'
        self.KEY_EFTY = '_EFTY'

        self.DAQ_O = 1
        self.DAQ_L = 3
        self.DAQ_W = 4
        self.DAQ_SAMP = 1000

class Cons(ConstantCons):
    '''
    DAQ_W_ON, W_OFF takes on DEFAULT_O values if DAQ_W_ON > 6 seconds.
    DAQ_DATA dimensions: time, variable, file
    '''
    def __init__(self, path = None):
        super(Cons, self).__init__()

        if path is None:
            self.DIR = 'E:/IMPORTANT DATA/DATA_2P/M187_ofc/7-27-2016/420'
        else:
            self.DIR = path

        #can be editted later to incorporate more options.
        self.FORMAT = 'cycle'
        self.FORMAT_READ = 'tifstack'

        self.STORAGE_EFTY = None
        self.STORAGE_ROI = None
        self.STORAGE_DATA = None

        self.DIR_ORIG = None
        self.DIR_RAW = None
        self.DIR_EFTY_SEP = None
        self.DIR_EFTY_SEPK = None
        self.DIR_EFTY_SEPCAT = None

        self.FILE_BANDPASS = None
        self.NAME_MOUSE = None
        self.NAME_DATE = None
        self.NAME_PLANE = None

        self.TRIAL_FRAMES = None
        self.TRIAL_PERIOD = None

        self.ODOR_TRIALS = None
        self.ODOR_UNIQUE = None
        self.ODOR_TRIALIDX = None

        self.DEFAULT_O_ON = 5.6
        self.DEFAULT_O_OFF = 7.6

        self.DAQ_W_ON = None
        self.DAQ_O_ON = None
        self.DAQ_O_OFF = None
        self.DAQ_O_ON_F = None
        self.DAQ_O_OFF_F = None
        self.DAQ_W_ON_F = None
        self.DAQ_DATA = None

        st = time.time()
        self._getDirs()
        self._getOdors()
        self._getTiming()
        self._getDaq()
        et = time.time()
        print('Config loaded in: {0:3.3f} seconds'.format(et - st))

    def _getDirs(self):
        self.DIR_ORIG = self.DIR + '_' + self.FORMAT
        path = os.path.normpath(self.DIR)
        p, plane = os.path.split(path)
        pp, date = os.path.split(p)
        _, mouse = os.path.split(pp)
        mouse_date_plane = mouse + '_' + date + '_' + plane
        dir_raw = os.path.join(self.FOLDER_ANALYSIS, mouse, date, plane + '_')

        self.DIR_RAW = dir_raw
        self.DIR_EFTY_SEP = dir_raw + self.KEY_EFTY + 'f'
        self.DIR_EFTY_SEPK = dir_raw + self.KEY_EFTY + 'fk'
        self.FILE_BANDPASS = os.path.join(self.FOLDER_ANALYSIS, mouse, date, 'm.tif')

        self.STORAGE_DATA = os.path.join(self.DIR_STORAGE_DATA, mouse_date_plane + '.mat')
        self.STORAGE_ROI = os.path.join(self.DIR_STORAGE_ROI, mouse_date_plane + '.mat')
        self.STORAGE_EFTY = os.path.join(self.DIR_STORAGE_EFTY, mouse_date_plane + '.mat')

        self.NAME_DATE = date
        self.NAME_MOUSE = mouse
        self.NAME_PLANE = plane

    def _getOdors(self):
        tif_pathnames = glob.glob(os.path.join(self.DIR_ORIG, '*.tif'))
        tif_names = [os.path.splitext(os.path.split(x)[1])[0] for x in tif_pathnames]
        odor_names = [x[4:] for x in tif_names]
        odor_unique, odor_index = np.unique(odor_names, return_inverse= True)

        self.ODOR_TRIALIDX = odor_index
        self.ODOR_UNIQUE = odor_unique
        self.ODOR_TRIALS = odor_names

    def _getTiming(self):
        def _getPeriod(xmlfile):
            #TODO: make this more efficient
            xmldoc = minidom.parse(xmlfile)
            itemlist = xmldoc.getElementsByTagName('Key')
            for s in itemlist:
                if s.attributes['key'].value == 'framePeriod':
                    period = float(s.attributes['value'].value)
                    return period

        dirs = os.listdir(self.DIR)
        xml_file = glob.glob(os.path.join(self.DIR, dirs[0], '*.xml'))[0]

        try:
            period = _getPeriod(xml_file)
        except:
            raise ValueError("""cannot read the xml file: {}""".format(xml_file))

        tifs = glob.glob(os.path.join(self.DIR_ORIG, '*.tif'))
        tif_file = tifs[0]
        try:
            im = io.imread(tif_file)
        except:
            raise ValueError("""cannot read the tiff file: {}""".format(tif_file))

        self.TRIAL_PERIOD = period
        self.TRIAL_FRAMES = im.shape[0]

    def _getDaq(self):
        def _get_odor_timing(O):
            max_pid_per_odor = np.max(O, axis=0)
            odor_ix = np.argmax(max_pid_per_odor)
            max_odor_pid = O[:, odor_ix]
            min, max = np.min(max_odor_pid), np.max(max_odor_pid)
            max_odor_pid = (max_odor_pid - min) / (max - min)
            O_on = np.argwhere(max_odor_pid > thres_odor_high)[0][0] / self.DAQ_SAMP
            O_off = np.argwhere(max_odor_pid > thres_odor_low)[-1][0] / self.DAQ_SAMP
            if O_on > 6:
                O_on = self.DEFAULT_O_ON
                O_off = self.DEFAULT_O_OFF
            return O_on, O_off


        thres_odor_low = .2
        thres_odor_high = .5

        daqs = glob.glob(os.path.join(self.DIR_ORIG, '*.mat'))
        test = [sio.loadmat(f)['data'] for f in daqs]
        data = np.stack(test, axis=2)
        dsamp_factor = 20
        data = data[::dsamp_factor,:,:]
        self.DAQ_SAMP /= dsamp_factor
        try:
            W = data[:,self.DAQ_W,:]
            W_t = np.argwhere(W > 1)[0][0]
            W_t /= self.DAQ_SAMP
        except:
            W_t = 10.02

        O = data[:,self.DAQ_O,:]


        self.DAQ_W_ON = W_t
        self.DAQ_O_ON, self.DAQ_O_OFF = _get_odor_timing(O)

        self.DAQ_O_ON_F = np.round(self.DAQ_O_ON/self.TRIAL_PERIOD)
        self.DAQ_O_OFF_F = np.round(self.DAQ_O_OFF/self.TRIAL_PERIOD)
        self.DAQ_W_ON_F = np.round(self.DAQ_W_ON/self.TRIAL_PERIOD)
        self.DAQ_DATA = data

if __name__ == '__main__':
    a = Cons()
    print(a)
    # dict = a.__dict__
    # for key, val in dict.items():
    #     print('{}: {}'.format(key, val))