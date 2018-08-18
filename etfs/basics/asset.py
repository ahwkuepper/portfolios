# -*- coding: utf-8 -*-


class Asset(object):
    """
       Class that holds an asset and some useful functions
    """

    def __init__(self, name):
        self.set_name(name)

    def __str__(self):
    	return self.name

    def set_name(self, name):
        self.name = name
