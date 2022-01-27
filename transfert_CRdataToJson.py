# -*- coding: utf-8 -*-

"""
Created 2019/10/01

    regexFile = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['regexFile'], separator=';', typeFile='regex')
@author: David BAUDOIN

fonction : script de transfert d'information compris dans les CR present dans I2B2 vers redcap

"""

import os, pprint, argparse
import Script.importCRcovid19
from Script.readCSVFile import lecture_csv_file
from Script.rihdoRegex import RihdoRegex
from Script.readTexteFile import Read
from Script.output_formatcovid19 import output_format
from Script.data_comparison import apply_comparison_data

def setup(dic_db_param, dic_config):
    # 1) import des CR
    dic_listCR = Script.importCRcovid19.setup(dic_config)
    print(dic_listCR)

    # 2) recuperation du format des CR et de la liste de regex
    ## 2.1) recuperation des info present dans fichier formatFile dans dic_meta
    infoFormat = Read(dic_config['path_to_config'] + dic_config['formatFile'])

    ## 2.2) recuperation de l'ensemble des regex present de le regexFile  du dic_meta
    regexFile = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['regexFile'], separator=';', typeFile='regex')
    regexFormat = lecture_csv_file(filename=dic_config['path_to_config'] + dic_config['regexFormat'], separator=';', typeFile='regex')
    # pprint.pprint(regexFile.dic_data)

    ## 2.3) creation de l'objet de gestion des regex preparation du dic_data
    regex_exe = RihdoRegex(infoFormat=infoFormat, dic_regex=regexFile.dic_data, dic_format=regexFormat.dic_data)

    # 3) recherche des information dans chaque CRs

    # 3.1) preparation (de l'|des)output(s) attendu(s) (redcap, csv, json, brat ...)
    output = output_format(dic_db_param, dic_config)

    for info_CR in dic_listCR:
        # 3.2) application de la recherche
        #print(info_CR['CR'])
        ### 3.2.1) appliquer la decoupe du fichier en fonction des regex FORMAT qu'on appellera rubrique
        dic_format = regex_exe.applyRegexToText(texte=info_CR['CR'], format='FORMAT', num_base=0)
        dic_format_bis = regex_exe.findRubricSize(dic_data=dic_format, texte=info_CR['CR'])
        #pprint.pprint(info_CR)
        pprint.pprint(dic_format_bis)
        #print(info_CR['CR'][dic_format_bis['TECHNIQUE'][0]['position'][0]:dic_format_bis['TECHNIQUE'][0]['end_position']])
        output.current_patient=info_CR['patient']
        output.id_CR=info_CR['num_CR'].replace('/', '')
        output.start_date=info_CR['start_date']
        output.dic_data={}

        ### 3.2.2) pour chaque rubrique : appliquer l'ensemble des regex attachee a la rubrique
        for format in dic_format_bis:
            if dic_format_bis[format] != None:
                #print(format)
                #print(info_CR['CR'][dic_format_bis[format][0]['position'][0]:dic_format_bis[format][0]['end_position']])
                output.dic_data[format] = regex_exe.applyRegexToText(texte=info_CR['CR'][dic_format_bis[format][0]['position'][0]:dic_format_bis[format][0]['end_position']].replace('\n', ' '),
                                                                    format=format,
                                                                    num_base=dic_format_bis[format][0]['position'][0])
            #print(format)
            #pprint.pprint(output.dic_data)

        ### 3.2.3) optionnel si les donnees sont deja presents en sortie redcap : comparaison ou non des valeur + choix de la valeur gardee
        if 'check_redcap_data' in dic_config and dic_config['check_redcap_data'] != '':
            apply_comparison_data(output.dic_data, {}, dic_config['check_redcap_data'])

        #3.3) enregistrement des resultat si condition respectees
        if output.iscsv: output.addDataToCsvDev()
        if output.isjson: output.addDataToJson(output.id_CR)
        if output.isann: output.addAnnfile(output.id_CR, info_CR['CR'])
        if output.issql: output.addDataToSqlTable()

    # 4 fermeture des fichiers + envoi
    output.send()


def main(directory, cr, import_date):
    dic_config = {}
    dic_config['path'] = os.getcwd()
    dic_config['path_to_config'] = dic_config['path'] + '/'+ directory #'config_anapath/'
    dic_config['pathToCR'] = cr
    if not dic_config['path_to_config'].endswith("/"):
        dic_config['path_to_config'] = dic_config['path_to_config']+"/"

    f_param = open(dic_config['path_to_config'] + 'param_config', 'r')
    for line in f_param:
        if len(line)>1 and '=' in line and line[0] != '#':
            dic_config[line.split('=')[0]] = line.split('=')[1].replace('\n', '')

    # DB parameters
    dic_db_param = {}
    f_db_config = open(dic_config['path_to_config'] + dic_config['db_param_file'], 'r')
    for line in f_db_config:
        dic_db_param[line.split('=')[0]] = line.split('=')[1].replace('\n', '')

    #search_redcap_data(dic_db_param['api_url'], dic_db_param['api_key'])
    if import_date != "" :
        dic_config['db_import_date'] = import_date
    setup(dic_db_param, dic_config)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="input folder")
    parser.add_argument("--cr", help="path to CR")
    parser.add_argument("--import_date", help="the most anterior date for import")
    args = parser.parse_args()
    if args.directory:
        print("Go with the inputFolder")
        main(args.directory, args.cr, args.import_date)
