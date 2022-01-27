# -*- coding: utf-8 -*-
"""
Created 2018/01/05

@author: David BAUDOIN

fonction : script d'interaction avec la base de donnees i2b2

"""

import psycopg2
#import cx_Oracle as cx

class db_interaction:

    # construction de l'objet
    def __init__(self, dic_db_param):
        self.type_connection = dic_db_param['DB_type']
        self.DB_host = dic_db_param['DB_host']
        self.DB_name = dic_db_param['DB_name']
        self.DB_port = dic_db_param['DB_port']
        self.DB_user = dic_db_param['DB_user']
        self.DB_password = dic_db_param['DB_password']
        self.dbcon = None

    def connect_i2b2(self):
        if self.type_connection.lower() == 'postgresql':
            config = 'host=' + self.DB_host + ' port=' + self.DB_port + ' dbname=' + self.DB_name + ' user=' + self.DB_user + ' password=' + self.DB_password
            self.dbcon = psycopg2.connect(config)
            cur = self.dbcon.cursor()
            return cur

        #elif self.type_connection.lower() == 'oracle':
        #    dsn = cx.makedsn(self.DB_host, self.DB_port, sid='CDWEGP')
        #    self.dbcon = cx.connect(user=self.DB_user, password=self.DB_password, dsn=dsn, encoding='UTF-8')
        #    cur = self.dbcon.cursor()
        #    return cur

        return None

    def table_request(self, request):
        cursor = self.connect_i2b2()
        cursor.execute(request.encode('utf-8'))
        self.dbcon.commit()
        cursor.close()
    

    def executeBasicRequest(self, request_i2b2, number_of_var=1):
        # return a dictionary :
        # dic[concept1] = [(key1, value11, ...), (key2, value21, ...), ...]
        res = []
        cursor = self.connect_i2b2()
        cursor.execute(request_i2b2.encode('utf-8'))
        for row in cursor:
            tuple_resp = []
            for i in range(0, number_of_var):
                tuple_resp.append(str(row[i]))
            res.append(tuple_resp)
        cursor.close()
        return res

    def insert_data(self, request_i2b2, values):
        cursor = self.connect_i2b2()
        cursor.execute(request_i2b2.encode('utf-8'), values)
        cursor.close()

    def executeBasicRequestWithDate(self, request_i2b2):
        res = [];resp_patient=[]
        cursor = self.connect_i2b2()
        print(request_i2b2.encode('utf-8'))
        cursor.execute(request_i2b2.encode('utf-8'))
        # return a dictionary :
        # dic[concept1] = [(patient24, value24), (patient30, value30), (patient30, value31), ...]
        for row in cursor:
            if str(row[0]) not in resp_patient:
                resp_patient.append(str(row[0]))
                res.append((str(row[0]), str(row[1])))
        cursor.close()
        return res

    def executeDrogRequest(self, request_i2b2):
        cursor = self.connect_i2b2()
        cursor.execute(request_i2b2.encode('utf-8'))
        dic_row = []
        for row in cursor:
            dic_row.append(row)
        return dic_row


    def executeRequest(self, request_i2b2):
        # return a dictionary :
        # dic[concept1] = [(key1, value11, ...), (key2, value21, ...), ...]
        res = []
        cursor = self.connect_i2b2()
        cursor.execute(request_i2b2.encode('utf-8'))
        field_names = [i[0] for i in cursor.description]
        for row in cursor:
            dic_resp = {}
            for i in range(0, len(field_names)):
                dic_resp[field_names[i].lower()]=str(row[i])
            res.append(dic_resp)
        cursor.close()
        return res

    def search_all_column_name(self, request):
        cursor = self.connect_i2b2()
        cursor.execute(request.encode('utf-8'))
        col_names = [row[0] for row in cursor.description]
        return col_names

    def executeBDAction(self, request):
        cursor = self.connect_i2b2()
        cursor.execute(request.encode('utf-8'))
        self.dbcon.commit()
        try:
            return cursor.rowcount
        except:
            return 'request done without rowcount'
