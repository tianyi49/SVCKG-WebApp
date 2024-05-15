from flask import Blueprint
from flask import render_template,redirect,url_for
from flask_login import login_required, current_user


from applications.view.handler import  search_entity_handler, search_relation_handler,statistic_handler,reason_handler
from applications.view.handler.kgCompletion import completion_handler
from applications.view.toolkit.pre_load import neo4jconn
from applications.view.forms import  EntityForm, RelationForm,StatisticForm,StatisticForm2,ReasonForm,PagecountForm,CompletionForm
index_bp = Blueprint('index', __name__)
#各个页面的缓存数据
dictcache={"homepage_date":'',"statistic_analysis":{"data1":{"formtype":'',"select_dict":'',"form":''},"data2":{"formtype":'',"select_dict":'',"form":''}},"max_page_num":1}
@index_bp.route('/')
def index():
    dictcache['statistic_analysis']["data1"].update((key, '') for key in dictcache['statistic_analysis']["data1"])
    dictcache['statistic_analysis']["data2"].update((key, '') for key in dictcache['statistic_analysis']["data2"])
    return render_template('index/index.html')


# 首页
@index_bp.get('/admin/')
@login_required
def admin_index():
    dictcache['statistic_analysis']["data1"].update((key, '') for key in dictcache['statistic_analysis']["data1"])
    dictcache['statistic_analysis']["data2"].update((key, '') for key in dictcache['statistic_analysis']["data2"])
    return render_template('index/admin_index.html', user=current_user)


# 控制台页面
@index_bp.get('/admin/welcome')
@login_required
def welcome():
    dictcache['statistic_analysis']["data1"].update((key, '') for key in dictcache['statistic_analysis']["data1"])
    dictcache['statistic_analysis']["data2"].update((key, '') for key in dictcache['statistic_analysis']["data2"])
    if (len(dictcache["homepage_date"]) == 0):
        home_dict=neo4jconn.homepagedata()
        dictcache["homepage_date"]=home_dict
    else:
        home_dict=dictcache["homepage_date"]
    return render_template('index/welcome.html',home_dict=home_dict)

#传递了三个参数：标签名，页码，页码偏移
@index_bp.route('/search_entity/<entity_tag>/<int:pagecounter>/<int:pageoffset>', methods=['GET', 'POST'])
@login_required
def search_entity(entity_tag,pagecounter=0,pageoffset=0):
    dictcache['statistic_analysis']["data1"].update((key, '') for key in dictcache['statistic_analysis']["data1"])
    dictcache['statistic_analysis']["data2"].update((key, '') for key in dictcache['statistic_analysis']["data2"])
    entity_form = EntityForm()
    page_form=PagecountForm()
    tuplelist=['padding']
    cost_time=0#实体查询时间
    cost_time1 = 0  # 实体标签查询时间
    #标签实体
    tuplelist1=[]
    #对列表页码的处理
    if(pageoffset!=2):
        pagecounter=pagecounter+pageoffset
    else:
        pagecounter=pagecounter-1
    if(pagecounter<1):
        pagecounter=1
    # 跳转页面有bug，暂时不用
    if page_form.validate_on_submit():
        pagecounter = page_form.page_num_input.data
        # return redirect(url_for('index.search_entity', entity_tag=entity_tag, pagecounter=page_form.page_num_input.data, pageoffset=0))
    if(entity_tag != 'None'):
        #获得最大页码
        for item in dictcache['homepage_date']['label_num_list']:
            if(entity_tag==item['labels(n)'][0]):
                dictcache['max_page_num']=int((item['count(labels(n))']-1)/5000)+1
                break
        if(pagecounter>dictcache['max_page_num']):
            pagecounter=1
        tuplelist1,cost_time1=search_entity_handler.search_entity_tag(entity_tag,pagecounter)

        # if(tuplelist1==[]):
        #    return redirect(url_for('index.search_entity',entity_tag=entity_tag,pagecounter=1,pageoffset=0))
    if entity_form.validate_on_submit():# 自动获取提交的数据，然后进行校验
       try:
            tuplelist,cost_time= search_entity_handler.search_entity(entity_form.entity.data)
       except:
            tuplelist=[]
            cost_time=0
    return render_template('index/entity.html', form=entity_form,page_form=page_form,tuplelist=tuplelist,home_dict=dictcache["homepage_date"],entity_tag=entity_tag,tuplelist1=tuplelist1,pagecounter=pagecounter,max_page_num=dictcache['max_page_num'],cost_time=cost_time/2,cost_time1=cost_time1)

@index_bp.route('/search_relation/<relation_tag>/<int:pagecounter>/<int:pageoffset>', methods=['GET', 'POST']) #路由分发，路由回应方式
@login_required
def search_relation(relation_tag,pagecounter=0,pageoffset=0):
    dictcache['statistic_analysis']["data1"].update((key, '') for key in dictcache['statistic_analysis']["data1"])
    dictcache['statistic_analysis']["data2"].update((key, '') for key in dictcache['statistic_analysis']["data2"])
    relation_form = RelationForm()
    tuplelist=['padding']
    # 标签关系
    tuplelist1 = []
    if (pageoffset != 2):
        pagecounter = pagecounter + pageoffset
    else:
        pagecounter = pagecounter - 1
    if(pagecounter<1):
        pagecounter=1
    if (relation_tag != 'None'):
       tuplelist1 = search_relation_handler.search_relation_tag(relation_tag, pagecounter)
       if (tuplelist1 == []):
           return redirect(url_for('index.search_relation', relation_tag=relation_tag, pagecounter=1, pageoffset=0))
    if relation_form.validate_on_submit():# 自动获取提交的数据，然后进行校验
        try:
            tuplelist= search_relation_handler.search_relation(relation_form.entity1.data, relation_form.relation.data, relation_form.entity2.data)
            return render_template('index/relation.html', form=relation_form, tuplelist=tuplelist,
                                   home_dict=dictcache["homepage_date"],
                                   entity2list=[relation_form.entity1.data.split(':'),relation_form.entity2.data.split(':')],path_length=int(relation_form.relation.data),relation_tag=relation_tag)
        except:
            tuplelist = []
    return render_template('index/relation.html', form=relation_form, tuplelist=tuplelist,home_dict=dictcache["homepage_date"],entity2list=[],tuplelist1=tuplelist1,relation_tag=relation_tag,pagecounter=pagecounter)
