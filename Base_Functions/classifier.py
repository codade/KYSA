'''Classification class. Import of respective classification excel file is accomplished through user process call.
Accounts Data class accesses categorization functions. Every single data point in the respective "text" column of the imported files is 
matched via regex check against existing values in classification table and the category returned. If no entry is found "other" is returned.
Classification table can be altered by user. Hardcoded category dictionary is only changeable through future updates.'''


import pandas as pd
import platform

import locale
import re


if platform.system()=='Windows':
    locale.setlocale(locale.LC_ALL, 'German')
    folder_sep='\\'
elif platform.system()=='Darwin':
    locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
    folder_sep='/'
else:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    folder_sep='/'

#_______________________________________ Hardcoded classifications dictionaries for second classification loop _______________________________________

hardcoded_classdicts={'lang_deu':{'dict_giro':{
 'ikeadeutschland': 'Anschaffungen',
 'conrad': 'Anschaffungen'.
 'obisagtdanke': 'Anschaffungen',
 'dbvertrieb': 'Bahnfahrten \nohne S-Bahn',
 'bahnticket': 'Bahnfahrten \nohne S-Bahn',
 'dkbvisacard': 'DKB-\nKreditkarte',
 'bvg-ticket-app': 'Nahverkehr\nBerlin',
 'berlinerverkehrsbetriebe': 'Nahverkehr\nBerlin',
 'mvgautomat': 'Nahverkehr\nMünchen',
 's-bahn-berlin': 'Nahverkehr\nBerlin',
 's-bahn-muenchen': 'Nahverkehr\nMünchen',
 'dmdrogeriemarkt': 'Drogerie'},
 'dict_credit':{'dbbahna-nr': 'Bahnfahrten \nohne Sbahn',
 'summemonatsabrechnungvisa': 'Comdirect VISA-\nKreditkarte'}},
 'lang_eng':{'dict_giro':{'withdrawal':'Cash payment',
 'savingsplan':'ETF /\ninvestment saving',
 'sharenumber':'share\ntransaction',
 'vodafone':'cell phone',
 'bookingnumber': 'holidays in XXX'},
 'dict_credit':{'berlin':'cash payments\nin Berlin'}
}}



#_______________________________________ Classifier class and import changeable classification table _______________________________________

class Classifier:

    def __init__(self,class_dir,langdict):
    #parent_dir=os.path.abspath(os.getcwd()+'/..')
        self.langdict=langdict

        #change locale if english was selected as language
        if self.langdict['tablename'][0]=='Classification_Table.xlsx':
            
            self.lang='lang_eng'

            if platform.system()=='Windows': #adjust locale if language choice is english
                locale.setlocale(locale.LC_ALL, 'English')
            elif platform.system()=='Darwin':
                locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
            else:
                locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        else:
            self.lang='lang_deu'
        
        class_path=class_dir+folder_sep+self.langdict['tablename'][0]
        self.dict_giro=pd.read_excel(class_path,engine='openpyxl',sheet_name=self.langdict['tablesheets'][0],index_col=0)[self.langdict['tablename'][1]].dropna().to_dict() #drop Nan-values and transform into dictionary
        self.dict_credit=pd.read_excel(class_path,engine='openpyxl',sheet_name=self.langdict['tablesheets'][1],index_col=0)[self.langdict['tablename'][1]].dropna().to_dict() #drop Nan-values and transform into dictionary
        
    ## data categorizer. dictionaries are used to get keys to search for and corresponding categories
    def categorizer(self,dicttype,string):
        
        if dicttype=='credit':
            dictuse_first=self.dict_credit
            dictuse_second=hardcoded_classdicts[self.lang]['dict_credit']
        else:
            dictuse_first=self.dict_giro
            dictuse_second=hardcoded_classdicts[self.lang]['dict_giro']

        #first loop
        for key in dictuse_first.keys():
            if re.findall(key,string):#'string' value is the string value in the 'text' column in one row. 'key' refers to the search word in this context
                return dictuse_first[key] # if search word ('key') was found in string, return the corresponding category
        
        #second loop with values where no value was found in users classification table
        else:
            for key in dictuse_second.keys():
                if re.findall(key,string):#'string' value is the string value in the 'text' column in one row. 'key' refers to the search word in this context
                    return dictuse_second[key]

            return self.langdict['noncategory'][0]#return 'other' value, if nothing was found

    def categorize_data(self,dicttype,data):
        data["lowtext"]=data['text'].apply(lambda text: ''.join(text.lower().split()))  ## create auxiliary column with scanable text
        data["cat"]=data['lowtext'].apply(lambda text: self.categorizer(dicttype,text))  ## do categorization
        data.drop("lowtext",axis=1,inplace=True)                                        ## get rid of auxiliary column
        
        return data
