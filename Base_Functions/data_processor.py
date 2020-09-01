
'''This file holds all relevant functions necessary for starting the data analysis.
An object class for all account data is established, which will hold the raw data after import,
the processed data and all subdata configuration necessary for plotting. If desired credit data is also integrated. 
Currently it is only working for the banks listed in acc_testscript. Further work towards integrating other banks will be done. Excel file is exported at the end.'''


from Base_Functions import acc_testscript
import numpy as np
import pandas as pd
import platform
import datetime
import locale
import os
import re


if platform.system()=='Windows':
    locale.setlocale(locale.LC_ALL, '')
    folder_sep='\\'
else:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    folder_sep='/'
parent_dir=os.getcwd()#parent directory for classification table on both systems



dateparser_capy = lambda x: datetime.datetime.strptime(x, "%d.%m.%Y")
dateparser_lowy= lambda x: datetime.datetime.strptime(x, "%d.%m.%y")


class Classifier:

    def __init__(self):
    #parent_dir=os.path.abspath(os.getcwd()+'/..')
        self.dict_giro=pd.read_excel(parent_dir+folder_sep+'Zuordnungstabelle.xlsx',engine='openpyxl',sheet_name='Girokonto',index_col=0)['Kategorie'].to_dict()
        self.dict_credit=pd.read_excel(parent_dir+folder_sep+'Zuordnungstabelle.xlsx',engine='openpyxl',sheet_name='Kreditkarte',index_col=0)['Kategorie'].to_dict()

    ## data categorizer. dictionaries are used to get keys to search for and corresponding categories
    def categorizer(self,dicttype,string):
        
        if dicttype=='credit':
            dictuse=self.dict_credit
        else:
            dictuse=self.dict_giro

        for key in dictuse.keys():
            if re.findall(key,string):
                return dictuse[key]
        else:
            return 'Sonstiges'

    def categorize_data(self,dicttype,data):
        data["lowtext"]=data['text'].apply(lambda text: ''.join(text.lower().split()))  ## create auxiliary column with scanable text
        data["cat"]=data['lowtext'].apply(lambda text: self.categorizer(dicttype,text))  ## do categorization
        data.drop("lowtext",axis=1,inplace=True)                                        ## get rid of auxiliary column
        
        return data


