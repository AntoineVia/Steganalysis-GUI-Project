class ImportFile:
    def __init__(self, file="", path="", dico=None, steg=False):
        self.filename = file
        self.path = path
        if dico is None:
            self.steg_dict: dict = {}
        else:
            self.steg_dict: dict = dico
        self.steg_detected = steg

    def __repr__(self):
        if self.steg_dict:
            s = ",".join([self.filename, self.path, str(self.steg_dict), str(self.steg_detected)])
        else:
            s = ",".join([self.filename, self.path, str(""), str(self.steg_detected)])
        return s

    def __str__(self):
        s = "File name: {filename}\nFile path: {path}".format(filename=self.filename, path=self.path)
        if self.steg_dict:
            s += "\nSteganography probabilities: {dict}".format(dict=self.steg_dict)
        else:
            s += "\nSteganography probabilities: {}"
        s += "\nSteganography detected: {detec}".format(detec=self.steg_detected)
        return s

    def update(self):
        for value in self.steg_dict:
            if value >= 0.75:
                self.steg_detected = True
