from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, SelectField,IntegerField
from wtforms.validators import DataRequired,NumberRange, Length


class MyBaseForm(FlaskForm):
    class Meta:
        locales = ['zh']

class EntityForm(MyBaseForm):
    entity = StringField('entity', validators=[DataRequired(), Length(0, 1000)])
    submit = SubmitField('查询')

class RelationForm(MyBaseForm):
    entity1 = StringField('entity1',validators=[DataRequired(), Length(0, 1000)])
    relation = IntegerField('relation',validators=[DataRequired(),NumberRange(1,5)])
    entity2 = StringField('entity2',validators=[DataRequired(), Length(0, 1000)])
    submit = SubmitField('查询')
#漏洞分布表单
class StatisticForm(MyBaseForm):
    start_time1=StringField('start_time',validators=[DataRequired()])
    end_time1=StringField('end_time',validators=[DataRequired()])
    statistic_type= SelectField('statistic_type', choices=[(1, '漏洞影响类型'),[2,'漏洞利用的攻击位置'],[3,'漏洞的危害程度'],[4,'漏洞cvss评分']], default=1, coerce=int)
    submit = SubmitField('查询')
#数量趋势表单
class StatisticForm2(MyBaseForm):
    start_time2=StringField('start_time',validators=[DataRequired()])
    end_time2=StringField('end_time',validators=[DataRequired()])
    statistic_type2= SelectField('statistic_type', choices=[(10, '全部'),[11,'高危'],[12,'中危'],[13,'低危']], default=10, coerce=int)
    submit2 = SubmitField('查询')
#知识推理功能
class ReasonForm(MyBaseForm):
    equip_input=StringField('equip_input',validators=[DataRequired(), Length(0, 100)])
    submit = SubmitField('开始推理')
#知识补全功能
class CompletionForm(MyBaseForm):
    submit = SubmitField('知识补全')
#表单页面跳转
class PagecountForm(MyBaseForm):
    page_num_input=IntegerField('page_num_input',validators=[DataRequired(),NumberRange(1,100)])
    submit3 = SubmitField('跳转')