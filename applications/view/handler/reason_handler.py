from applications.view.toolkit.pre_load import neo4jconn
import json


# 输入设备进行推理，返回三元组信息和利用表展示信息
def equip_reason(equip):
    tuplelist = []  # tuplelist=[entity1, rel, entity2],entity第一个元素是标签第二个元素是属性字典
    tabeldict = {}  # 格式{‘equip':设备，’cve':cve信息字典，‘cwechain’:cwe链信息，'cwe':cwe信息及相应的缓解措施,'baseflag':1表示cve可推理，2表示ics可推理,3表示其它设备，默认为0，4表示查询为空}
    try:
        with open("applications/view/sourcedata/chain_product0.14.json", encoding='utf-8') as f:
            dict1 = json.load(f)
            f.close()
        if equip in dict1:
            tabeldict['equip'] = equip
            with open("applications/view/sourcedata/cve_relate_cwe.json", encoding='utf-8') as f:
                dict_cwe = json.load(f)
                f.close()
            # 获得设备影响信息
            equip_cve = dict1[equip]['cve']
            equip_cwe = dict1[equip]['cwe']
            # 对展示表格添加漏洞信息
            with open("applications/view/sourcedata/cveinfo_tabel.json", encoding='utf-8') as f:
                cveinfo_tabel = json.load(f)
                f.close()
            tabeldict['cve'] = {}
            for cve in equip_cve:
                tabeldict['cve'][cve] = cveinfo_tabel[cve]
            # 添加equip-cve-cwe:三元组信息
            for cve in equip_cve:
                tuplelist.append([['cve_id', {"name": cve}], 'impact_product', ['product', {"name": equip}]])
                for cwe in dict_cwe[cve]:
                    if (cwe not in equip_cwe):
                        continue
                    tuplelist.append([['cve_id', {"name": cve}], 'instance_of', ['cwe_id', {"name": cwe}]])
            # 获得cwe-cwe链
            with open("applications/view/sourcedata/kg_reson_dict0.14.json", encoding='utf-8') as f:
                cwe_chainlist = json.load(f)['cwe_chainlist']
                f.close()
            # cwe_relate_cve列表
            with open("applications/view/sourcedata/cwe_relate_cve.json", encoding='utf-8') as f:
                cwe_relate_cve = json.load(f)
                f.close()
            #cweinfo字典
            with open("applications/view/sourcedata/cweinfo.json", encoding='utf-8') as f:
                cweinfo = json.load(f)
                f.close()
            tabeldict['cwechain'] = []
            # 关联cwe_chain推理
            for cwe_chain in cwe_chainlist:
                if (cwe_chain['cwe1'] in equip_cwe and cwe_chain['cwe2'] in equip_cwe):
                    cwe_chain_name = cwe_chain['cwe1'] + '&' + cwe_chain['cwe2']
                    tuplelist.append([['cwe_id', {'name': cwe_chain['cwe1']}], 'member_of', ['cwe_chain', {'name': cwe_chain_name}]])
                    tuplelist.append([['cwe_id', {'name': cwe_chain['cwe2']}], 'member_of',['cwe_chain', {'name': cwe_chain_name}]])
                    cwe1_cve_set = set(cwe_relate_cve[cwe_chain['cwe1']]);
                    cwe2_cve_set = set(cwe_relate_cve[cwe_chain['cwe2']])
                    cwe1_equip_cve = cwe1_cve_set & set(equip_cve);
                    cwe2_equip_cve = cwe2_cve_set & set(equip_cve)
                    cve_instancelist = list(cwe1_equip_cve | cwe2_equip_cve)
                    cwe1_cwe2_cve = [cwe1_equip_cve, cwe2_equip_cve]
                    cwe_chain['instance'] = cwe1_cwe2_cve
                    tabeldict['cwechain'].append(cwe_chain)
                    for  cve_instance in cve_instancelist:
                        tuplelist.append([['cwe_chain', {'name': cwe_chain_name}], 'has_instance',
                                          ['cve_id', {'name': cve_instance}]])
            # cwe信息添加
            tabeldict['cwe'] = {}
            for cwe in equip_cwe:
                try:
                    tabeldict['cwe'][cwe] = cweinfo[cwe]
                except:
                    tabeldict['cwe'][cwe] = []
            if (len(tabeldict['cwechain']) > 0):
                tabeldict['baseflag'] = 1
            else:
                tabeldict['baseflag'] = 3
            return tuplelist, tabeldict
        # ics设备库查找
        with open("applications/view/sourcedata/chain_ics_product0.14.json", encoding='utf-8') as f:
            dict1 = json.load(f)
            f.close()
        if equip in dict1:
            tabeldict['equip'] = equip
            # 获得设备影响信息
            equip_ics = dict1[equip]['ics']
            equip_cwe = []
            with open("applications/view/sourcedata/icscert1.json", encoding='utf-8') as f:
                icsinfo = json.load(f)
                f.close()
            # 得到设备对应的cve集合
            tabeldict['cve'] = {}
            for ics in equip_ics:
                equip_cwe+= [i['ics_relate_cwe'] for i in icsinfo[ics]['ics_vul']]
                tabeldict['cve'][ics] = icsinfo[ics]
            #防止字符不匹配
            equip_cwe = [i for i in equip_cwe if 'CWE' in i]
            # 添加equip-ics-cwe:三元组信息
            for ics in equip_ics:
                tuplelist.append([['ics_id', {"name": ics}], 'impact_product', ['product', {"name": equip}]])
                ics_relate_cwe = [i['ics_relate_cwe'] for i in icsinfo[ics]['ics_vul']]
                for cwe in ics_relate_cwe:
                    if (cwe not in equip_cwe):
                        continue
                    tuplelist.append([['ics_id', {"name": ics}], 'relate_cwe', ['cwe_id', {"name": cwe}]])
            # 获得cwe-cwe链
            with open("applications/view/sourcedata/kg_reson_dict0.14.json", encoding='utf-8') as f:
                cwe_chainlist = json.load(f)['cwe_chainlist']
                f.close()
            # cwe_relate_cve列表
            with open("applications/view/sourcedata/cwe_relate_cve.json", encoding='utf-8') as f:
                cwe_relate_cve = json.load(f)
                f.close()
            with open("applications/view/sourcedata/cweinfo.json", encoding='utf-8') as f:
                cweinfo = json.load(f)
                f.close()
            tabeldict['cwechain'] = []
            # 关联cwe_chain推理
            for cwe_chain in cwe_chainlist:
                if (cwe_chain['cwe1'] in equip_cwe and cwe_chain['cwe2'] in equip_cwe):
                    cwe_chain_name = cwe_chain['cwe1'] + '&' + cwe_chain['cwe2']
                    tuplelist.append(
                        [['cwe_id', {'name': cwe_chain['cwe1']}], 'member_of',
                         ['cwe_chain', {'name': cwe_chain_name}]])
                    tuplelist.append([['cwe_id', {'name': cwe_chain['cwe2']}], 'member_of',
                                      ['cwe_chain', {'name': cwe_chain_name}]])
                    # cwe1_cve_set = set(cwe_relate_cve[cwe_chain['cwe1']]);
                    # cwe2_cve_set = set(cwe_relate_cve[cwe_chain['cwe2']])
                    # cwe1_equip_cve = cwe1_cve_set & set(equip_cve);
                    # cwe2_equip_cve = cwe2_cve_set & set(equip_cve)
                    #判断cwe链中CWE的是否与ics有关，如存在ics1与ics2对应包含CWE1与CWE2，添加相应实例
                    cwe1_cwe2_ics = [set(),set()]
                    for ics in equip_ics:
                        ics_relate_cwe= [i['ics_relate_cwe'] for i in icsinfo[ics]['ics_vul']]
                        if (cwe_chain['cwe1'] in ics_relate_cwe ):
                            cwe1_cwe2_ics[0].add(ics)
                        if (cwe_chain['cwe2'] in ics_relate_cwe ):
                            cwe1_cwe2_ics[1].add(ics)
                    cwe_chain['instance'] = cwe1_cwe2_ics
                    tabeldict['cwechain'].append(cwe_chain)
                    ics_instancelist=list(cwe1_cwe2_ics[0]|cwe1_cwe2_ics[1])
                    for ics_instance in ics_instancelist:
                        tuplelist.append([['cwe_chain', {'name': cwe_chain_name}], 'has_instance',
                                          ['ics_id', {'name': ics_instance}]])
            # cwe信息添加
            tabeldict['cwe'] = {}
            for cwe in equip_cwe:
                try:
                    tabeldict['cwe'][cwe] = cweinfo[cwe]
                except:
                    tabeldict['cwe'][cwe]=[]
            if (len(tabeldict['cwechain']) > 0):
                tabeldict['baseflag'] = 2
            else:
                tabeldict['baseflag'] = 3
            return tuplelist, tabeldict
        # 两个设备库都不含有该设备，进行other_product查找
        with open("applications/view/sourcedata/other_product0.14.json", encoding='utf-8') as f:
            dict1 = json.load(f)
            f.close()
        if equip in dict1:
            tabeldict['equip'] = equip
            tabeldict['baseflag'] = 3
            # 获得设备影响信息
            equip_cve = dict1[equip]['cve']
            equip_cwe = []
            # ICSA设备处理
            if ('CVE' not in dict1[equip]['cve'][0]):
                with open("applications/view/sourcedata/icscert1.json", encoding='utf-8') as f:
                    icsinfo = json.load(f)
                    f.close()
                for ics in dict1[equip]['cve']:
                    equip_cwe += [i["ics_relate_cwe"] for i in icsinfo[ics]["ics_vul"]]
                # 展示表格添加漏洞信息
                tabeldict['cve'] = {}
                for ics in equip_cve:
                    tabeldict['cve'][ics] = icsinfo[ics]
                # 添加equip-ics-cwe:三元组信息
                for ics in equip_cve:
                    tuplelist.append([['ics_id', {"name": ics}], 'impact_product', ['product', {"name": equip}]])
                    ics_relate_cwe = [i['ics_relate_cwe'] for i in icsinfo[ics]['ics_vul']]
                    for cwe in ics_relate_cwe:
                        if (cwe not in equip_cwe):
                            continue
                        tuplelist.append([['ics_id', {"name": ics}], 'relate_cwe', ['cwe_id', {"name": cwe}]])
                with open("applications/view/sourcedata/cweinfo.json", encoding='utf-8') as f:
                    cweinfo = json.load(f)
                    f.close()
                # cwe信息添加
                tabeldict['cwe'] = {}
                for cwe in equip_cwe:
                    try:
                        tabeldict['cwe'][cwe] = cweinfo[cwe]
                    except:
                        tabeldict['cwe'][cwe] = []
            else:
                with open("applications/view/sourcedata/cve_relate_cwe.json", encoding='utf-8') as f:
                    dict_cwe = json.load(f)
                    f.close()
                for cve in equip_cve:
                    equip_cwe += dict_cwe[cve]
                # 对展示表格添加漏洞信息
                with open("applications/view/sourcedata/cveinfo_tabel.json", encoding='utf-8') as f:
                    cveinfo_tabel = json.load(f)
                    f.close()
                tabeldict['cve'] = {}
                for cve in equip_cve:
                    tabeldict['cve'][cve] = cveinfo_tabel[cve]
                # 添加equip-cve-cwe:三元组信息
                for cve in equip_cve:
                    tuplelist.append([['cve_id', {"name": cve}], 'impact_product', ['product', {"name": equip}]])
                    for cwe in dict_cwe[cve]:
                        tuplelist.append([['cve_id', {"name": cve}], 'instance_of', ['cwe_id', {"name": cwe}]])
                # cwe信息添加
                with open("applications/view/sourcedata/cweinfo.json", encoding='utf-8') as f:
                    cweinfo = json.load(f)
                    f.close()
                tabeldict['cwe'] = {}
                for cwe in equip_cwe:
                    tabeldict['cwe'][cwe] = cweinfo[cwe]
            return tuplelist, tabeldict
    except:
        # 错误的输入
        tabeldict['baseflag'] = 4
        return tuplelist, tabeldict
    # 错误的输入
    tabeldict['baseflag'] = 4
    return tuplelist, tabeldict
