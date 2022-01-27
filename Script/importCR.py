# -*- coding: utf-8 -*-
"""
Created 2019/10/01

@author: David BAUDOIN

fonction : importation des CR depuis differents type
    de la DB I2B2
    d'un ou de plusieurs dossier present sur la machine ou ailleur
    d'un seul fichier de type CSV

output: renvoi un dictionnaire ordonnees sur patient puis start_date de la forme

dic_CR {[patient_num = ...
         num_CR = ...
         start_date = ...
         CR = ...

"""
from Script.SQLexecution import i2b2_interaction
from redcap import Project
from scp import SCPClient
import paramiko, datetime, io

def setup(dic_db_param, dic_config):
    list_CRs = []
    # 1) cas 1 import sql
    if dic_config['type_import'] == 'sql':
        # 1 recherche des compte rendus dans i2b2 et transfert dans un fichier temp
        i2b2Interac = i2b2_interaction(dic_db_param)
        patient_selected = ''
        if 'patient_selected' in dic_db_param and dic_db_param['patient_selected'] == 'redcap':
            ## recherche dans le projet redcap les patients selectionne
            project = Project(dic_db_param['api_url'], dic_db_param['api_key'], verify_ssl=False)
            response = project.export_records(fields=['record_id'])
            break_line = 0
            patient_selected = '('
            for rep in response:
                patient_selected += rep['record_id'] + ', '
                if break_line % 5 == 0:
                    patient_selected += '\n'
                break_line += 1
            if break_line % 5 != 1:
                patient_selected = patient_selected[:-2] + ')'
            else:
                patient_selected = patient_selected[:-3] + ')'

        ## 1.2 recherche des CR correspondants
        #request = open(dic_config['path_to_config'] + dic_config['i2b2_request_file'], 'r+').read().replace('$s', dic_config['i2b2_patient_table'])
        request = open(dic_config['path_to_config'] + dic_config['i2b2_request_file'], 'r+').read()
        i2b2_response = i2b2Interac.executeBasicRequest(request, 4)

        # 1.3 creation du dictionnaire
        for i2b2_response_line in i2b2_response:
            dic_CR = {}
            dic_CR['patient'] = i2b2_response_line[0]
            dic_CR['num_CR'] = i2b2_response_line[1]
            dic_CR['start_date'] = i2b2_response_line[2]
            dic_CR['CR'] = i2b2_response_line[3]
            list_CRs.append(dic_CR)

    elif dic_config['type_import'] == 'scp':
        sshConnection = paramiko.SSHClient()
        sshConnection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshConnection.connect(dic_config['scp_host'], username=dic_config['scp_user'],
                              password=dic_config['scp_password'])
        ssh_stdin_bam, ssh_coverageAnalysis_stdout_bam, ssh_stderr_bam = sshConnection.exec_command(
            'find ' + dic_config['scp_repertory'] + ' -name "*.txt"')
        scp = SCPClient(sshConnection.get_transport())
        list_CRs = []

        for bamfile in ssh_coverageAnalysis_stdout_bam.readlines():
            user = bamfile[:-1].split('/')[-1][:-4]
            CR_current = bamfile[:-1]
            start_date = ''
            scp.get(CR_current, dic_config['path_to_result'] + '/current.txt')
            observation_blob = open(dic_config['path_to_result'] + '/current.txt', 'r+').read()

            return_txtfile = open(dic_config['path_to_result'] + '/current.txt', 'w')
            return_txtfile.write(bytes(observation_blob, 'utf8').decode('utf8'))
            return_txtfile.close()
            scp.put(dic_config['path_to_result'] + '/current.txt', CR_current)

            # print(user + ' : ' + str(len(observation_blob)))
            list_CRs.append([user, CR_current, start_date, observation_blob])

    elif dic_config['type_import'] == 'txt':
        list_CRs = []
        dic_CR = {}
        #print('type import txt used')
        dic_CR['patient'] = 'current'
        dic_CR['num_CR'] = dic_config['num_CR']
        dic_CR['start_date'] = str(datetime.date.today().strftime("%d/%m/%Y"))
        dic_CR['CR'] = io.open(dic_config['pathToCR'], mode='r+', encoding="utf-8").read()
        list_CRs.append(dic_CR)
    return list_CRs
