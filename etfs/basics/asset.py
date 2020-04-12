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

    def save(self, filename, datadir="../data/"):
        """
        Saves data to datadir
        """
        try:
            filepath = "{0}{1}".format(datadir, filename)
            print("Saving {}".format(filepath))
            self.data.index.name = "Date"
            self.data.to_csv(filepath, header=True, index=True)
            return 1
        except:
            print("Saving data failed")
            return 0
