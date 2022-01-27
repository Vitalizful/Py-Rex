# -*- coding: utf-8 -*-
"""
Created 2019/03/05

@author: David BAUDOIN

objet : date
    a partir d'un string definir tous les informations via une liste de regex
    et renvoyer une date avec un format voulu (on utilise le datetime)

"""
from datetime import datetime
from Script.readCSVFile import lecture_csv_file
import re, pprint
class rihdoDate:
    # construction de l'objet
    def __init__(self, fileDateConfig):
        self.DateConfig = self.enumerateRegexList(fileDateConfig)
        self.dateR = {}
        self.isDate = False
        self.monthValue = (
        'janvier', 'jan', 'février', 'fevrier', 'fév', 'fev', 'mars', 'avril', 'avr', 'mai', 'juin', 'juillet', 'juil',
        'aout', 'août', 'septembre', 'sep', 'sept', 'octobre', 'oct', 'novembre', 'nov', 'décembre', 'decembre', 'déc',
        'dec')
        self.monthCor = (
        '01', '01', '02', '02', '02', '02', '03', '04', '04', '05', '06', '07', '07',
        '08', '08', '09', '09', '09', '10', '10', '11', '11', '12', '12', '12',
        '12')

    def enumerateRegexList(self, fileDateConfig):
        regexFile = lecture_csv_file(filename=fileDateConfig, separator=';')
        return regexFile.dic_data

    def searchDateFormat(self, date):
        i=0
        #print(date)
        for regexDate in self.DateConfig['regex']:
            resRegex = re.search(regexDate, date.lower())
            if resRegex != None:
                #print(regexDate)
                #print('year group = ' + self.DateConfig['year'][i] + ' month group = ' + self.DateConfig['month'][i] + ' day group = ' + self.DateConfig['day'][i])
                self.isDate = True
                self.dateR['year']=resRegex.group(int(self.DateConfig['year'][i]))
                self.dateR['month'] = resRegex.group(int(self.DateConfig['month'][i]))
                if self.DateConfig['day'][i] != '': self.dateR['day'] = resRegex.group(int(self.DateConfig['day'][i]))
                else: self.dateR['day'] = 1
                break
            i+=1

    def getDate(self):
        #print(str(self.dateR['day']) + '/' + str(self.dateR['month']) + '/' + str(self.dateR['year']))
        return datetime(year=int(self.dateR['year']),
                        month=int(self.dateR['month']),
                        day=int(self.dateR['day']))

    def get_redcapDate(self):
        return str(self.dateR['year']) + '-' + str(self.dateR['month']) + '-' + str(self.dateR['day'])
    
    def translateMonth(self, data):
        i=0
        for month in self.monthValue:
            if data == month.lower(): return self.monthCor[i]
            i+=1
        return data

    def checkYear(self):
        #pprint.pprint(self.dateR)
        if len(str(self.dateR['year']))==2:
            #print('20' + str(self.dateR['year']))
            return '20' + str(self.dateR['year'])
        elif len(str(self.dateR['year']))==4:
            return str(self.dateR['year'])
    
    def checkMonth(self):
        if len(str(self.dateR['month']))==1:
            #print("mark1")
            #print('Date corrigée ' + '0' + str(self.dateR['month']))
            return '0' + str(self.dateR['month'])
        elif len(str(self.dateR['month']))==2:
            #print("mark2")
            return str(self.dateR['month'])
        
    def checkDay(self):
        if 'day' in self.dateR :
            if len(str(self.dateR['day']))==1:
                #print('0' + str(self.dateR['day']))
                return '0' + str(self.dateR['day'])
            elif len(str(self.dateR['day']))==2:
                return str(self.dateR['day'])
        return '01'

    def searchAndTransformDate(self, date):
        self.dateR = {}
        self.searchDateFormat(date)
        if self.isDate:
            self.dateR['year'] = self.checkYear()
            self.dateR['month'] = self.translateMonth(self.dateR['month'])
            self.dateR['month'] = self.checkMonth()
            return self.get_redcapDate()
        else:
            return None

    def searchAndTransformRedcapDate(self, date):
        self.dateR = {}
        self.searchDateFormat(date)
        if self.isDate:
            self.dateR['year'] = self.checkYear()
            self.dateR['month'] = self.translateMonth(self.dateR['month'])
            self.dateR['month'] = self.checkMonth()
            self.dateR['day'] = self.checkDay()
            return self.get_redcapDate()
        else:
            return date


