# -*- coding: utf-8 -*-
"""
Created 2019/02/10

@author: David BAUDOIN

objet : formatage des tableau tel qu'il est attendu dans i2b2

"""
import re
from Script.dateFormat import rihdoDate

class i2b2Format:
    # construction de l'objet
    def __init__(self, dic_typeTable, dateFile, patient='0', visit='0', dateInit=''):
        self.dic_data = []
        self.idPatient = patient
        self.idVisit = visit
        self.dic_typeTable = self.interpreterTable(dic_typeTable)
        self.dateToFormat = rihdoDate(dateFile)
        self.idDateInit = self.dateToFormat.searchAndTransformDate(dateInit)
        print(self.idDateInit)

    def addNewObservation(self, dataEntry):
        if str(dataEntry['tval_char']) != '' and str(dataEntry['tval_char']) is not None:
            obs = {}
            obs['patient_num'] = str(self.idPatient)
            obs['encounter_num'] = str(self.idVisit)
            if 'startDate' in dataEntry:
                obs['start_date'] = str(dataEntry['startDate'])
            else: obs['start_date'] = str(self.idDateInit)
            obs['concept_cd'] = str(dataEntry['concept_cd'])
            obs['modifier_cd'] = str(dataEntry['modifier_cd'])
            obs['instance_num'] = str(dataEntry['instance_num'])
            obs['tval_char'] = str(dataEntry['tval_char'])
            obs['location_cd'] = str(dataEntry['location_cd'])
            obs['units_cd'] = str(dataEntry['units_cd'])
            obs['provider_id'] = dataEntry['provider_id']
            #obs['nval_num'] = dataEntry['nval_num']

            self.dic_data.append(obs)

    def readNewObs(self, dataTable, nameTable, provider='@'):
        if nameTable in self.dic_typeTable.keys():
            dataEntry={}
            dataEntry['location_cd'] = nameTable
            dataEntry['provider_id'] = provider
            if self.dic_typeTable[nameTable]['modifier_cd']:
                modifier_list = dataTable[nameTable][0]
                for data in dataTable[nameTable][self.dic_typeTable[nameTable]['begin']:]:
                    dataEntry = {}
                    dataEntry['provider_id'] = provider
                    dataEntry['location_cd'] = nameTable
                    dataEntry['concept_cd'] = data[self.dic_typeTable[nameTable]['concept_cd']]
                    dataEntry['startDate'] = self.idDateInit
                    i=1
                    for subData in data[1:]:
                        varUnit = self.separateVarToUnits(modifier_list[i])
                        dataEntry['modifier_cd'] = varUnit[0]
                        dataEntry['units_cd'] = varUnit[1]
                        dataEntry['tval_char'] = subData
                        dataEntry['instance_num'] = 1
                        self.addNewObservation(dataEntry)
                        i += 1
            elif self.dic_typeTable[nameTable]['startDate']:
                startDate_list = dataTable[nameTable][0]
                for data in dataTable[nameTable][self.dic_typeTable[nameTable]['begin']:]:
                    dataEntry = {}
                    dataEntry['provider_id'] = provider
                    varUnit = self.separateVarToUnits(data[self.dic_typeTable[nameTable]['concept_cd']])
                    dataEntry['location_cd'] = nameTable
                    dataEntry['concept_cd'] = varUnit[0]
                    dataEntry['units_cd'] = varUnit[1]
                    dataEntry['modifier_cd'] = '@'
                    i=1
                    for subData in data[1:]:
                        dataEntry['startDate'] = self.dateToFormat.searchAndTransformDate(startDate_list[i])
                        #dataEntry['startDate'] = startDate_list[i]
                        dataEntry['tval_char'] = subData
                        dataEntry['instance_num'] = 1
                        self.addNewObservation(dataEntry)
                        i += 1
            else:
                for data in dataTable[nameTable]:
                    dataEntry = {}
                    dataEntry['provider_id'] = provider
                    dataEntry['location_cd'] = nameTable
                    varUnit = self.separateVarToUnits(data[self.dic_typeTable[nameTable]['concept_cd']])
                    dataEntry['concept_cd'] = varUnit[0]
                    dataEntry['units_cd'] = varUnit[1]
                    try:
                        dataEntry['tval_char'] = data[self.dic_typeTable[nameTable]['value']]
                    except:
                        dataEntry['tval_char'] = None
                        print('WARNING : ' + dataEntry['concept_cd'] + ' has no value in table ' + nameTable)
                    dataEntry['startDate'] = self.idDateInit
                    dataEntry['modifier_cd'] = '@'
                    dataEntry['instance_num'] = 1
                    self.addNewObservation(dataEntry)

    def interpreterTable(self, dic_typeTable):
        i=0;dic_res={}
        for nameTable in dic_typeTable['table_name']:
            typeTable=dic_typeTable['table_type'][i]
            dic_res[nameTable] = {}
            if typeTable == 'conceptValue':
                dic_res[nameTable]['size'] = 2
                dic_res[nameTable]['concept_cd'] = 0
                dic_res[nameTable]['value'] = 1
                dic_res[nameTable]['begin'] = 0
                dic_res[nameTable]['modifier_cd'] = False
                dic_res[nameTable]['startDate'] = False
            elif typeTable == 'conceptModifierValue':
                dic_res[nameTable]['concept_cd'] = 0
                dic_res[nameTable]['value'] = 1
                dic_res[nameTable]['begin'] = 1
                dic_res[nameTable]['modifier_cd'] = True
                dic_res[nameTable]['startDate'] = False
            elif typeTable == 'conceptStartdateValue':
                dic_res[nameTable]['concept_cd'] = 0
                dic_res[nameTable]['value'] = 1
                dic_res[nameTable]['begin'] = 1
                dic_res[nameTable]['modifier_cd'] = False
                dic_res[nameTable]['startDate'] = True
            i+=1
        return dic_res

    def separateVarToUnits(self, data):
        unitPresent = re.findall('\(.*\)', data)
        var = data
        unit = ''
        if unitPresent:
            unit = unitPresent[0]
            varmatch = re.findall('^[^(]*\(', data)
            var = varmatch[0][:-1].strip()
        return (var, unit)
