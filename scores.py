#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json


class Scores:
    """
    Class to manage scores
    """

    def __init__(self):
        """
        Constructor
        """

        self.scores = {}
        self.identity = {}
        self.index = -1

    def identification(self, string):
        """
        Function to return the identifier of a string in the identity dictionary.
        :param string: string to be checked.
        :return: Integer with the identifier
        """

        if string in self.identity:
            return self.identity[string]
        else:
            self.index = self.index + 1
            self.identity[string] = self.index
            return self.index

    def load_data(self, path):
        """
        Load data with the scores precalculated with R script and merge it into dictionary.
        :param path: path of the txt file.
        :return: dictionary with scores.
        """
        # note that we insert negative value of score as the BIC scores is better as nearer to zero

        f = open(path, "r")

        for line in f.readlines():
            split = line.split()
            if len(split) == 4:
                # both combinations just in case
                self.scores[self.identification(str(split[0])),
                            self.identification(str(split[1])), self.identification(str(split[2]))] = -float(str(split[3]))

                self.scores[self.identification(str(split[0])),
                            self.identification(str(split[2])), self.identification(str(split[1]))] = -float(str(split[3]))
            elif len(split) == 3:
                self.scores[self.identification(str(split[0])),
                            self.identification(str(split[1]))] = -float(str(split[2]))
            elif len(split) == 2:
                self.scores[self.identification(str(split[0]))] = -float(str(split[1]))
            else:
                raise Exception('Something is going wrong with number of words in line')

        print('File readout completed')
        return self.scores

    def export_data(self, path):
        """
        Function to export the scores to a file
        :param path: path of the output file.
        :return: creates file and writes it.
        """

        with open(path, "w") as outfile:
            json.dump(self.scores, outfile)

        print('Export completed')


