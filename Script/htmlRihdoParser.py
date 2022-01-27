# -*- coding: utf-8 -*-
"""
Created 2019/02/25

@author: David BAUDOIN

objet : parsing du fichier html
    recuperer tous les tableau

"""

from html.parser import HTMLParser
from Script.readCSVFile import lecture_csv_file
import re

class RidhoHTMLParser(HTMLParser):
    # Initializing lists
    lsStartTags = list()
    lsEndTags = list()
    lsData = list()
    lsHtmlTable = {};inHtmlTable=False;inHtmlNewLigne=False;inHtmlNewData=False
    temporarListData=[];temporarData='';titleTable='';dic_tableName={}
    iListTable = 0
    balNewTitle = False

    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        self.lsStartTags.append(tag)
        if tag.strip() == 'b': self.balNewTitle = True
        if tag.strip() == 'u' and self.balNewTitle:
            self.titleTable=''
        if tag.strip() == 'table':
            self.inHtmlTable=True
            if self.titleTable == '': self.titleTable = str(self.iListTable)
            self.lsHtmlTable[self.titleTable] = []
        if tag.strip() == 'tr':
            self.inHtmlNewLigne=True
            if self.temporarListData != []:
                self.lsHtmlTable[self.titleTable].append(self.temporarListData)
            self.temporarListData = []
        if tag.strip() == 'td':
            self.inHtmlNewData = True
            if self.temporarData != '':
                self.temporarListData.append(self.temporarData)
            self.temporarData = ''

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        self.lsEndTags.append(tag)
        if tag.strip() == 'b': self.balNewTitle = False
        if tag.strip() == 'table':
            self.inHtmlTable=False
            self.iListTable+=1
            self.titleTable=''
        if tag.strip() == 'tr':
            self.inHtmlNewLigne=False
            self.lsHtmlTable[self.titleTable].append(self.temporarListData)
            self.temporarListData = []
        if tag.strip() == 'td':
            self.inHtmlNewData = False
            self.temporarListData.append(self.temporarData)
            self.temporarData = ''

    def handle_data(self, data):
        #print("Encountered some data  :", data)

        if self.inHtmlTable:
            #self.temporarData +=data
            self.temporarData += self.clear_data(data)
        else:
            self.lsData.append(self.clear_data(data))
            self.searchTableNameToData(data)

    def clear_data(self, dataToClear):
        # suppr extra ' '
        dataToClear=re.sub('\s+',' ', dataToClear)
        # suppr ' ' between 0 000
        if re.search('^( *\d{1,3} *){2,}$', dataToClear):
            dataToClear=dataToClear.replace(' ', '')
        return dataToClear

    def format_date(self, dateToFormat):
        newDate = ''

        return newDate

    def listTableTitle(self, listTableFile):
        f_tableName=lecture_csv_file(filename=listTableFile, separator=';')
        self.dic_tableName=f_tableName.dic_data

    def searchTableNameToData(self, data):
        i=0
        for table_name in self.dic_tableName['table_name']:
            match_name=re.search(self.dic_tableName['regex'][i], data)
            if match_name != None:
                self.titleTable = table_name
                break
            i+=1
