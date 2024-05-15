# -*- coding: utf-8 -*-

import torch

class Config():
    def __init__(self):
        # Data arguments
        self.testpath = "applications/view/handler/kgCompletion/data/test.txt"
        self.entpath = "applications/view/handler/kgCompletion/data/entityDict.json"
        self.relpath = "applications/view/handler/kgCompletion/data/relationDict.json"

        # Dataloader arguments
        self.shuffle = True
        self.numworkers =0

        # self.device= torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.usegpu = torch.cuda.is_available()
        self.gpunum = 0
        self.modelname = "TransH"
        self.simmeasure = "L2"
        self.modelsave = "full"
        self.modelpath = "data/model/"
        self.premodel = "applications/view/handler/kgCompletion/data/TransH_ent200_rel200_type.model"
