import os
import numpy as np

experimentHash = {
    'exp': 'rixx1003721',
    'location': 'RixEndstation',
    'fluxSource': 'MfxDg1BmMon',
    'fluxChannels': [15],
    'fluxSign': -1,
    'singlePixels': [
        [0, 150, 10], [0, 150, 100], [0, 275, 100],
        [0, 272, 66], [0, 280, 70], [0, 282, 90],
        [0, 270, 90], [0, 271, 90], [0, 272, 90], [0, 273, 90],
        [0, 265 + 22, 60 + 35], [0, 265 + 21, 60 + 12],
        [0, 275 + 1, 100], [0, 275 + 2, 100], [0, 275 + 3, 100]
    ],
    'ROIs': ['XavierV4_2', 'OffXavierV4_2'],
    'regionSlice': np.s_[270:288, 59:107]
}