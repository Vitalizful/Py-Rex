# -*- coding: utf-8 -*-
"""
Created 2019/11/25

@author: David BAUDOIN

fonction : data update

"""

def apply_comparison_data(dic_data_find, dic_data_init, type_comparison):
    print ('en_cours')

def search_redcap_data(api_url, api_key):
    from redcap import Project
    project = Project(api_url, api_key, verify_ssl=False)
    #to_import = [{'record': 'foo', 'test_score': 'bar'}]
    data = project.export_records()

