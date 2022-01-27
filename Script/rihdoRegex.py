# -*- coding: utf-8 -*-
"""
Created 2019/01/03

@author: David BAUDOIN

fonction : script de de gestion des regex

"""

import re, pprint

class RihdoRegex:
    # construction de l'objet
    def __init__(self, infoFormat, dic_regex, dic_format):
        self.infoFormat = infoFormat
        self.dic_regex = dic_regex
        self.dic_format = dic_format
        self.list_ordreFormat = []
        self.schemaFormat = self.create_schemaFormat
        self.dic_RihdoRegex = self.create_dic_RihdoRegex()
        self.prepareRegex()
        ### rajouter variable insensitive et allmatching et modifier applyRegexToText

    # recuperation de la structure du format de fichier
    @property
    def create_schemaFormat(self):
        schemaFormat = {}
        entry_dic = schemaFormat
        list_parent_entry = []
        currentlevel = 0
        precinfo = ''

        for info in self.infoFormat.tab_line:
            info_level = info.count('-')/3

            if info_level > currentlevel:
                list_parent_entry.append(entry_dic)
                entry_dic = entry_dic[precinfo]
                currentlevel = info_level

            if info_level < currentlevel:
                for i in range(0, int(currentlevel - info_level)):
                    entry_dic = list_parent_entry[-1]
                    del (list_parent_entry[-1])
                currentlevel = info_level

            entry_dic[info[info.count('-'):]] = {}
            self.list_ordreFormat.append((str(info).replace('---', '').replace('\\n', '').replace('\n', ''), int(info.count('-')/3)))
            precinfo = info[info.count('-'):]
        #pprint.pprint(schemaFormat)
        return schemaFormat

    # creation du dictionnaire de regex repertorie en rubrique
    def create_dic_RihdoRegex(self):
        dic_RihdoRegex = {}
        dic_RihdoRegex['ALL'] = []
        dic_RihdoRegex['FORMAT'] = []
        i=0
        for regex_group in self.dic_format['group']:
            dic_RihdoRegex['FORMAT'].append({'name': self.dic_format['name'][i],
                                             #'multiple': self.dic_format['multiple'][i], #dev
                                             'restriction': self.dic_format['restriction'][i],
                                             'regex': self.dic_format['regex'][i],
                                             'cible': self.dic_format['cible'][i]})
            i += 1

        i = 0
        for regex_group in self.dic_regex['group']:
            if regex_group in dic_RihdoRegex:
                #pprint.pprint(self.dic_regex['name'][i])
                #pprint.pprint(self.dic_regex['restriction'][i])
                dic_RihdoRegex[regex_group].append({'name': self.dic_regex['name'][i],
                                                    #'multiple': self.dic_regex['multiple'][i], #dev
                                                    'restriction': self.dic_regex['restriction'][i],
                                                    'regex': self.dic_regex['regex'][i],
                                                    'cible': self.dic_regex['cible'][i]})
            else:
                dic_RihdoRegex[regex_group] = [{'name': self.dic_regex['name'][i],
                                                #'multiple': self.dic_regex['multiple'][i], #dev
                                                'restriction': self.dic_regex['restriction'][i],
                                                'regex': self.dic_regex['regex'][i],
                                                'cible': self.dic_regex['cible'][i]}]
            if regex_group not in ('GENERIC', 'FORMAT'):
                dic_RihdoRegex['ALL'].append({'name': self.dic_regex['name'][i],
                                              #'multiple': self.dic_regex['multiple'][i], #dev
                                              'restriction': self.dic_regex['restriction'][i],
                                              'regex': self.dic_regex['regex'][i],
                                              'cible': self.dic_regex['cible'][i]})
            i+=1
        #pprint.pprint(dic_RihdoRegex)
        return dic_RihdoRegex

    def applyRegexToText(self, texte, format, num_base): 
        if format in self.dic_RihdoRegex:
            dic_result = {}
            for regex in self.dic_RihdoRegex[format]:
                #print("List of regex: " + regex['regex'])
                if 'm' in regex['restriction']:
                    multiple = True
                else:
                    multiple = False
                if  'i' in regex['restriction']:
                    #print(regex['regex'])
                    list_position = re.finditer(regex['regex'], texte, re.IGNORECASE)
                else:
                    list_position = re.finditer(regex['regex'], texte)
                for match in list_position:
                    #print(match.span(), match.group())
                    if regex['name'] not in dic_result.keys(): dic_result[regex['name']] = []
                    if regex['cible'] == '': dic_result[regex['name']].append({'result': match.group(), 'position': (int(match.span()[0])+num_base, int(match.span()[1])+num_base), 'multiple':multiple})
                    else: dic_result[regex['name']].append({'result': match.group(int(regex['cible'])), 'position': (int(match.span(int(regex['cible']))[0])+num_base, int(match.span(int(regex['cible']))[1])+num_base), 'multiple':multiple})
            pprint.pprint(dic_result)
            return dic_result

        else:
            #print('no format match with the data of formatFile')
            return None

    # determiner la bonne position des rubriques
    def findRubricSize(self, dic_data, texte):
        #pprint.pprint(dic_data)
        #pprint.pprint("------------------------")
        #pprint.pprint(self.list_ordreFormat[0][0])
        current = self.list_ordreFormat[0][0]
        posCursor = 0
        #pprint.pprint(self.list_ordreFormat)
        dic_data[current] = [{'result':'HEADER', 'position':(0, 0)}]
        #pprint.pprint(self.list_ordreFormat)
        # partie 1 on determine les end position stricte on en profite pour retirer les mauvais match
        for ordreFormat in self.list_ordreFormat[1:]:
            found = False
            #print("ORDRE FORMAT: "+ str(ordreFormat))
            if ordreFormat[0] in dic_data:
                #print("FOUND IN DIC_DATA")
                i = 0
                pprint.pprint(dic_data[ordreFormat[0]])
                for posEnd in dic_data[ordreFormat[0]]:
                    #print("FIND IN DIC_DATA[ORDRE FORMAT]")
                    #print('pos Cursor : ' + str(posCursor) + ' compare to (<) ' + ordreFormat[0] + ' pos : ' + str(posEnd['position'][0] - 1))
                    if posCursor < posEnd['position'][0]-1:
                        posCursor = int(posEnd['position'][0]) - 1
                        dic_data[current][0]['end_position'] = posCursor
                        current = ordreFormat[0]
                        found = True
                        break
                    else:
                        i += 1
                if not found: dic_data[ordreFormat[0]][0]['end_position'] = len(texte)
                while i > 0 and found:
                    del(dic_data[ordreFormat[0]][0])
                    i -= 1

        dic_data[current][0]['end_position'] = len(texte)
        #pprint.pprint(dic_data)

        # partie 2 verification

        i = 0
        list_paragraphe = []
        list_paragraphe.append(True)
        for ordreFormat in self.list_ordreFormat:
            if ordreFormat[0] in dic_data:
                racine_check = True
            else:
                racine_check = False
            if i == ordreFormat[1]:
                del (list_paragraphe[-1])
            elif i>ordreFormat[1]:
                while i+1 > ordreFormat[1]:
                    del (list_paragraphe[-1])
                    i -= 1
            list_paragraphe.append(racine_check)
            #print(ordreFormat[0])
            #print(list_paragraphe)
            for paragraphe in list_paragraphe:
                if not paragraphe and ordreFormat[0] in dic_data:
                    #print('element supprimee '+ ordreFormat[0])
                    del(dic_data[ordreFormat[0]])
                    break
            i = ordreFormat[1]

        # partie 3 cas paragraphe et sous paragraphe
        i = 0
        list_paragraphe = []
        previous_par = ''
        endPosition = 0
        #pprint.pprint(dic_data)
        for ordreFormat in self.list_ordreFormat:
            if ordreFormat[0] in dic_data:
                #print(ordreFormat[0] + str(dic_data[ordreFormat[0]]))
                endPosition = dic_data[ordreFormat[0]][0]['end_position']
                if len(list_paragraphe) > 0 and dic_data[list_paragraphe[-1]][0]['position'][0] > dic_data[ordreFormat[0]][0]['position'][0]:
                    #print(list_paragraphe[-1] + ' position ' + str(dic_data[list_paragraphe[-1]][0]['position'][0]) + ' > ' + ordreFormat[0] + ' position ' + str(dic_data[ordreFormat[0]][0]['position'][0]))
                    del (dic_data[ordreFormat[0]])
                if i < ordreFormat[1]:
                    list_paragraphe.append(previous_par)

                elif i > ordreFormat[1]:
                    while i > ordreFormat[1]:
                        dic_data[list_paragraphe[-1]][0]['end_position'] = dic_data[ordreFormat[0]][0]['position'][0]
                        del(list_paragraphe[-1])
                        i -= 1
                i = ordreFormat[1]
                previous_par = ordreFormat[0]
            else:
                if i > ordreFormat[1]:
                    while i > ordreFormat[1]:
                        dic_data[list_paragraphe[-1]][0]['end_position'] = endPosition
                        del (list_paragraphe[-1])
                        i -= 1
            #previous_par = ordreFormat[0]
        #print(list_paragraphe)
        for paragraphe in list_paragraphe:
            dic_data[paragraphe][0]['end_position'] = endPosition
            
        #print(dic_data.keys())
        dic_data['ALL'] = list()
        dic_data['ALL'].append({'result':'ALL','position':(0,0),'end_position':len(texte)})
        #pprint.pprint(dic_data)
        return dic_data

    def allElementIsInlist(self, previous_par, elements, list):
        if elements != [] :
            if previous_par not in list: return False
        else :
            for element in elements:
                if element not in list: return False
        return True

    def prepareRegex(self):
        if 'GENERIC' in self.dic_RihdoRegex:
            for genericRegex in self.dic_RihdoRegex['GENERIC']:
                for formatRub in self.dic_RihdoRegex:
                    if formatRub != 'GENERIC':
                        for otherRegex in self.dic_RihdoRegex[formatRub]:
                            otherRegex['regex'] = otherRegex['regex'].replace('$'+genericRegex['name']+'$',genericRegex['regex'])
