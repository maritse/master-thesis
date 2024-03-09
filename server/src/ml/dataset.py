class DatasetMNIST():

    def __init__(self, path):
        self.path = path

    def load(self):
        data = list()
        labels = list()

        for (i, imgpath) in enumerate(self.path):
            pass