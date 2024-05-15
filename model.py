# -*- coding: utf-8 -*-

import torch.nn as nn
import torch.nn.functional as F
class cnn_TransH(nn.Module):
    def __init__(self, entityNum, relationNum, embeddingDim, margin=1.0, L=2, C=1.0, eps=0.001,cnn_param={},entityDict={}):
        super(cnn_TransH, self).__init__()

    # @staticmethod 可以不需要实例化，不需要表示自身对象的self和自身类的cls参数，就跟使用函数一样
    @staticmethod
    def conv_and_pool(x, conv):
        # x: (batch, 1, sentence_length,  )
        x = conv(x)
        # x: (batch, kernel_num, H_out, 1)
        x = F.relu(x.squeeze(3))
        # x: (batch, kernel_num, H_out)
        x = F.max_pool1d(x, x.size(2)).squeeze(2)
        #  (batch, kernel_num)
        return x

    def cnn_vector(self, x):
        # x: (batch, sentence_length, embed_dim)
        # TODO init embed matrix with pre-trained
        x = x.unsqueeze(1)
        # x: (batch, 1, sentence_length, embed_dim)
        x1 = self.conv_and_pool(x, self.conv11)  # (batch, kernel_num)
        x2 = self.conv_and_pool(x, self.conv12)  # (batch, kernel_num)
        # x3 = self.conv_and_pool(x, self.conv13)  # (batch, kernel_num)
        # x4=x1+x2+x3
        # return self.layer_norm(x4)
        return self.layer_norm(x1 + x2)