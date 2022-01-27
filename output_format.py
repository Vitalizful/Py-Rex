# -*- coding: utf-8 -*-
"""
Created 2019/10/01

@author: David BAUDOIN

fonction : preparation de la sortie attendu


"""
from Script.readCSVFile import lecture_csv_file
from Script.correct_merge_response import CR_response
from Script.dateFormat import rihdoDate
from redcap import Project
import json, pprint, os, paramiko, shutil
from scp import SCPClient

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

        #redcap param
        self.redcap_data = ''
        self.isredcap = False
        self.previous_patient = ''
        self.redcap_repeat_instance = 1

        #csv param
        self.iscsv = False
        self.res_csv = None
        self.res_csv2 = None

        #ann param
        self.isann = False
        self.outputfolder = ''

        # 0) enregistement des fichiers techniques
        self.listVarInterest = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['listVarRes'], separator=';', typeFile='csv')
        self.dateToFormat = rihdoDate(dic_config['path_to_config'] + dic_config['formatDate'])
        self.listVarInterest = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['listVarRes'], separator=';', typeFile='csv')
        self.listCorAnswer = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['listCorAnswer'], separator=';', typeFile='csv')
        self.obj_corrector = CR_response(self.listVarInterest.dic_data, self.listCorAnswer.dic_data, self.dateToFormat)
        #print(self.listVarInterest.dic_data['columnName'])


        if 'redcap' in self.type_return:
            self.prepare_redcap_output()
            self.download_previous_redcap_data()
        if 'csv' in self.type_return: self.prepare_csv_output()
        if 'ann' in self.type_return: self.prepare_ann_output()

    def prepare_redcap_output(self):
        self.dic_redcap_data = '{'
        self.isredcap = True

    def download_previous_redcap_data(self):
        project = Project(self.dic_config['api_url'], self.dic_config['api_key'], verify_ssl=False)
        self.previous_data = project.export_records(fields=self.listVarInterest.dic_data['columnName'])

    def prepare_csv_output(self):
        self.res_csv = open(self.dic_config['resultat.csv'], 'w')
        # dev
        self.res_csv2 = open(self.dic_config['resultat.csv'] + 'garder', 'w')
        self.res_csv2.write('record_id;CR_instance')
        ##################################################
        self.res_csv.write('record_id;CR_instance')
        for varInterest in self.obj_corrector.listVar:
            self.res_csv.write(';')
            self.res_csv2.write(';')
            if varInterest != '':
                self.res_csv.write(varInterest)
                self.res_csv2.write(varInterest)
                # res_csv.write('\n')
        self.iscsv = True

    def prepare_ann_output(self):
        self.isann = True
        self.outputfolder = self.dic_config['output_annfile']
        os.mkdir(self.dic_config['path_to_temporarFile'])

    def addDataToRedcap(self):
        self.isRelevantCR = True
        list_redcap_data = '{' + '\"record_id\":\"' + self.current_patient + '\"' + ', '

        # gestion des donnees "repeatable"
        if self.dic_config['form_repeatable'] != '':
            list_redcap_data += '\"redcap_repeat_instrument\":\"' + self.dic_config['form_repeatable'] + '\"' + ', '
            if self.previous_patient == self.current_patient:
                self.redcap_repeat_instance += 1
            else:
                self.redcap_repeat_instance = 1
            list_redcap_data += '\"redcap_repeat_instance\":\"' + str(self.redcap_repeat_instance) + '\"' + ', '
        self.previous_patient = self.current_patient

        ### DEV ###
        if 'ref_redcap_cr' in self.dic_config and self.dic_config['ref_redcap_cr'] != '':
            list_redcap_data += '\"'+self.dic_config['ref_redcap_cr']+'\":\"' + self.current_patient[0:4] + '/' + self.current_patient[4:7] + '/' + self.current_patient[7:] + '/' + self.id_CR + '\"' + ', '

        for varInterest in self.obj_corrector.listVarRestriction:
            if self.current_patient in self.previous_data and varInterest in self.previous_data[self.current_patient] and self.previous_data[self.current_patient][varInterest] != '':
                redcap_data = self.previous_data[self.current_patient][varInterest]
            elif varInterest[1] == 'start_date':
                redcap_data = self.start_date[0:10]
            else: redcap_data = str(self.obj_corrector.send_value(self.dic_data, varInterest[0]))
            if varInterest[1] == 'O' and redcap_data == '':
                self.isRelevantCR = False
                break
            if varInterest[0] != '':
                list_redcap_data += '\"' + varInterest[0] + '\":\"' + redcap_data + '\"' + ', '

        list_redcap_data = list_redcap_data[:-2] + '}, '
        if self.isRelevantCR: self.redcap_data += list_redcap_data
        else: self.redcap_repeat_instance -= 1

    def addDataToCsv(self):
        self.isRelevantCR = True
        line_res = ''
        line_res += '\n'
        line_res += self.current_patient
        line_res += ';'
        line_res += self.id_CR
        for varInterest in self.obj_corrector.listVarRestriction:
            if self.current_patient in self.previous_data and varInterest in self.previous_data[self.current_patient] and self.previous_data[self.current_patient][varInterest] != '':
                data = self.previous_data[self.current_patient][varInterest]
            else:
                data = str(self.obj_corrector.send_value(self.dic_data, varInterest[0]))
            if varInterest[1] == 'O' and data == '':
                self.isRelevantCR = False
                break
            line_res += ';'
            line_res += data
        if self.isRelevantCR: self.res_csv.write(line_res)

    def addDataToCsvDev(self):
        self.isRelevantCR = True
        line_res = ''
        self.res_csv.write('\n')
        line_res += '\n'
        self.res_csv.write(self.current_patient)
        line_res += self.current_patient

        self.res_csv.write(';')
        line_res += ';'
        self.res_csv.write(self.id_CR)
        line_res += self.id_CR
        for varInterest in self.obj_corrector.listVarRestriction:
            if self.current_patient in self.previous_data and varInterest in self.previous_data[self.current_patient] and self.previous_data[self.current_patient][varInterest] != '':
                data = self.previous_data[self.current_patient][varInterest]
            elif varInterest[1] == 'start_date':
                data = self.start_date[0:10]
            else:
                data = str(self.obj_corrector.send_value(self.dic_data, varInterest[0]))
            self.res_csv.write(';')
            line_res += ';'
            self.res_csv.write(data)
            line_res += data
            if varInterest[1] == 'O' and data == '': self.isRelevantCR = False
        if self.isRelevantCR:
            self.res_csv2.write(line_res)
        #else:
            #self.res_csv.write('data deleted')

    def addAnnfile(self, id_cr):
        f_brat = open(self.dic_config['path_to_temporarFile'] + str(id_cr) + '.ann', 'w')
        instance_brat = 0
        for format in self.dic_data:
            if self.dic_data[format] != None:
                for result in self.dic_data[format]:
                    if self.dic_data[format][result] != None:
                        for dic_result in self.dic_data[format][result]:
                            bratline = 'T' + str(instance_brat) + '	' + result + ' ' + str(dic_result['position'][0]) \
                                       + ' ' + str(dic_result['position'][1]) + '	' + str(dic_result['result'])
                            instance_brat += 1
                            f_brat.write(bratline)
                            f_brat.write('\n')
        f_brat.close()

    def send(self):
        if self.iscsv:
            print(self.dic_config['resultat.csv'])
            self.res_csv.close()
            self.res_csv2.close()
            print('cvs file done')

        if self.isredcap:
            json_data3 = json.loads('['+self.redcap_data[:-2]+']')
            project = Project(self.dic_config['api_url'], self.dic_config['api_key'], verify_ssl=False)
            print('['+self.redcap_data[:-2]+']')
            response = project.import_records(json_data3)
            print(response)
            print('redcap transfert done')

        if self.isann:
            sshConnection = paramiko.SSHClient()
            sshConnection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshConnection.connect(self.dic_config['scp_host'], username=self.dic_config['scp_user'],password=self.dic_config['scp_password'])
            scp_cursor = SCPClient(sshConnection.get_transport())

            for file in os.listdir(self.dic_config['path_to_temporarFile']):
                wholePath = self.dic_config['output_annfile']
                folders = [str(file.split('_')[0])[0:4], str(file.split('_')[0])[4:7], str(file.split('_')[0])[7:]]
                for thisPath in folders:
                    wholePath = wholePath + thisPath + "/"
                scp_cursor.put(self.dic_config['path_to_temporarFile'] + file, wholePath + file[11:])
                print(file + ' send')

            shutil.rmtree(self.dic_config['path_to_temporarFile'])
            print('ann file done')

    def replace_value(self, format, key, value):
        self.dic_data[format][0][key] = value
        print('en cours')
