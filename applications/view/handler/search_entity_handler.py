from applications.view.toolkit.pre_load import neo4jconn


#实体查询
def search_entity(entity):
	#根据传入的实体名称搜索出关系
	#连接数据库
	db = neo4jconn
	# 针对输入文本：标签加实体名进行分割
	entity=entity.split(':')
	tuplelist,cost_time= db.getEntityRelationbyEntity(entity)
	return tuplelist,cost_time
def search_entity_tag(entity_tag,pagecounter=0):
	db = neo4jconn
	tuplelist1,cost_time1 = db.getEntityTag(entity_tag,pagecounter)
	return tuplelist1,cost_time1