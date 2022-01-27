# -*- coding: utf-8 -*-
"""
Created 2019/01/05

@author: David BAUDOIN

fonction : lecture des fichiers textes recuperation en differentes formes :
    string
    tableau de ligne

"""
class Read:

    # construction de l'objet
    def __init__(self, texte_file):
        self.texte_file = texte_file
        self.tab_line = []
        self.texte = ''
        self.read_file()

    def read_file(self, PRESERVE_LENGTH=False):
        #print(self.texte_file)
        filetxt = open(self.texte_file, 'r', encoding='utf-8')
        texte_bis = ''
        for line in filetxt:
            if(PRESERVE_LENGTH):
                self.tab_line.append(line.replace('\n', ' '))
            else: 
                self.tab_line.append(line.replace('\n', ''))
            texte_bis += line
        self.texte = str(texte_bis)
        filetxt.close()
