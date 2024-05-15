# -*- coding: utf-8 -*-
import torch
from torch.utils.data import DataLoader
from applications.view.handler.kgCompletion import config
import numpy as np
import json
from torch.utils.data import dataloader
from applications.view.handler.kgCompletion.my_dataloader import tripleDataset
args = config.Config()         #引入配置参数类

# 准备测试数据迭代器
def prepareTestDataloader(args):
    dataset = tripleDataset(posDataPath=args.testpath,
                            entityDictPath=args.entpath,
                            relationDictPath=args.relpath)
    #注意此处能够设置验证集数据迭代器的batchsize大小
    dataloader = DataLoader(dataset,
                            batch_size=len(dataset),
                            shuffle=False,
                            drop_last=False)
    return dataloader

# 传入数据迭代器，模型，距离评估方式，嵌入向量字典,返回显示预测结果及概率
def forecast(evalloader:dataloader, model_name, model,simMeasure="dot", **kwargs):
    for tri in evalloader:
        tri = tri.numpy()
        head, relation, tail = tri[:, 0], tri[:, 1], tri[:, 2]
        if model_name == "TransH":
            simscore= evalTransH(head, relation,model,simMeasure, **kwargs)
        else:
            print("ERROR : The %s evaluation is not supported!" % model)
            exit(1)
    top3list = np.empty(shape=(len(simscore),3),dtype=int)
    # 找到尾实体前三个最相似的实体（排除自身），并返回其索引及距离度量
    for i in range(len(simscore)):
        temindex=np.argsort(simscore[i])
        if(temindex[0]==head[i]):
            top3list[i]=temindex[1:4]
        else:
            top3list[i]=temindex[0:3]
    head=head.tolist()
    relation=relation.tolist()
    top3list=top3list.tolist()
    for i in range(len(simscore)):
        top3list[i]=[[j,simscore[i][j]] for j in top3list[i]]
    kgCompletion=[]
    for i in range(len(simscore)):
        kgCompletion.append([head[i],relation[i],top3list[i]])
    return kgCompletion
def evalTransH(head, relation,model, simMeasure, **kwargs):
    # Gather embedding
    with torch.no_grad():
        head_sentence = [model.itowordi[i] for i in head.tolist()]  # batchnum*embeddingnum
        head_sentence = model.des_entityEmbedding(torch.tensor(head_sentence, dtype=torch.int32).type(torch.LongTensor).cuda())
        head_ds_vector = model.cnn_vector(head_sentence).detach().cpu().numpy()
        head = np.take(kwargs["entityEmbed"], indices=head, axis=0)
        hyper = np.take(kwargs["hyperEmbed"], indices=relation, axis=0)
        relation = np.take(kwargs["relationEmbed"], indices=relation, axis=0)
        # Projection
        head = head - hyper * np.sum(hyper * head, axis=1, keepdims=True)
        head_ds_vector=head_ds_vector- hyper * np.sum(hyper * head_ds_vector, axis=1, keepdims=True)

        #计算实体描述向量
        all_sentence = [model.itowordi[i] for i in range(model.entnum)]  # batchnum*embeddingnum
        all_sentence = model.des_entityEmbedding(torch.tensor(all_sentence, dtype=torch.int32).type(torch.LongTensor).cuda())
        all_ds_vector = model.cnn_vector(all_sentence).detach().cpu().numpy()
        simScore = calHyperSim(head+relation,head_ds_vector+relation, kwargs["entityEmbed"], hyper, all_ds_vector,simMeasure=simMeasure)
    return simScore
# 计算实体列表中各个尾实体的距离
def calHyperSim(expTailMatrix,exp_des_TailMatrix,tailEmbedding, hyperMatrix, taildesEmbedding,simMeasure="dot"):
    simScore = []
    for expM, hypM,expdesM in zip(expTailMatrix, hyperMatrix,exp_des_TailMatrix):
        '''
        expM : shape(E,)
        hypM : shape(E,)
        Step1 : Projection tailEmbedding on hyperM as hyperTailEmbedding(shape(N,E))
        Step2 : Calculate similarity between expTailMatrix and hyperTailEmbedding
        Step3 : Add similarity to simMeasure
        (1, E) * matmul((N, E), (E, 1)) -> (1, E) * (N, 1) -> (N, E)
        '''
        # 得到尾实体在关系平面上的投影向量hyperTailEmbedding
        hyperTailEmbedding = tailEmbedding - hypM[np.newaxis,:] * np.matmul(tailEmbedding, hypM[:,np.newaxis])
        hyperdesTailEmbedding = taildesEmbedding - hypM[np.newaxis, :] * np.matmul(taildesEmbedding, hypM[:, np.newaxis])
        if simMeasure == "dot":
            simScore.append(np.squeeze(np.matmul(hyperTailEmbedding, expM[:, np.newaxis])))
        elif simMeasure == "L2":
            # (E,) -> (1, E)
            # (N, E) - (1, E) -> (N, E)
            # np.linalg.norm()求范数
            score = np.linalg.norm(hyperTailEmbedding-expM[np.newaxis, :], ord=2, axis=1, keepdims=False)\
                    +np.linalg.norm(hyperdesTailEmbedding - expdesM[np.newaxis, :], ord=2, axis=1, keepdims=False)\
                    +np.linalg.norm(hyperdesTailEmbedding - expM[np.newaxis, :], ord=2, axis=1, keepdims=False) \
                    + np.linalg.norm(hyperTailEmbedding - expdesM[np.newaxis, :], ord=2, axis=1, keepdims=False)
            simScore.append(score)
        else:
            print("ERROR : simMeasure %s is not supported!" % simMeasure)
            exit(1)
    return np.array(simScore)
class trainTriples():
    def __init__(self, args):
        self.args = args

    def loadPretrainModel(self):
        if self.args.modelname == "TransH":
            print("INFO : Loading pre-training model.")
            self.model = torch.load(self.args.premodel)
        else:
            print("ERROR : Model type %s is not supported!")
            exit(1)

    def testModel(self):
        print("INFO : Testing model %s"%self.args.modelname)
        self.loadPretrainModel()
        self.model.retEvalWeight={"entityEmbed": self.model.entityEmbedding.weight.detach().cpu().numpy(),
                "relationEmbed": self.model.relationEmbedding.weight.detach().cpu().numpy(),
                "hyperEmbed": self.model.relationHyper.weight.detach().cpu().numpy(),
                "init_weightentity_des_Embed":self.model.des_entityEmbedding.weight.detach().cpu().numpy()}
        self.testloader = prepareTestDataloader(self.args)
        kgCompletion= forecast(evalloader=self.testloader,
                                          model_name=self.args.modelname,
                                          model=self.model,
                                          simMeasure=args.simmeasure,
                                          **self.model.retEvalWeight)
        entitylist = json.load(open(self.args.entpath, "r"))["itos"]
        relationlist = json.load(open(self.args.relpath, "r"))["itos"]
        # 将实体id转换为实体名
        for i in range(len(kgCompletion)):
            kgCompletion[i][0]=entitylist[kgCompletion[i][0]]
            kgCompletion[i][1]=relationlist[kgCompletion[i][1]]
            kgCompletion[i][2]=[[entitylist[j[0]],j[1]] for j in kgCompletion[i][2]]
        return kgCompletion


def kgCompletion():
    # 设置 args
    trainModel = trainTriples(args)
    kgCompletion=trainModel.testModel()
    return kgCompletion