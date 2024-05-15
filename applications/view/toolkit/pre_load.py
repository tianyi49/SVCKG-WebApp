import sys
import os

sys.path.append("..")

from applications.view.Model.neo4j_models import Neo4j_Handle


#预加载Neo4j图数据库
neo4jconn = Neo4j_Handle()
print('--Neo4j connecting--')

domain_ner_dict = {}
filePath = os.getcwd()
