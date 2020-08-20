
'''This file contains the list (dictionary) necessary for categorizing all booking entries. This dictionary is work in progress.
Feel free to adapt it to your needs '''

import numpy as np
import pandas as pd
import datetime
import re

dict_giro=pd.read_excel('Zuordnungstabelle.xlsx',sheet_name='Girokonto',index_col=0)['Kategorie'].to_dict()
dict_credit=pd.read_excel('Zuordnungstabelle.xlsx',sheet_name='Kreditkarte',index_col=0)['Kategorie'].to_dict()

## data categorizer. dictionaries are used to get keys to search for and corresponding categories
def categorizer(dicttype,string):
	if dicttype=='credit':
		dictuse=dict_credit
	else:
		dictuse=dict_giro

	for key in dictuse.keys():
		if re.findall(key,string):
			return dictuse[key]
	else:
		return 'Sonstiges'

def categorize_data(dicttype,data):
	data["lowtext"]=data['text'].apply(lambda text: ''.join(text.lower().split()))	## create auxiliary column with scanable text
	data["cat"]=data['lowtext'].apply(lambda text: categorizer(dicttype,text))	## do categorization
	data.drop("lowtext",axis=1,inplace=True)										## get rid of auxiliary column
	
	return data