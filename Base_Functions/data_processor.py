
'''This file holds all relevant functions necessary for starting the data analysis.
An object class for all account data is established, which will hold the raw data after import,
the processed data and all subdata configuration necessary for plotting. 
The account data is provided through the account identification process in account_ident.py
Necessary functions for holiday extraction, roundies calculation as well as merging and cashbook linkage are provided in the Accounts class
Excel file is exported at the end exported.'''


from Base_Functions import account_ident
import numpy as np
import pandas as pd
import platform
import datetime
import locale
import os
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
    



class Accounts_Data:

    def __init__(self,res_dir,classifier_class,langdict):

        self.langdict=langdict

        ## set language variable
        if self.langdict['result_pathvars'][0]=='Ergebnisse_':
            self.lang_choice='deu'
        else:
            self.lang_choice='eng'
            #change locale to English
            if platform.system()=='Windows':
                locale.setlocale(locale.LC_ALL, 'English')
            elif platform.system()=='Darwin':
                locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
            else:
                locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        
        self.current_date=datetime.datetime.now().strftime("%b'%y")
        self.imported_csv_acctypes={}
        self.folder_sep=folder_sep       
        self.res_dir=res_dir+folder_sep+self.langdict['result_pathvars'][0]+self.current_date+self.folder_sep #adjusted complete path
        self.folder_res={}
        self.raw_data={}
        self.raw_data_header={}
        self.basis_data={}
        self.month_data={}
        self.cat_data={}
        self.plotting_list={}
        self.error_codes={}
        self.classifier=classifier_class


            
        

    def process_data(self,raw_fileinfo,import_type):
        
        #unpack tuple with fileinformation
        filename,filepath=raw_fileinfo
        
        ##read in csv-files from different account_types
        
        ##start functions for getting csv account type info and data input & adjustment
        if import_type=='csv_analyse':

            #get account information
            while True:
                try:
                    account_infos,raw_data,acctype=account_ident.account_info_identifier(filepath,self.lang_choice)
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
                    elif "currency" in header_columns:# 
                        self.basis_data[filename]=self.raw_data[filename][self.raw_data[filename]["currency"]=="EUR"].copy()
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
                        self.basis_data[filename].insert(2,'act',self.langdict['act_value'][0])
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
                self.imported_csv_acctypes[filename]=acctype
                self.folder_res[filename]=self.res_dir+filename
                break

           
        #Plot manually manipulated excel files
        elif import_type=='xls_analyse':

            #read excel
            try:
                raw_data=pd.read_excel(filepath,sheet_name=self.langdict['sheetname_basis'][0], engine='openpyxl')
                raw_data.columns=["time1","time2","act","text","val",'month','cat']
                raw_data.dropna(subset=['time1','val'],inplace=True)
                
                #check if dataframe is empty: If yes skip else proceed
                if len(raw_data)!=0:
                    self.basis_data[filename]=raw_data.copy()
                    self.plotting_list[filename]=""
                    self.folder_res[filename]=self.res_dir+filename
                else:
                    self.error_codes[filename]='Err01'
            except:
                self.error_codes[filename]='Err01'

              # Excel file for concatenation
        elif import_type=='xls_longterm':

            #Longterm analysis: Read-in excel to concat csvs
            try:
                raw_data=pd.read_excel(filepath,sheet_name=self.langdict['sheetname_basis'][0], engine='openpyxl')
                raw_data.columns=["time1","time2","act","text","val",'month','cat']
                raw_data.dropna(subset=['time1','val'],inplace=True)
                
                #check if dataframe is empty: If yes skip else proceed
                if len(raw_data)!=0:
                    self.basis_data[filename]=raw_data.copy()
                else:
                    self.error_codes[filename]='Err01'
            except:
                self.error_codes[filename]='Err01'

              # Excel file for concatenation
        
        elif import_type=='xls_cashbook':

            #cashbok analysis: Read-in to append info to csvs
            try:
                raw_data=pd.read_excel(filepath,sheet_name=self.langdict['cashbookvars_name'][0],usecols=[0,1,2,3,4,5], engine='openpyxl')
                raw_data.columns=["time1","text","val","cat","acctype","cashcat"]
                raw_data=raw_data[raw_data['time1'].isna()==False]
                #adjust categories if no value is set    
                raw_data['cat']=raw_data[["text",'cat']].apply(lambda dataitem: self.classifier.categorizer('giro',''.join(dataitem['text'].lower().split())) if dataitem['cat'] is np.nan else dataitem['cat'],axis=1)
                
                if raw_data.isnull().values.any()==False:#reject cashbook if there are empty values
                    
                    raw_data['val']=-raw_data['val']
                    raw_data["time2"]=raw_data["time1"]
                    raw_data['month']=raw_data['time1'].apply(lambda dates: dates.strftime('%b %Y'))
                    raw_data['act']=self.langdict['cashbookvars_name'][1]
                    raw_data=raw_data.reindex(columns=raw_data.columns[[0,6,8,1,2,7,3,4,5]])
                    self.basis_data[self.langdict['cashbookvars_name'][0]]=raw_data.copy()
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
            self.basis_data[framename]=pd.concat(concat_dataframes)
            self.basis_data[framename].drop_duplicates(inplace=True,ignore_index=True)#get rid of doubled entry rows
            self.basis_data[framename]=self.basis_data[framename].sort_values(['time1'],ascending=False) 
            self.folder_res[framename]=self.res_dir+framename
            self.plotting_list[framename]=""
    
    
    def bundle_holiday(self):
        #concat holiday data from different csv-files
        holidayvar_name=self.langdict['holidayvars_name'][0]
        self.basis_data[holidayvar_name]=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat"])
        for element_name in list(self.folder_res.keys()):
            if not (element_name==self.langdict['dataname_savecent'][0] or element_name==self.langdict['cashbookvars_name'][0]): #cashbook and savecentnames
                data_hol=self.basis_data[element_name].loc[self.basis_data[element_name]['cat'].str.contains(self.langdict['holiday_searchwords'][0])].copy()
                self.basis_data[holidayvar_name]=self.basis_data[holidayvar_name].append(data_hol,ignore_index=True)
        
        if len(self.basis_data[holidayvar_name].index)>0:
            self.basis_data[holidayvar_name]=self.basis_data[holidayvar_name].sort_values(['time1'],ascending=False)
            self.folder_res[holidayvar_name]=self.res_dir+self.langdict['holidayvars_name'][1]
            self.plotting_list[holidayvar_name]='basic'
        else:
            del self.basis_data[holidayvar_name]

  
    def month_cat_maker(self):
        
        ##categorize data and sort ascending. Same goes for monthly data
        for element_name in list(self.folder_res.keys()):
            if not (element_name==self.langdict['dataname_savecent'][0] or element_name==self.langdict['cashbookvars_name'][0]): #cashbook and savecent names
                basis_data_subset=self.basis_data[element_name].copy()

                #make month data
                self.month_data[element_name]=basis_data_subset.groupby('month',sort=False)['val'].sum().reset_index() ##get monthly overview
                self.month_data[element_name]=self.month_data[element_name][::-1]##sort monthly data starting with first month up respective left in monthplot
                
                #process data and aggregate based on category
                cat_intermediate=basis_data_subset.groupby('cat')['val'].sum().reset_index()
                            
                hilfs=pd.DataFrame([[self.langdict['balance_normal'][0], sum(basis_data_subset['val'])]],columns=list(cat_intermediate.columns))
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
        savecentvar_name=self.langdict['dataname_savecent'][0]
        self.basis_data[savecentvar_name]=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat","savecent","acc_origin"])
        #get data from every imported csv and do savecent calculation
        for element_name in list(self.folder_res.keys()):
            if not (element_name==self.langdict['holidayvars_name'][0] or element_name==self.langdict['cashbookvars_name'][0]): #cashbook and holiday names
                savecent_subset=self.basis_data[element_name].loc[self.basis_data[element_name]['val']<0].copy()
                savecent_subset['savecent']=np.ceil(savecent_subset['val'].abs())+savecent_subset['val']
                savecent_subset['acc_origin']=element_name
                self.basis_data[savecentvar_name]=self.basis_data[savecentvar_name].append(savecent_subset,ignore_index=True)

        if len(self.basis_data[savecentvar_name].index)>0:
            self.basis_data[savecentvar_name]=self.basis_data[savecentvar_name].sort_values(['time1'],ascending=False)
            self.folder_res[savecentvar_name]=self.res_dir+savecentvar_name
            self.plotting_list[savecentvar_name]='basic'

            ## do monthly accumulation and grouping by acc_origin
            #prepare set
            savecent_set=self.basis_data[savecentvar_name].copy()
            savecent_set['val']=savecent_set['savecent']
            savecent_set['cat']=savecent_set['acc_origin']
            savecent_set.drop(savecent_set.columns[[7,8]],axis=1,inplace=True)

            #group by month
            self.month_data[savecentvar_name]=savecent_set.groupby('month',sort=False)['val'].sum().reset_index() ##get monthly overview
            self.month_data[savecentvar_name]=self.month_data[savecentvar_name].sort_values(['val'],ascending=False) ##sort monthly data

            #group by account-origin ("category")

            savecent_cat=savecent_set.groupby('cat',sort=False)['val'].sum().reset_index() ##get monthly overview
            savecent_cat=savecent_cat.sort_values(['val'],ascending=False) ##sort monthly data
            savecent_cat=savecent_cat.append(pd.DataFrame([[self.langdict['balance_savecent'][0],sum(savecent_set['val'])]],columns=list(savecent_cat.columns)),ignore_index=True)
            savecent_cat['val_month']=savecent_cat['val']/(self.month_data[savecentvar_name]['month'].nunique())
            self.cat_data[savecentvar_name]=savecent_cat
        else:
            del self.basis_data[savecentvar_name]


    def cashbook_calculation(self):
    #Preparations
        cashbook_name=self.langdict['cashbookvars_name'][0]
        cashbook_subset=self.basis_data[cashbook_name].copy()
        #reformat acctype names for further processing
        accounts_list={"Comdirect Giro":'comdirect_giro',"Comdirect Kredit":'comdirect_credit',"DKB Giro":'dkb_giro',"DKB Kredit":'dkb_credit',"Triodos Giro":'mlp_triodos_giro',"Apobank Giro":'apobank_giro',"Sparkasse Giro":'sparka_giro',"Consorsbank Giro":'consors_giro',"Commerzbank Giro":'commerz_giro',"Deutsche Bank Giro":'deutsche_giro',"MLP Giro":'mlp_triodos_giro'}
        for item in list(accounts_list.keys()):
            cashbook_subset.loc[cashbook_subset['acctype']==item,'acctype']=accounts_list[item]

        cashbook_acctype=list(cashbook_subset["acctype"].unique())
        cashbook_errorlist=[]
        cashbook_successlist=[]
        #check for entries in the cashbook for every imported csv and filter relevant data points (date and cashcat); append if indicated
        for element_name in list(self.imported_csv_acctypes.keys()):
            element_acctype=self.imported_csv_acctypes[element_name]
            #create appendable subframe
            element_cashappend=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat"])
            if element_acctype in cashbook_acctype:#check if there are entries in the cashbook for this file 
                subframe=cashbook_subset[cashbook_subset['acctype']==element_acctype] #get subframe of cashbook corresponding to acctype
                
                #do preparations for data filtering
                cashcat_names_subframe=list(subframe["cashcat"].unique())
                start_date=self.basis_data[element_name]['time1'].iloc[-1]
                end_date=self.basis_data[element_name]['time1'].iloc[0]
                
                #create appendable subframe
                #loop through cash categories and get relevant data points. Set Errorcodes if necessary
                for item in cashcat_names_subframe:
                    if item in list(self.basis_data[element_name]['cat'].unique()):
                        try:
                            subframe_append=subframe[(subframe['cashcat']==item)&(subframe["time1"].between(start_date,end_date))].copy()
                            subframe_append.drop(subframe_append.columns[[7,8]],axis=1,inplace=True)
                            subframe_sum=pd.DataFrame([[subframe_append['time1'].iloc[0],subframe_append['time2'].iloc[0],self.langdict['cashbookvars_name'][1],self.langdict['balance_cashbook'][0],abs(sum(subframe_append['val'])),subframe_append['month'].iloc[0],item]],columns=list(subframe_append.columns))
                            subframe_append=subframe_append.append(subframe_sum,ignore_index=True)
                            element_cashappend= element_cashappend.append(subframe_append,ignore_index=True)
                            cashbook_successlist.append(element_name)
                        except:
                            cashbook_errorlist.append(element_name+' (Err08)')
                    else:
                        cashbook_errorlist.append(element_name+' (Err07)')

            else:
                pass#no action needed when 

                #append cashbook entries to main data frame
            if len(element_cashappend.index)>0:
                self.basis_data[element_name]=self.basis_data[element_name].append(element_cashappend,ignore_index=True)
                self.basis_data[element_name]=self.basis_data[element_name].sort_values('time1',ascending=False).reset_index(drop=True)
                del element_cashappend
            else:
                del element_cashappend


        #prepare cashbook entries for plotting
        #group by month
        #change back acc types:
        self.basis_data[cashbook_name]['val']=-self.basis_data[cashbook_name]['val']
        cashbook_plotsubset=self.basis_data[cashbook_name].copy()
        self.month_data[cashbook_name]=cashbook_plotsubset.groupby('month',sort=False)['val'].sum().reset_index() ##get monthly overview
        self.month_data[cashbook_name]=self.month_data[cashbook_name][::-1] ##sort monthly data

        #create cat data and join it together
        sum_cashbook=cashbook_plotsubset['val'].sum()
        #first categorical subset sorted by categories
        cat4plot_1=cashbook_plotsubset.groupby('cat',sort=False)['val'].sum().abs().reset_index().copy() ##get monthly overview
        cat4plot_1=cat4plot_1.sort_values(['val'],ascending=False) ##sort monthly data
        cat4plot_1=cat4plot_1.append(pd.DataFrame([[self.langdict['balance_cashbook'][1],sum_cashbook]],columns=list(cat4plot_1.columns)),ignore_index=True)
        cat4plot_1['val_month']=cat4plot_1['val']/(self.month_data[cashbook_name]['month'].nunique())
        #second categorical subset sorted by cash categories
        cat4plot_2=cashbook_plotsubset.groupby("cashcat",sort=False)['val'].sum().abs().reset_index()
        cat4plot_2=cat4plot_2.sort_values(['val'],ascending=False)
        cat4plot_2=cat4plot_2.append(pd.DataFrame([[self.langdict['balance_cashbook'][1],sum_cashbook]],columns=list(cat4plot_2.columns)),ignore_index=True)
        cat4plot_2['val_month']=cat4plot_2['val']/(self.month_data[cashbook_name]['month'].nunique())
        cat4plot_2.columns=["cashcat","val_2","val_month_2"]
        #join both subsets on the left side
        cat4plot_join=pd.concat([cat4plot_1, cat4plot_2],axis=1)#integrate two empty columns
        

        self.cat_data[cashbook_name]=cat4plot_join
        self.folder_res[cashbook_name]=self.res_dir+cashbook_name
        self.plotting_list[cashbook_name]='basic'
        return (cashbook_errorlist,cashbook_successlist)

        


    
    def makefolder_excel(self):
        ## Create folders and export data into excel with several subsheets

        for element_name in list(self.folder_res.keys()):
            result_dir=self.folder_res[element_name]
            try:
                if not os.path.exists(result_dir):
                    os.makedirs(result_dir)
            except OSError:
                print ('Error: Creating directory. ' +  result_dir)

            #set excel writer depending on language choice
            if self.lang_choice=='deu': #german date format
                writer_excel = pd.ExcelWriter(result_dir+self.folder_sep+element_name+self.langdict['result_pathvars'][1]+'.xlsx', engine='openpyxl',datetime_format="dd.mm.yyyy")

            else:#english date format
                writer_excel = pd.ExcelWriter(result_dir+self.folder_sep+element_name+self.langdict['result_pathvars'][1]+'.xlsx', engine='openpyxl')

            if element_name in self.raw_data:
                self.raw_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetname_rawdata'][0],index=False,header=self.raw_data_header[element_name])
            else:#no action needed
                pass

            if element_name==self.langdict['dataname_savecent'][0]:
                self.basis_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetnames_savecent1'][0],index=False,header=self.langdict['sheetnames_savecent1'][1])
                self.month_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetnames_savecent2'][0],index=False,header=self.langdict['sheetnames_savecent2'][1])
                self.cat_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetnames_savecent3'][0],index=False,header=self.langdict['sheetnames_savecent3'][1])

            elif element_name==self.langdict['cashbookvars_name'][0]:
                
                self.basis_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetnames_cashbook1'][0],index=False,header=self.langdict['sheetnames_cashbook1'][1])
                #disintregate cat data
                cashbook_cats=self.cat_data[element_name].copy()
                cashbook_cats1=cashbook_cats[cashbook_cats.columns[[0,1,2]]]
                cashbook_cats2=cashbook_cats[cashbook_cats.columns[[3,4,5]]]
                #export cat data
                cashbook_cats1.to_excel(writer_excel,sheet_name=self.langdict['sheetnames_cashbook2'][0],index=False,header=self.langdict['sheetnames_cashbook2'][1])
                cashbook_cats2.to_excel(writer_excel,sheet_name=self.langdict['sheetnames_cashbook3'][0],index=False,header=self.langdict['sheetnames_cashbook3'][1])
               
                

            else:
                self.basis_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetname_basis'][0],index=False,header=self.langdict['sheetname_basis'][1])
                self.cat_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetname_catdata'][0],index=False,header=self.langdict['sheetname_catdata'][1])
     
            writer_excel.save()
