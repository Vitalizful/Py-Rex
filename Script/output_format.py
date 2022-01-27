# -*- coding: utf-8 -*-
"""
Created 2019/10/01

@author: David BAUDOIN

fonction : preparation de la sortie attendu


"""
from Script.readCSVFile import lecture_csv_file
from Script.correct_merge_response import CR_response
from Script.dateFormat import rihdoDate
from Script.SQLexecution import db_interaction
import json, pprint, os, shutil, re

class output_format:
    # construction de l'objet
    def __init__(self, dic_db_param, dic_config):
        self.dic_config = dic_config
        self.type_return = dic_config['output_result'].split('+')
        self.previous_data = {}

        # result to treat
        self.dic_data = {}
        self.isRelevantCR = True
        self.current_patient = ''
        self.id_CR = ''
        self.start_date = ''

        #csv param
        self.iscsv = False
        self.res_csv = None
        self.res_csv2 = None

        #ann param
        self.isann = False
        self.outputfolder = ''

        #json param
        self.isjson = False
        
        #db variable
        self.dbInterac = ''
        self.issql = False

        # 0) enregistement des fichiers techniques
        self.listVarInterest = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['listVarRes'], separator=';', typeFile='csv')
        self.dateToFormat = rihdoDate(dic_config['path_to_config'] + dic_config['formatDate'])
        self.listVarInterest = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['listVarRes'], separator=';', typeFile='csv')
        self.listCorAnswer = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['listCorAnswer'], separator=';', typeFile='csv')
        self.obj_corrector = CR_response(self.listVarInterest.dic_data, self.listCorAnswer.dic_data, self.dateToFormat)
        #print(self.listVarInterest.dic_data['columnName'])

        if 'csv' in self.type_return: self.prepare_csv_output()
        if 'ann' in self.type_return: self.prepare_ann_output()
        if 'json' in self.type_return: self.isjson = True
        if 'sql' in self.type_return: self.prepare_db_output(dic_db_param)

    #def prepare_csv_output(self):
    #    self.res_csv = open(self.dic_config['resultat.csv'], 'w')
    #    # dev
    #    self.res_csv2 = open(self.dic_config['resultat.csv'] + 'garder', 'w')
    #    self.res_csv2.write('record_id;CR_instance')
    #    ##################################################
    #    self.res_csv.write('record_id;CR_instance')
    #    for varInterest in self.obj_corrector.listVar:
    #        self.res_csv.write(';')
    #        self.res_csv2.write(';')
    #        if varInterest != '':
    #            self.res_csv.write(varInterest)
    #            self.res_csv2.write(varInterest)
    #            # res_csv.write('\n')
    #    self.iscsv = True

    def prepare_csv_output(self):
        if os.path.exists(self.dic_config['resultat.csv']):
            self.res_csv = open(self.dic_config['resultat.csv'], 'a')
            self.res_csv2 = open(self.dic_config['resultat.csv'] + 'garder', 'a')
        else:
            self.res_csv = open(self.dic_config['resultat.csv'], 'w')
            # dev
            self.res_csv2 = open(self.dic_config['resultat.csv'] + 'garder', 'w')
            self.res_csv2.write('record_id'+self.dic_config['resultatSep']+'CR_instance')
            ##################################################
            self.res_csv.write('record_id'+self.dic_config['resultatSep']+'CR_instance')
            for varInterest in self.obj_corrector.listVar:
                self.res_csv.write(self.dic_config['resultatSep'])
                self.res_csv2.write(self.dic_config['resultatSep'])
                if varInterest != '':
                    self.res_csv.write(varInterest)
                    self.res_csv2.write(varInterest)
                    # res_csv.write('\n')
            #self.res_csv.write(self.dic_config['resultatSep']+'deleted')
        self.iscsv = True
        
    def prepare_ann_output(self):
        self.isann = True
        self.outputfolder = self.dic_config['output_annfile']
        #os.mkdir(self.dic_config['path_to_temporarFile'])

    def prepare_db_output(self, dic_db_param):
        self.dbInterac = db_interaction(dic_db_param)
        # creation de la table correspondante aux resultats de l'extration pyrex
        request_create_result_table = 'CREATE TABLE IF NOT EXISTS '+self.dic_config['resultat.sqltable.name']+'('
        request_create_result_table += 'cr_instance varchar (100), '
        for varInterest in self.obj_corrector.listVar:
            request_create_result_table += varInterest + ' varchar (400), '
        request_create_result_table = request_create_result_table[:-2] + ')'
        self.dbInterac.table_request(request_create_result_table)
        self.issql = True
        
    def addDataToCsv(self):
        self.isRelevantCR = True
        line_res = ''
        line_res += '\n'
        line_res += self.current_patient
        line_res += self.dic_config['resultatSep']
        line_res += self.id_CR
        for varInterest in self.obj_corrector.listVarRestriction:
            if self.current_patient in self.previous_data and varInterest in self.previous_data[self.current_patient] and self.previous_data[self.current_patient][varInterest] != '':
                data = self.previous_data[self.current_patient][varInterest]
            else:
                data = str(self.obj_corrector.send_value(self.dic_data, varInterest[0]))
            if varInterest[1] == 'O' and data == '':
                self.isRelevantCR = False
                break
            line_res += self.dic_config['resultatSep']
            line_res += data
        if self.isRelevantCR: self.res_csv.write(line_res)

    def addDataToCsvDev(self):
        self.isRelevantCR = True
        line_res = ''
        self.res_csv.write('\n')
        line_res += '\n'
        self.res_csv.write(self.current_patient)
        line_res += self.current_patient

        self.res_csv.write(self.dic_config['resultatSep'])
        line_res += self.dic_config['resultatSep']
        self.res_csv.write(self.id_CR)
        line_res += self.id_CR

        #pprint.pprint(self.dic_data)
        for varInterest in self.obj_corrector.listVarRestriction:
            #print("Var interest: {} | {}".format(varInterest[0], varInterest[1]))
            if self.current_patient in self.previous_data and varInterest in self.previous_data[self.current_patient] and self.previous_data[self.current_patient][varInterest] != '':
                data = self.previous_data[self.current_patient][varInterest]
                #print("Mark 1")
            elif varInterest[1] == 'start_date':
                data = self.start_date[0:10]
                #print("Mark 2")
            else:
                data = str(self.obj_corrector.send_value(self.dic_data, varInterest[0]))
                #print("Mark 3")
            #print(data)
            self.res_csv.write(self.dic_config['resultatSep'])
            line_res += self.dic_config['resultatSep']
            data_quoted = data
            if(len(data)>0):
                data_quoted = "\"" + data_quoted + "\""
            self.res_csv.write(data_quoted)
            line_res += data_quoted
            if varInterest[1] == 'O' and data == '': self.isRelevantCR = False
        if self.isRelevantCR:
            self.res_csv2.write(line_res)
        #else:
            #self.res_csv.write(self.dic_config['resultatSep']+'data deleted')

    def addAnnfile(self, id_cr, texte):
        f_brat = open(self.dic_config['output_annfile'] + str(id_cr) + '.ann', 'w')
        instance_brat = 0
        
        #### regex et compteur de retour chariot ### Problem Solved
        #liste_retour_chariot =[]
        #regex_res = re.finditer('\n', texte)
        #i=1
        #for match in regex_res:
        #    liste_retour_chariot.append((i, int(match.span()[0])))
        #    i+=1
        #print (liste_retour_chariot)
        ###

        for format in self.dic_data:
            if self.dic_data[format] != None:
                for result in self.dic_data[format]:
                    if self.dic_data[format][result] != None:
                        for dic_result in self.dic_data[format][result]:
                            position_debut = dic_result['position'][0]
                            postion_fin = dic_result['position'][1]
                            
                            ### comparaison avec la liste de retour chariot ### Problem Solved
                            #nb_rc = 0
                            #for retour_chariot in liste_retour_chariot :
                            #    if position_debut < retour_chariot[1]:
                            #        break
                            #    nb_rc = retour_chariot[0]
                            #position_debut += nb_rc
                            #for retour_chariot in liste_retour_chariot[nb_rc:] :
                            #    if postion_fin < retour_chariot[1]+1:
                            #        break
                            #    nb_rc = retour_chariot[0]
                            #postion_fin += nb_rc
                            ###
                            
                            bratline = 'T' + str(instance_brat) + '	' + result + ' ' + str(position_debut) \
                                       + ' ' + str(postion_fin) + '	' + str(dic_result['result'])
                            instance_brat += 1
                            f_brat.write(bratline)
                            f_brat.write('\n')
        f_brat.close()
        
        # Create a new .txt file with utf-8 encoding to resolve the encoding problem with brat
        f_txt = open(self.dic_config['output_annfile'] + str(id_cr) + '.txt', 'w')
        f_txt.write(bytes(texte, 'utf8').decode('utf-8'))
        f_txt.close()
        

    def addDataToJson(self, id_cr):
        f = open(self.dic_config['path_to_result'] + id_cr + '.json', 'w')
        f.write(str(self.dic_data))
        f.close()

    def addDataToSqlTable(self):
        request_add_values = 'insert into '+ self.dic_config['resultat.sqltable.name']+ '('
        request_add_values += 'cr_instance, '
        for varInterest in self.obj_corrector.listVar:
            request_add_values += varInterest + ', '
        request_add_values = request_add_values[:-2] + ') VALUES ('
        request_add_values += '\'' + self.id_CR + '\', '
        for varInterest in self.obj_corrector.listVarRestriction:
            if self.current_patient in self.previous_data and varInterest in self.previous_data[self.current_patient] and self.previous_data[self.current_patient][varInterest] != '':
                data = self.previous_data[self.current_patient][varInterest]
                #print("Mark 1")
            elif varInterest[1] == 'start_date':
                data = self.start_date[0:10]
                #print("Mark 2")
            else:
                data = str(self.obj_corrector.send_value(self.dic_data, varInterest[0]))
                #print("Mark 3")
            data_quoted = "\'" + data + "\'"
            request_add_values += data_quoted + ', '
        request_add_values = request_add_values[:-2] + ')'
        self.dbInterac.table_request(request_add_values)
        
        
    def send(self):
        if self.iscsv:
            print(self.dic_config['resultat.csv'])
            self.res_csv.close()
            self.res_csv2.close()
            print('cvs file done')

#         if self.isann:
#             for file in os.listdir(self.dic_config['path_to_temporarFile']):
#                 wholePath = self.dic_config['output_annfile']
#                 shutil.copyfile(self.dic_config['path_to_temporarFile'] + file, wholePath + file[11:])
#                 print(file + ' send')

#             shutil.rmtree(self.dic_config['path_to_temporarFile'])
#             print('ann file done')



    def replace_value(self, format, key, value):
        self.dic_data[format][0][key] = value
        print('en cours')
