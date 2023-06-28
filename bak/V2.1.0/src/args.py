# MIT License
#
# Copyright (c) 2023  Dr. Magnus Christ (mc0110)
#
# This is part of the inetbox2mqtt package
# 
# Simulate a persistant args-parameter string
# Usable as generator

import os


class Args():
    
    __ARGS = "args.dat"
    
    def __init__(self, fn = None):
        self.__arg = ""
        if fn != None:
            self.fn = fn
        else:
            self.fn = self.__ARGS
        if self.fn in os.listdir("/"):
            self.load()
                       
    def reset(self):
        self.__arg = ""
        os.remove(self.fn)
        
    def load(self):
        if self.fn in os.listdir("/"):
            with open(self.fn, "r") as f:
                self.__arg = f.read()
            
    def store(self, s):
        with open(self.fn, "w") as f:
                f.write(s)
        self.__arg = s
        
    def check(self, s):
        return s in self.__arg
    
    def get(self):
        a = self.__arg.split()
        while a != []:
            q = a.pop(0)
            yield q
            
    def get_key(self, key):
        for i in self.get():
            q = i.split("=")
            if q[0]==key:
                return q[1]
        return None    