@index_bp.route('/statistic_analysis', methods=['GET', 'POST'])
@login_required
def statistic_analysis():
    statistic_form = StatisticForm()
    statistic_form2=StatisticForm2()
    select_dict= {'flag':0}    #表示表单的状态0不展示，1展示，2搜索结果为空
    select_dict2={'flag':0}
    formtype=0         #表示表单类型
    formtype2=0
    #表单一
    if statistic_form.validate_on_submit():# 自动获取提交的数据，然后进行校验
        formtype = statistic_form.statistic_type.data
        try:
            select_dict = statistic_handler.search_statistical(statistic_form.start_time1.data,statistic_form.end_time1.data,statistic_form.statistic_type.data)
        except:
            select_dict={}
        if(select_dict=={}):
            select_dict['flag'] = 2
        #flag为1可以展示
        else:
            select_dict['flag']=1
        # 对当前数据进行存储，对表单2的数据进行恢复
        dictcache["statistic_analysis"]["data1"]["select_dict"] = select_dict
        dictcache["statistic_analysis"]["data1"]["formtype"]=formtype
        dictcache["statistic_analysis"]["data1"]["form"]=statistic_form
        select_dict2 = dictcache["statistic_analysis"]["data2"]["select_dict"] 
        if (dictcache["statistic_analysis"]["data2"]["form"] != ''):
            statistic_form2=dictcache["statistic_analysis"]["data2"]["form"]
        formtype2=dictcache["statistic_analysis"]["data2"]["formtype"]
    if statistic_form2.validate_on_submit():  # 自动获取提交的数据，然后进行校验
        formtype2= statistic_form2.statistic_type2.data
        try:
            select_dict2 = statistic_handler.search_statistical(statistic_form2.start_time2.data,statistic_form2.end_time2.data,statistic_form2.statistic_type2.data)
        except:
            select_dict2={}
        if(select_dict2=={}):
            select_dict2['flag'] = 2
        else:
            select_dict2['flag']=1
        #对当前数据进行存储，对表单1数据进行恢复
        dictcache["statistic_analysis"]["data2"]["select_dict"] = select_dict2
        dictcache["statistic_analysis"]["data2"]["formtype"]=formtype2
        dictcache["statistic_analysis"]["data2"]["form"]=statistic_form2
        select_dict=dictcache["statistic_analysis"]["data1"]["select_dict"]
        if(dictcache["statistic_analysis"]["data1"]["form"]!=''):
            statistic_form= dictcache["statistic_analysis"]["data1"]["form"]
        formtype= dictcache["statistic_analysis"]["data1"]["formtype"]
    return render_template('index/statistic.html',form=statistic_form,form2=statistic_form2,select_dict=select_dict,select_dict2=select_dict2,formtype=formtype,formtype2=formtype2)

# 推理模块
@index_bp.route('/reason', methods=['GET', 'POST'])
@login_required
def reson():
    dictcache['statistic_analysis']["data1"].update((key, '') for key in dictcache['statistic_analysis']["data1"])
    dictcache['statistic_analysis']["data2"].update((key, '') for key in dictcache['statistic_analysis']["data2"])
    tuplelist=[]
    tabeldict={}
    kgCompletion=[]
    kgCompletion.append('None')
    reason_form=ReasonForm()
    completion_form=CompletionForm()
    tabeldict['baseflag'] = 0
    if reason_form.validate_on_submit():
        try:
            tuplelist, tabeldict=reason_handler.equip_reason(reason_form.equip_input.data)
            return render_template('index/reason.html', tuplelist=tuplelist, tabeldict=tabeldict, form=reason_form,
                                   kgCompletion=kgCompletion, form2=completion_form)
        except:
            tuplelist = []
            tabeldict = {}
            return render_template('index/reason.html', tuplelist=tuplelist, tabeldict=tabeldict, form=reason_form,
                                   kgCompletion=kgCompletion, form2=completion_form)
    if completion_form.validate_on_submit():
        kgCompletion=completion_handler.kgCompletion()
        for i in kgCompletion:
            if('cwe' in i [0]):
                i[0]=i[0].replace('cwe','CWE-')
            elif('capec' in i[0]):
                i[0]=i[0].replace('capec','CAPEC-')
            for j in range(len(i[2])):
                if('cwe' in i[2][j][0]):
                    i[2][j][0]=i[2][j][0].replace('cwe','CWE-')
                elif('capec' in i[2][j][0]):
                    i[2][j][0]=i[2][j][0].replace('capec','CAPEC-')
    return render_template('index/reason.html',tuplelist=tuplelist,tabeldict=tabeldict, form=reason_form,kgCompletion=kgCompletion,form2=completion_form)
