#%%
import json
import logging
import pathlib
from enum import Enum

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

#TODO move to common/constants


class EnumInterpolation(Enum):
    """this is an Collection of values that interpolation can take.

    The problem is that the code is based on str, instead of integer values

    Returns:
        _type_: _description_
    """    
    RAW = 'raw'
    LINEAR = 'linear'
    CUBIC = 'cubic'
    SPLINE = 'spline'
    DELAUNAY = 'delaunay'

    @classmethod
    def to_list(cls):
        # return cls._member_names_
        return list(map(lambda c: c.value, cls)) # with enum
        # return [value for name, value in vars(cls).items() if not name.startswith("__")]
        # return [cls.RAW, cls.LINEAR, cls.CUBIC, cls.SPLINE, cls.DEALUNEY]

class EnumStrainType(Enum):
    GREEN_LAGRANGE = 'green_lagrange' # should be the same as 2nd order
    CAUCHY_ENG = 'cauchy-eng'
    LOG = 'log'
    SECOND_ORDER = '2nd_order'
    
    @classmethod
    def to_list(cls):
        # return cls._member_names_
        return list(map(lambda c: c.value, cls))
        # return [cls.CAUCHY, cls.LOG, cls.SECOND_ORDER]

class EnumTrackingMethodType(Enum):
    #TOD O
    UNSTRUCTURED = 'unstructured_grid'
    DEEP_FLOW = 'deep_flow'
    LUCAS_KANADE  = 'Lucas-Kanade'


    @classmethod
    def to_list(cls):
        # return cls._member_names_
        return list(map(lambda c: c.value, cls))


class EnumDataSelection(Enum):
    REMOVE_BORDER = 'Remove OUTSIDE Border'
    SELECT_ALL = 'Select All'
    PORTION0_20 = 'Select [20% to 80%]'
    PORTION0_40 = 'Select [40% to 60%]'
    
    
    @classmethod
    def to_list(cls):
        return list(map(lambda c: c.value, cls))
    

LocationMeasuresDict:dict = {
    "mean": 'mean',
    "median": 'median'
}