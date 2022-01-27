# -*- coding: utf-8 -*-

"""
Created 2022/01/18

@author: David BAUDOIN, Valentin POHYER

fonction : script de preparation de la table sql pour extraction de donnees issus des resultats regex

"""

from Script.SQLexecution import db_interaction
import os, pprint, argparse

def setup(dic_db_param, dic_config):
    dbInterac = db_interaction(dic_db_param)
    request = 'DROP TABLE IF EXISTS '+dic_config['resultat.sqltable.name']
    dbInterac.table_request(request)

def main(directory):
    dic_config = {}
    dic_config['path'] = os.getcwd()
    dic_config['path_to_config'] = dic_config['path'] + '/'+ directory #'config_anapath/'
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
        
    setup(dic_db_param, dic_config)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="input folder")
    args = parser.parse_args()
    if args.directory:
        print("Go with the inputFolder")
        main(args.directory)
