# -*- coding: utf-8 -*-
"""
Created 2018/01/05

@author: David BAUDOIN

fonction : script d'interaction avec la base de donnees i2b2

"""


class I2B2Request:

    # construction de l'objet
    def __init__(self, file_infoPatient, file_infoProvider,file_infoVisit):
        self.dic_infoPatient = self.tanslateConfigToDic(file_infoPatient)
        self.dic_infoProvider = self.tanslateConfigToDic(file_infoProvider)
        self.dic_infoVisit = self.tanslateConfigToDic(file_infoVisit)


    def tanslateConfigToDic(self, configFile):
        dic_config = {}
        fileConfig = open(configFile, 'r')

        fileConfig.close()
        return dic_config
