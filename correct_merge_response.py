# -*- coding: utf-8 -*-
"""
Created 2019/06/05

@author: David BAUDOIN

fonction : script de transformation des donnees reccueil en fonction des regles

"""
import re, pprint, unidecode

class CR_response:
    def __init__(self, dic_data, dic_rules, dateToFormat):
        self.listVar = []
        self.listVarRestriction = []
        self.dic_priority = self.create_dic_priority(dic_data)
        self.dic_rules = self.create_dic_rules(dic_rules)
        self.dateToFormat = dateToFormat
        #pprint.pprint(self.dic_priority)

    def fctSortDict(self, value):
        #pprint.pprint(value['priority'])
        return value['priority']

    def create_dic_priority(self, dic_data):
        dic_priority = {}; i=0
        for f_var in dic_data['columnName']:
            if f_var not in dic_priority:
                self.listVar.append(f_var)
                self.listVarRestriction.append((f_var, dic_data['restriction'][i]))
                dic_priority[f_var] = []
            dic_priority[f_var].append({'priority': dic_data['priority'][i], 'restriction': dic_data['restriction'][i],
                                        'regexVar': dic_data['regexVar'][i], 'rubrique': dic_data['rubrique'][i]})
            i+=1
        #for f_var in dic_priority: dic_priority[f_var] = sorted(dic_priority[f_var], key=self.fctSortDict, reverse=False)
        #pprint.pprint(dic_data['priority'])
        return dic_priority

    def create_dic_rules(self, dic_rules):
        dic_res = {};i = 0
        for rules in dic_rules['regexVar']:
            if rules not in dic_res:
                dic_res[rules] = []
            dic_res[rules].append((dic_rules['motif'][i], dic_rules['changeTo'][i]))
            i += 1
        return dic_res

    def send_value(self, dic_value, var1):
        #pprint.pprint(dic_value)
        for var in self.dic_priority[var1]:
            #print('mark :' + var['regexVar'])
            if var['rubrique'] in dic_value and var['regexVar'] in dic_value[var['rubrique']]:
                #print('check 1')
                if dic_value[var['rubrique']][var['regexVar']][0]['result'] != '':
                    if dic_value[var['rubrique']][var['regexVar']][0]['multiple']: # variable True False
                        return self.send_all_values(var['regexVar'], dic_value[var['rubrique']][var['regexVar']])
                    #print('check 2')
                    #print(self.correct_value(var['regexVar'], dic_value[var['rubrique']][var['regexVar']][0]['result']))
                    #pprint.pprint(var)
                    #print('previous value: ' + dic_value[var['rubrique']][var['regexVar']][0]['result'])
                    #print('corrected value: ' + self.correct_value(var['regexVar'], dic_value[var['rubrique']][var['regexVar']][0]['result']))
                    return self.correct_value(var['regexVar'], dic_value[var['rubrique']][var['regexVar']][0]['result'])
        return ''
    
    def send_all_values(self, regexVar, list_regexRes):
        result_list = []
        #result_string = ''
        for match in list_regexRes:
            result_list.append(str(self.correct_value(regexVar, match['result'])))
            #result_string += str(self.correct_value(regexVar, match['result']))
            #result_string += ', '
        #return result_string[:-2]
        result_list = set(result_list)
        result_string = str(result_list)
        result_string = result_string.replace('{', '')
        result_string = result_string.replace('}', '')
        result_string = result_string.replace("'", '')
        return result_string

    def correct_value(self, var, value):
        corrected_value = value
        if corrected_value == None: return ''
        if var in self.dic_rules:
            for correct in self.dic_rules[var]:
                print (var + ' : ' + value)
                #corrected_value = corrected_value.replace(correct[0], correct[1])
                if correct[0] == 'date':
                    #print('correct date ' + str(corrected_value))
                    corrected_value = self.dateToFormat.searchAndTransformRedcapDate(corrected_value)
                if correct[0] == 'strtoupper':
                    corrected_value = unidecode.unidecode(corrected_value) # removes accents
                    corrected_value = corrected_value.upper()
                else:
                    #print('correct a value : '+ corrected_value + ' with the pattern : '+correct[0] + ' change to : ' +  correct[1])
                    corrected_value = re.sub(correct[0], correct[1], corrected_value)
        #print('final value : ' + corrected_value)
        return corrected_value
