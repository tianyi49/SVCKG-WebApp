from applications.view.toolkit.pre_load import neo4jconn


def  search_relation_tag(relation_tag, pagecounter):
	db = neo4jconn
	tuplelist=db.getRelationTag(relation_tag, pagecounter)
	return tuplelist
def search_relation(entity1, relation, entity2):
	db = neo4jconn
	#针对输入文本：标签加实体名进行分割
	entity1=entity1.split(':')
	entity2= entity2.split(':')
	relation=int(relation)
	tuplelist=db.find_route(entity1, relation, entity2)
	return tuplelist
