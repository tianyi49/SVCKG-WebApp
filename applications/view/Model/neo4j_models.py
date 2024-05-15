import time

from py2neo import Graph, NodeMatcher,RelationshipMatcher
class Neo4j_Handle():
    graph = None

    # matcher = None
    def __init__(self):
        print("Neo4j Init ...")
        self.graph = Graph("http://localhost:7474", auth=("neo4j", "tianyi49"), name='neo4j')
        self.node_matcher = NodeMatcher(self.graph)
        self.relationship_matcher=RelationshipMatcher(self.graph)
    #实体名字查找关系图
    #name:实体名字 ，tuplelist：接收三元组 ，dir关系边方向0为出，1为入
    #对返回数量进行限制提高速率
    def get_entity_relgraph(self,name,tuplelist=[],dir=0):
        if(dir==0):
            answer = self.graph.run(
                "MATCH (entity1:%s) - [rel] ->(entity2)  WHERE entity1.name ='%s' RETURN entity1,rel,entity2 limit 80" % (name[0],name[1])).data()
        else:
            answer = self.graph.run(
                "MATCH (entity1) - [rel] ->(entity2:%s)  WHERE entity2.name ='%s' RETURN entity1,rel,entity2 limit 80" % (name[0],name[1])).data()
        for i in range(len(answer)):
            node1 = answer[i]['entity1']
            entity1 = [str(node1.labels).strip(':'), dict(node1)]  # 第1个元素是标签，第二个是元素属性字典
            node2 = answer[i]['entity2']
            entity2 = [str(node2.labels).strip(':'), dict(node2)]  # 第1个元素是标签，第二个是元素属性字典
            rel = type(answer[i]['rel']).__name__
            tuplelist.append([entity1, rel, entity2])
    # 实体名字查找关系图，返回实体关系实体三元组,出入两个方向
    #name:实体名字
    def getEntityRelationbyEntity(self, entity):
        tuplelist=[]  #[实体，关系，实体]
        start = time.clock()
        self.get_entity_relgraph(entity,tuplelist)
        self.get_entity_relgraph(entity, tuplelist,dir=1)
        end=time.clock()
        cost_time=round(end-start,5)
        return tuplelist,cost_time
    #根据实体标签获得对应的实体列表
    def  getEntityTag(self,entity_tag,pagecounter=0):
        skipnum=int(pagecounter-1)*5000
        tuplelist= []
        start =time.clock()
        answer = self.graph.run(
           f"MATCH (entity:{entity_tag})  RETURN entity skip {skipnum}  limit 5000").data()
        for i in range(len(answer)):
            node= answer[i]['entity']
            entity=[str(node.labels).strip(':'), dict(node)]
            tuplelist.append(entity)
        end=time.clock()
        cost_time1 = round(end - start, 5)
        return tuplelist,cost_time1
    #输入两个实体和路径长度限制，返回返回实体关系实体三元组
    def find_route(self,label_name1, relation, label_name2):
        tuplelist = []  # [实体，关系，实体]
        answer = self.graph.run(f'MATCH (from:{label_name1[0]}), (to:{label_name2[0]}) where from.name="{label_name1[1]}" and to.name="{label_name2[1]}" CALL apoc.algo.allSimplePaths(from, to,"", {relation}) YIELD path RETURN  path limit 100').data()
        for i in range(len(answer)):
            for j in range(len(answer[i]['path'].relationships)):
                node1=answer[i]['path'].relationships[j].nodes[0]
                entity1=[str(node1.labels).strip(':'), dict(node1)]# 第1个元素是标签，第二个是元素属性字典
                node2 = answer[i]['path'].relationships[j].nodes[1]
                entity2 = [str(node2.labels).strip(':'), dict(node2)]  # 第1个元素是标签，第二个是元素属性字典
                rel = type(answer[i]['path'].relationships[j]).__name__
                tuplelist.append([entity1, rel, entity2])
        return tuplelist
    def getRelationTag(self,relation_tag, pagecounter):
        skipnum = int(pagecounter-1) * 2000
        tuplelist = []
        answer = self.graph.run(f" match path=(m)-[r:{relation_tag}]->(n)   RETURN m,n skip {skipnum}  limit 2000").data()
        for i in range(len(answer)):
            node1=answer[i]['m']
            entity1=[str(node1.labels).strip(':'), dict(node1)]# 第1个元素是标签，第二个是元素属性字典
            node2 = answer[i]['n']
            entity2 = [str(node2.labels).strip(':'), dict(node2)]  # 第1个元素是标签，第二个是元素属性字典
            rel = relation_tag
            tuplelist.append([entity1, rel, entity2])
        return tuplelist

    #首页展示数据获取，主要有"entity_num":'', "relationship_num":'' , "label_num":'', "vul_num":'',"relationship_type":[], "label_num_list":[]
    def homepagedata(self):
        dict = {"entity_num":'', "relationship_num":'' , "label_num":'', "vul_num":'',"relationship_type":[], "label_num_list":[]}
        entity_num=self.graph.run("match(n) return count(n)").data()[0]['count(n)']
        relationship_num=self.graph.run("MATCH (n)-[r]->() RETURN COUNT(r)").data()[0]['COUNT(r)']
        vul_num=self.graph.run("match(n:cve_id)  return count(n)").data()[0]['count(n)']
        dict["entity_num"]=entity_num;dict["relationship_num"]=relationship_num;dict["vul_num"]=vul_num
        dict['relationship_type']=list(self.graph.schema.relationship_types)
        dict["label_num_list"]=self.graph.run("match(n) return distinct count(labels(n)),labels(n)").data()
        label_num =len( dict["label_num_list"])
        dict["label_num"] = label_num
        return dict

