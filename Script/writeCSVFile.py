# -*- coding: utf-8 -*-
"""
Created 2019/01/27

@author: David BAUDOIN

fonction : script lisant le dictionnaire de resultat et transmettant les resultats dans un fichier csv

"""

class ecriture_csv_file:
    # construction de l'objet
    def __init__(self, filename, separator=',', dic_resultat, config_file=None):
        self.filename = filename
        self.separator = separator
        self.dic_resultat = dic_resultat
        if config_file is not None: self.writeRes(config_file=config_file)

    def writeRes(self, config_file):
        f_csv = open(self.filename, 'w')
        line='compteRendu' + self.separator
        for variable in config_file['columnName']:
            line+=variable + self.separator
        line = line[:-1] + '\n'
        f_csv.write(line)

        for compteRendu in self.dic_resultat:
            line = compteRendu + self.separator
            for variable in config_file['regexVar']:
                result = self.findResValue(compteRendu, variable)
                line += result + self.separator
            line = line[:-1] + '\n'
            f_csv.write(line)

        f_csv.close()

    def addRes(self, config_file, list_compteRendu):
        f_csv = open(self.filename, 'a')

        for compteRendu in list_compteRendu:
            line = compteRendu + self.separator
            for variable in config_file['regexVar']:
                result = self.findResValue(compteRendu, variable)
                line += result + self.separator
            line = line[:-1] + '\n'
            f_csv.write(line)

        f_csv.close()

    def addTitles(self, config_file):
        f_csv = open(self.filename, 'w')

        line = 'compteRendu' + self.separator

        for variable in config_file['columnName']:
            line += variable + self.separator
        line = line[:-1] + '\n'
        f_csv.write(line)

        f_csv.close()

    def findResValue(self, compteRendu, regexVar):
        for rubrique in self.dic_resultat[compteRendu]:
            if self.dic_resultat[compteRendu][rubrique] is not None:
                if regexVar in self.dic_resultat[compteRendu][rubrique]:
                    return self.dic_resultat[compteRendu][rubrique][regexVar][0]['result']
        return ''

    def writeI2b2File(self):
        f_csv = open(self.filename, 'w')
        titleLine = 'patient_num;encounter_num;concept_cd;provider_id;start_date;modifier_cd;instance_num;tval_char;location_cd;units_cd'
        f_csv.write(titleLine)
        f_csv.write('\n')
        for obs in self.dic_resultat:
            line = obs['patient_num'] + self.separator
            line += obs['encounter_num'] + self.separator
            line += obs['concept_cd'] + self.separator
            line += obs['provider_id'] + self.separator
            line += obs['start_date'] + self.separator
            line += obs['modifier_cd'] + self.separator
            line += obs['instance_num'] + self.separator
            line += obs['tval_char'] + self.separator
            line += obs['location_cd'] + self.separator
            line += obs['units_cd'] + self.separator
            f_csv.write(line[:-1])
            f_csv.write('\n')
        f_csv.close()

    def addDataI2b2File(self):
        f_csv = open(self.filename, 'a')
        for obs in self.dic_resultat:
            line = obs['patient_num'] + self.separator
            line += obs['encounter_num'] + self.separator
            line += obs['concept_cd'] + self.separator
            line += obs['provider_id'] + self.separator
            line += obs['start_date'] + self.separator
            line += obs['modifier_cd'] + self.separator
            line += obs['instance_num'] + self.separator
            line += obs['tval_char'] + self.separator
            line += obs['location_cd'] + self.separator
            f_csv.write(line[:-1])
            f_csv.write('\n')
        f_csv.close()