class Accounts_Data:

    def __init__(self,folder_raw,classtable):

        self.imported_files=[]
        self.folder_sep=folder_sep       
        self.folder_raw=folder_raw+folder_sep
        self.folder_res={}
        self.raw_data={}
        self.raw_data_header={}
        self.basis_data={}
        self.month_data={}
        self.cat_data={}
        self.plotting_list={}
        self.error_codes={}
        self.classifier=classtable
       

    def process_data(self,raw_fileinfo,import_type):
        
        #unpack tuple with fileinformation
        filename,filepath=raw_fileinfo
        
        ##read in csv-files from different account_types
        
        ##start functions for getting csv account type info and data input & adjustment
        if import_type=='csv_analyse':

            #get account information
            while True:
                try:
                    account_infos,raw_data,acc_infotype=acc_testscript.account_info_identifier(filepath)
                except:
                    self.error_codes[filename]='Err01'
                    break
                ##unpack account read-in info tuple
                header_columns,column_join,column_drop,catdict_type,cat_adjust,plot_info=account_infos

                self.raw_data[filename]=raw_data
                self.raw_data_header[filename]=header_columns
                
                #data preprocess
                try:
                    #select Euro entrys
                    if "Währung" in header_columns:
                        self.basis_data[filename]=self.raw_data[filename][self.raw_data[filename]["Währung"]=="EUR"].copy()
                    else:
                        self.basis_data[filename]=self.raw_data[filename].copy()

                    ##do text adjustment for categorization
                    if column_join[0]=='yes':
                        self.basis_data[filename]['text'] = self.basis_data[filename][self.basis_data[filename].columns[column_join[1]]].apply(lambda x: ' || '.join(x.dropna()),axis=1)
                    else:
                        pass

                    ##drop columns if necessary and reaarange columns
                    if column_drop[0]=='yes':
                        self.basis_data[filename].drop(self.basis_data[filename].columns[column_drop[1]],axis=1,inplace=True)
                        self.basis_data[filename]=self.basis_data[filename].reindex(columns=self.basis_data[filename].columns[column_drop[2]])
                    else:
                        pass

                    ##insert "act" column if necessary (currently only dkb_credit)
                    if len(self.basis_data[filename].columns)==4:
                        self.basis_data[filename].insert(2,'act',pd.Series())
                    else:
                        pass

                    self.basis_data[filename].columns=["time1","time2","act","text","val"]

                    #delete row with time1&time2 empty
                    self.basis_data[filename]=self.basis_data[filename].drop(self.basis_data[filename][(self.basis_data[filename]['time1'].isna()==True)&(self.basis_data[filename]['time2'].isna()==True)].index)
                    
                    #adjust for missing time values in "tiem1"-columns
                    self.basis_data[filename]['time1'].mask(self.basis_data[filename]['time1'].isna(),self.basis_data[filename]['time2'],inplace=True) ##new
                    #make month-column and categorize
                    self.basis_data[filename]['month']=self.basis_data[filename]['time1'].apply(lambda dates: dates.strftime('%b %Y'))
                
                except:
                    self.error_codes[filename]='Err02'
                    break
                #try categorization else give error code
                try:
                    self.basis_data[filename]=self.classifier.categorize_data(catdict_type,self.basis_data[filename])
                except:
                    self.error_codes[filename]='Err03'
                    break
                ##readjust categories for better understanding when comparing with different account types
                if cat_adjust[0]=='yes':
                    self.basis_data[filename].loc[self.basis_data[filename]['cat']==cat_adjust[1],'cat']=cat_adjust[2]
                else:
                    pass

                #add variables for subsequent handling and plotting
                self.plotting_list[filename]=plot_info
                self.imported_files.append(filename)
                self.folder_res[filename]=self.folder_raw+'Ergebnisse'+self.folder_sep+filename
                break

        # Excel file for concatenation
        elif import_type=='xls_longterm':

            #Longterm analysis: Read-in excel to concat csvs
            try:
                raw_data=pd.read_excel(filepath,sheet_name='Aufbereitete Daten', engine='openpyxl')
                raw_data.columns=["time1","time2","act","text","val",'month','cat']
                if raw_data.isnull().values.any()==False:
                    self.basis_data[filename]=raw_data.copy()
                else:
                    self.error_codes[filename]='Err01'
            except:
                self.error_codes[filename]='Err01'

           
        #Plot manually manipulated excel files
        elif import_type=='xls_analyse':

            #read excel
            try:
                raw_data=pd.read_excel(filepath,sheet_name='Aufbereitete Daten', engine='openpyxl')
                raw_data.columns=["time1","time2","act","text","val",'month','cat']
                #filter for empty values
                if raw_data.isnull().values.any()==False:
                    self.basis_data[filename]=raw_data.copy()
                    self.plotting_list[filename]=""
                    self.imported_files.append(filename)
                    self.folder_res[filename]=self.folder_raw+'Ergebnisse'+self.folder_sep+filename
                else:
                    self.error_codes[filename]='Err01'
            except:
                self.error_codes[filename]='Err01'



        else:#no action needed
            pass
        
       
    def concatter(self,concat_list):
        
        #create list to find concat choice in datasets
        for item in concat_list:
            #tuple unpack concat choice values
            framename,concat_choice=item
            #get names for new datasets
            concat_dataframes=[]
            for choicename in concat_choice:
                concat_dataframes.append(self.basis_data[choicename])
            #concat and add to data-object
            self.basis_data[framename]=pd.concat(concat_dataframes,ignore_index=True)
            self.basis_data[framename]=self.basis_data[framename].sort_values(['time1'],ascending=False) 
            self.folder_res[framename]=self.folder_raw+'Ergebnisse'+self.folder_sep+framename
            self.plotting_list[framename]=""
    
    
    def bundle_holiday(self):
        #concat holiday data from different csv-files
        
        self.basis_data['Urlaube']=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat"])
        for element_name in self.imported_files:
            data_hol=self.basis_data[element_name].loc[self.basis_data[element_name]['cat'].str.contains('Urlaub')].copy()
            self.basis_data['Urlaube']=self.basis_data['Urlaube'].append(data_hol,ignore_index=True)
        
        if len(self.basis_data['Urlaube'].index)>0:
            self.basis_data['Urlaube']=self.basis_data['Urlaube'].sort_values(['time1'],ascending=False)
            self.folder_res['Urlaube']=self.folder_raw+'Ergebnisse'+self.folder_sep+'Urlaubsauswertung'
            self.plotting_list['Urlaube']='basic'
        else:
            del self.basis_data['Urlaube']

  
    def month_cat_maker(self):
        
        ##categorize data and sort ascending. Same goes for monthly data
        for element_name in list(self.folder_res.keys()):
            if not element_name=='Sparcents':
                basis_data_subset=self.basis_data[element_name].copy()

                #make month data
                self.month_data[element_name]=basis_data_subset.groupby('month',sort=False)['val'].sum().reset_index() ##get monthly overview
                self.month_data[element_name]=self.month_data[element_name][::-1]##sort monthly data starting with first month up respective left in monthplot
                
                #process data and aggregate based on category
                cat_intermediate=basis_data_subset.groupby('cat')['val'].sum().reset_index()
                            
                hilfs=pd.DataFrame([['Gesamtsaldo\nder Periode', sum(basis_data_subset['val'])]],columns=list(cat_intermediate.columns))
                cat_intermediate=cat_intermediate.sort_values(['val'],ascending=False).reset_index(drop=True)
                cat_data=cat_intermediate.loc[(cat_intermediate['val']>0)].copy()

                if len(cat_data.index)>0:
                    cost_data=cat_intermediate[cat_data.index[-1]+1:].copy()
                else:
                    cost_data=cat_intermediate[0:].copy()

                cost_data=cost_data.sort_values(['val'])
                cat_data=cat_data.append(cost_data,ignore_index=True)
                cat_data=cat_data.append(hilfs,ignore_index=True)
                cat_data['val_month']=cat_data['val']/(self.month_data[element_name]['month'].nunique())
                self.cat_data[element_name]=cat_data
    
    
    def savecent_calculation(self):
        #account for difference between actucal cost value and full amount (rounding). Gives a number which can be invested every month. Since the data structure will be different, the results will be saved and plotted separately.

        self.basis_data['Sparcents']=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat","savecent","acc_origin"])
        #get data from every imported csv and do savecent calculation
        for element_name in self.imported_files:
            savecent_subset=self.basis_data[element_name].loc[self.basis_data[element_name]['val']<0].copy()
            savecent_subset['savecent']=np.ceil(savecent_subset['val'].abs())+savecent_subset['val']
            savecent_subset['acc_origin']=element_name
            self.basis_data['Sparcents']=self.basis_data['Sparcents'].append(savecent_subset,ignore_index=True)
        if len( self.basis_data['Sparcents'].index)>0:
            self.basis_data['Sparcents']=self.basis_data['Sparcents'].sort_values(['time1'],ascending=False)
            self.folder_res['Sparcents']=self.folder_raw+'Ergebnisse'+self.folder_sep+'Sparcents'
            self.plotting_list['Sparcents']='basic'

            ## do monthly accumulation and grouping by acc_origin
            #prepare set
            savecent_set=self.basis_data['Sparcents'].copy()
            savecent_set['val']=savecent_set['savecent']
            savecent_set['cat']=savecent_set['acc_origin']
            savecent_set.drop(savecent_set.columns[[7,8]],axis=1,inplace=True)

            #group by month
            self.month_data['Sparcents']=savecent_set.groupby('month',sort=False)['val'].sum().reset_index() ##get monthly overview
            self.month_data['Sparcents']=self.month_data['Sparcents'].sort_values(['val'],ascending=False) ##sort monthly data

            #group by account-origin ("category")

            savecent_cat=savecent_set.groupby('cat',sort=False)['val'].sum().reset_index() ##get monthly overview
            savecent_cat=savecent_cat.sort_values(['val'],ascending=False) ##sort monthly data
            savecent_cat=savecent_cat.append(pd.DataFrame([['Gesamtsumme der\nSparcents',sum(savecent_set['val'])]],columns=list(savecent_cat.columns)),ignore_index=True)
            savecent_cat['val_month']=savecent_cat['val']/(self.month_data['Sparcents']['month'].nunique())
            self.cat_data['Sparcents']=savecent_cat
        else:
            del self.basis_data['Sparcents']


    
    def makefolder_excel(self):
        ## Create folders and export data into excel with several subsheets
        for element_name in list(self.folder_res.keys()):
            result_dir=self.folder_res[element_name]
            try:
                if not os.path.exists(result_dir):
                    os.makedirs(result_dir)
            except OSError:
                print ('Error: Creating directory. ' +  result_dir)
            writer_excel = pd.ExcelWriter(result_dir+self.folder_sep+element_name+'_Auswertung.xlsx', engine='openpyxl',datetime_format="dd.mm.yyyy")

            if element_name in self.raw_data:
                self.raw_data[element_name].to_excel(writer_excel,sheet_name='Rohdaten',index=False,header=self.raw_data_header[element_name])
            else:#no action needed
                pass

            if element_name=='Sparcents':
                self.basis_data[element_name].to_excel(writer_excel,sheet_name='Aufbereitete Daten',index=False,header=["Buchungstag","Wertstellung (Valuta)","Vorgang","Buchungsinformationen","Umsatzbetrag in EUR","Monat","Kategorie","Sparcents in EUR","Herkunft Sparcent"])
                self.month_data[element_name].to_excel(writer_excel,sheet_name="Monatliche Sparcents",index=False,header=["Monat","Sparcents in EUR"])
                self.cat_data[element_name].to_excel(writer_excel,sheet_name='Sparcents nach Konto-Herkunft',index=False,header=["Herkunft Sparcent","Kumulierte Sparcents (€)","Durchschnittliche Sparcents pro Monat (€)"])

            else:
                self.basis_data[element_name].to_excel(writer_excel,sheet_name='Aufbereitete Daten',index=False,header=["Buchungstag","Wertstellung (Valuta)","Vorgang","Buchungsinformationen","Umsatzbetrag in EUR","Monat","Kategorie"])
                self.cat_data[element_name].to_excel(writer_excel,sheet_name='Aufstellung nach Kategorien',index=False,header=["Kategorie","Kumulierte Absolutbeträge (€)","Durchschnittliche Absolutbeträge pro Monat (€)"])
     
            writer_excel.save()
