
import json


class Scores:

    def __init__(self):
        self.scores = {}
        self.identity = {}
        self.index = -1

    def identification(self, string):
        if string in self.identity:
            return self.identity[string]
        else:
            self.index = self.index + 1
            self.identity[string] = self.index
            return self.index

    def load_data(self, path):
        f = open(path, "r")

        for line in f.readlines():
            split = line.split()
            if len(split) == 4:
                # both combinations just in case
                self.scores[self.identification(str(split[0])),
                            self.identification(str(split[1])), self.identification(str(split[2]))] = float(str(split[3]))

                self.scores[self.identification(str(split[0])),
                            self.identification(str(split[2])), self.identification(str(split[1]))] = float(str(split[3]))
            elif len(split) == 3:
                self.scores[self.identification(str(split[0])),
                            self.identification(str(split[1]))] = float(str(split[2]))
            else:
                raise Exception('Something is going wrong with number of words in line')

        print('File readout completed')
        return self.scores

    def export_data(self, path):
        with open(path, "w") as outfile:
            json.dump(self.scores, outfile)

        print('Export completed')


scores = Scores()
scores.load_data("C:/Users/vicen/Downloads/cancer.txt")
print(scores.scores)
print(scores.identity)

