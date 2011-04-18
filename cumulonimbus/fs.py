class FS:
    def __init__(self, swift):
        self.swift = swift
        pass

    def opendir(self, path):
        self.swift.get(path)
