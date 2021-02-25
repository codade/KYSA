
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

if platform.system()=='Darwin':
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
            if platform.system()=='Darwin':
                locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
            else:
                locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        
        self.current_date=datetime.datetime.now().strftime("%b'%y")
        self.imported_acctypes={} #longterm excel, excel and csv files
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
        self.bank_shortnames=('comdi_giro','comdi_credit','dkb_giro','dkb_credit','mlp_triodos_giro','apobank_giro','sparka_giro','consors_giro','commerz_giro','deutsche_giro')
        self.bank_fullnames=("Comdirect Girokonto","Comdirect Kreditkarte","DKB Girokonto","DKB Kreditkarte","MLP / Triodos Girokonto","Apobank Girokonto","Sparkasse Girokonto","Consorsbank Girokonto","Commerzbank Girolkonto","Deutsche Bank Girokonto")


            
        

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
                header_columns,column_join,column_drop,acc_subtype,plot_info=account_infos #acc_subtype ('giro' or 'credit') currently not used, but kept in tuple list for possible later use

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
                    self.basis_data[filename]=self.classifier.categorize_rawdata(self.basis_data[filename],'csvdata')
                except:
                    self.error_codes[filename]='Err03'
                    break
                
                #add account type to basis dataframe and to imported_acctypes list
                imported_acctypename=self.bank_fullnames[self.bank_shortnames.index(acctype)]
                self.basis_data[filename]['acctype']=None #create acctype column and set values to Nan
                self.basis_data[filename].at[0,'acctype']=imported_acctypename #set account type to imported name 

                self.imported_acctypes[filename]=acctype
                #add variables for subsequent handling and plotting
                self.plotting_list[filename]=plot_info
                
                self.folder_res[filename]=self.res_dir+filename
                break

           
        #Plot manually manipulated excel files
        elif import_type=='xls_analyse':

            #read excel
            try:
                raw_data=pd.read_excel(filepath,sheet_name=self.langdict['sheetname_basis'][0], engine='openpyxl') #main category is not read-in but separately assigned)
                try:
                    acctype_name=raw_data[raw_data.columns[8]][0] #get acctype data if existing
                except: # if bank name is not existing set it to unknown#
                    acctype_name=self.langdict['acctype_name'][1]
                    
                raw_data=raw_data[raw_data.columns[range(0,7)]].copy()
                raw_data.dropna(subset=raw_data.columns[[0,4]],inplace=True) #delete rows where value in time1 or val column is empty

                #check if raw data is in the right data format and contains at least one row
                if (raw_data.columns.tolist()==self.langdict['sheetname_basis'][1][:-2]) and (len(raw_data)!=0): 

                #headers must be identical to those outputted via excel
                    raw_data.columns=["time1","time2","act","text","val",'month','cat']

                    #save histo data to saved file

                    histo_data=raw_data[['act','text','cat']].copy() #get a copy of relevant data for categorization
                    self.classifier.machineclassifier.adjust_histo_data(histo_data) # add data to existing history dataset
                    del histo_data

                    self.basis_data[filename]=raw_data.copy()
                    self.basis_data[filename]=self.classifier.assign_maincats(self.basis_data[filename]) #assign main categories

                    self.basis_data[filename]['acctype']=None #create acctype column and set values to Nan
                    self.basis_data[filename].at[0,'acctype']=acctype_name #set account type to imported name 

                    self.plotting_list[filename]=""
                    self.folder_res[filename]=self.res_dir+filename

                    #set acctype to imported_acctypes if existing
                    if acctype_name in self.bank_fullnames:
                        self.imported_acctypes[filename]=self.bank_shortnames[self.bank_fullnames.index(acctype_name)] #if name doesn't exist in list it breaks
                    else:
                        pass
                    
                else:
                    self.error_codes[filename]='Err01'

                del raw_data

            except:
               self.error_codes[filename]='Err01'

        # Excel file for concatenation
        elif import_type=='xls_longterm':

            #Longterm analysis: Read-in excel to concat csvs
            try:
                raw_data=pd.read_excel(filepath,sheet_name=self.langdict['sheetname_basis'][0], engine='openpyxl') #main category is not read-in but separately assigned)
                try:
                    acctype_name=raw_data[raw_data.columns[8]][0] #get acctype data if existing
                    
                except: # if bank name is not existing set it to unknown#
                    acctype_name=self.langdict['acctype_name'][1]
                    
                raw_data=raw_data[raw_data.columns[range(0,7)]].copy()
                raw_data.dropna(subset=raw_data.columns[[0,4]],inplace=True) #delete rows where value in time1 or val column is empty

                #check if raw data is in the right data format and contains at least one row
                if (raw_data.columns.tolist()==self.langdict['sheetname_basis'][1][:-2]) and (len(raw_data)!=0): 

                #headers must be identical to those outputted via excel
                    raw_data.columns=["time1","time2","act","text","val",'month','cat']

                    #save histo data to saved file
                    histo_data=raw_data[['act','text','cat']].copy() #get a copy of relevant data for categorization
                    self.classifier.machineclassifier.adjust_histo_data(histo_data) # add data to existing history dataset
                    del histo_data

                    self.basis_data[filename]=raw_data.copy()
                    self.basis_data[filename]=self.classifier.assign_maincats(self.basis_data[filename]) #assign main categories

                    self.basis_data[filename]['acctype']=None #create acctype column and set values to Nan
                    self.basis_data[filename].at[0,'acctype']=acctype_name #set account type to imported name 

                    #set acctype to imported_acctypes if existing
                    if acctype_name in self.bank_fullnames:
                        self.imported_acctypes[filename]=self.bank_shortnames[self.bank_fullnames.index(acctype_name)] #if name doesn't exist in list it breaks
                    else:
                        pass
                else:
                    self.error_codes[filename]='Err01'

                del raw_data

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
                #raw_data['cat']=raw_data[["text",'cat']].apply(lambda dataitem: self.classifier.fixedvalue_categorizer(''.join(dataitem['text'].lower().split())) if dataitem['cat'] is np.nan else dataitem['cat'],axis=1)
                      
                if raw_data[['time1','text','val']].isnull().values.any()==False:#reject cashbook if there are empty values
                    
                    raw_data['val']=-raw_data['val']
                    raw_data["time2"]=raw_data["time1"]
                    raw_data['month']=raw_data['time1'].apply(lambda dates: dates.strftime('%b %Y'))
                    raw_data['act']=self.langdict['cashbookvars_name'][1]
                    
                    #do categorization for empty values in cashbook, get main cats and reorder dataframe
                    raw_data=self.classifier.categorize_rawdata(raw_data,'cashbook')        
                    raw_data=raw_data.reindex(columns=raw_data.columns[[0,6,8,1,2,7,3,9,4,5]])
                    self.basis_data[self.langdict['cashbookvars_name'][0]]=raw_data.copy()

                else:
                    self.error_codes[filename]='Err01'

                del raw_data
            except:
                self.error_codes[filename]='Err01'


        else:#no action needed
            pass
         

    
    def sorting_processor(self,element_name,balance_row_name,group_name,value_name):

        basis_data_subset=self.basis_data[element_name].copy() #create subset

        #make month data
        self.month_data[element_name]=basis_data_subset.groupby('month',sort=False)[value_name].sum().reset_index() ##get monthly overview

        if element_name==self.langdict['dataname_savecent'][0]: #do sorting of month data differently for savecents
            self.month_data[element_name]=self.month_data[element_name].sort_values([value_name],ascending=False)
            self.month_data[element_name].columns=['month','val']

        else: #sort monthly data for all other dataframes starting with first month up respective left in monthplot
            self.month_data[element_name]=self.month_data[element_name][::-1]

        month_number=self.month_data[element_name]['month'].nunique()

        #process data and aggregate based on sorting type(category/main category)
        grouped_data=basis_data_subset.groupby(group_name,sort=False)[value_name].sum().reset_index()

        balance_row=pd.DataFrame([[balance_row_name, sum(basis_data_subset[value_name])]],columns=list(grouped_data.columns))
        grouped_data=grouped_data.sort_values([value_name],ascending=False).reset_index(drop=True) #sort by values to have all positive values at top (necessary to get indices
        #if not (element_name==self.langdict['dataname_savecent'][0] or element_name==self.langdict['cashbookvars_name'][0]): 
        income_data=grouped_data.loc[(grouped_data[value_name]>0)].copy() #get positive valued entries 

        #get negative valued entries based on length of positive valued dataframe
        if len(income_data.index)>0:
            cost_data=grouped_data[income_data.index[-1]+1:].copy()
        else:
            cost_data=grouped_data[0:].copy()

        cost_data=cost_data.sort_values([value_name]) # sort negative valued dataframe, with most negative at top
        result_data=income_data.append(cost_data,ignore_index=True) #append negative dataframe to positive dataframe
        result_data=result_data.append(balance_row,ignore_index=True) # add balance row
        result_data['val_month']=result_data[value_name]/(month_number) # create value per month 

        return result_data


    def month_cat_maker(self):
        
        ##categorize data and sort ascending. Same goes for monthly data
        for element_name in list(self.folder_res.keys()):

            if element_name==self.langdict['dataname_savecent'][0]:
                main_cats="empty"
                subcats=self.sorting_processor(element_name,self.langdict['balance_savecent'][0],'acc_origin','savecent')
                subcats.columns=['cat','val','val_month']

            elif element_name==self.langdict['cashbookvars_name'][0]:
                subcats=self.sorting_processor(element_name,self.langdict['balance_cashbook'][1],'cat','val')
                main_cats=self.sorting_processor(element_name,self.langdict['balance_cashbook'][1],'acctype','val') #main cats equals acctype sorting
                #rename columns maincat cashbook from 'acctype' to 'cat'
                main_cats.columns=['cat','val','val_month']

            elif element_name==self.langdict['holidayvars_name'][0]:
                main_cats="empty"
                subcats=self.sorting_processor(element_name,self.langdict['balance_holiday'][0],'cat','val')

            else: #make cat data and month data for all other dataframes
                main_cats=self.sorting_processor(element_name,self.langdict['balance_normal'][0],'main cat','val') # create sorted dataframe for main categories
                subcats=self.sorting_processor(element_name,self.langdict['balance_normal'][0],'cat','val') # create sorted dataframe for categories
                subcats=self.classifier.assign_maincats(subcats) #add main category column to cat data for later use
                subcats.loc[subcats['cat']==self.langdict['balance_normal'][0],'main cat']=self.langdict['balance_normal'][0] #adjust main category for balance category 
                subcats=subcats.reindex(columns=['main cat','cat','val','val_month'])#reorder columns
            
            self.cat_data[element_name]=(subcats,main_cats)
                
    #def longterm_evaluate(self,saved_data,user_choice):
    def longterm_evaluate(self,saved_data,user_choice):
        #update saved longterm data, evaluate and output if user opted for it
        #get saved longterm data
        self.longterm_data=saved_data

        #create iterable dict for acc types and store imported filename in list 
        acctypelist_dict={}
        #get indices to extract single dataframes of longterm data file
        indices_new_dataframes=list(np.where(self.longterm_data['acctype'].isna()==False)[0]) #get indices where a account name is set

        for num in range(0,len(indices_new_dataframes)): #iterate through list with indices
            lowerlimit=indices_new_dataframes[num]
            if lowerlimit != indices_new_dataframes[-1]:
                upperlimit=indices_new_dataframes[num+1]
                acctypelist_dict[new_dataframe['acctype'][lowerlimit]]=new_dataframe.iloc[lowerlimit:upperlimit] #get saved subdataframes including second to last and save it to dataframe dict
            else:
                acctypelist_dict[new_dataframe['acctype'][lowerlimit]]=new_dataframe.iloc[lowerlimit:] #get saved last dataframe and save it to dataframe dict

        #get basis dataframe for every imported account type 
        for element_name in list(self.imported_acctypes.keys()):
            if self.imported_acctypes[element_name]!=self.langdict['acctype_name'][1]: #check if the name is 'unknown'. If yes skip, else import basis data
                try: #if list for acctype already exists, add dataframe
                    acctypelist_dict[self.imported_acctypes[element_name]].append(self.basis_data[element_name])
                except: #create list for acctype with dataframe
                    acctypelist_dict[self.imported_acctypes[element_name]]=[self.basis_data[element_name]]
            else:
                pass #nothing to do
            
        #generate new dataframes
        longterm_data_prep=[]
        for account_type in acctypelist_dict.keys():

            acctype_concat=pd.concat(acctypelist_dict[account_type]) #concat data for every account type and list it
            acctype_concat.drop_duplicates(subset=['time1','text','val'],inplace=True,ignore_index=True) #get rid of doubled entry rows with respect to time1,text and value
            acctype_concat['acctype']=None # clear acctype 
            acctype_concat.at[0,'acctype']=account_type#set new account type for this subframe
            # if chosen by user evaluate this new dataframe and create basis_dataframe with the account type name
            if user_choice:
                longterm_data_name=self.langdict['longterm_name'][0]+self.bank_fullnames[self.bank_shortnames.index(account_type)] # "Longterm_"+account fullname 
                self.basis_data[longterm_data_name]=acctype_concat
            else:
                pass #nothing to do
            longterm_data_prep.append(acctype_concat) #save concatted datframe to list to be able to concat all data frames and store it as csv
        self.longterm_data=pd.concat(longterm_data_prep)
        return self.longterm_data
    
    def concatter(self,concat_list):
        
        #create list to find concat choice in datasets
        for item in concat_list:
            #tuple unpack concat choice values
            framename,concat_choice=item
            #get names for new datasets
            concat_dataframes=[]
            acctypelist=[]# determine wether all dataframe have same account type or not
            for choicename in concat_choice:               
                concat_dataframes.append(self.basis_data[choicename])
                acctypelist.append(self.basis_data[choicename][self.basis_data[choicename].columns[8]][0])#read acctype and save it to list
            #concat and add to data-object
            self.basis_data[framename]=pd.concat(concat_dataframes)
            self.basis_data[framename].drop_duplicates(subset=['time1','text','val'],inplace=True,ignore_index=True) #get rid of doubled entry rows with respect to time1,text and value
            self.basis_data[framename]=self.basis_data[framename].sort_values(['time1'],ascending=False)

            #add acctype
            self.basis_data[framename]['acctype']=None #clear acctype column
            if all(elem == acctypelist[0] for elem in acctypelist): #if all entries in acctypelist are identical, take first value of list else write unclear
                self.basis_data[framename].at[0,'acctype']=acctypelist[0] #set acctype
            else:
                self.basis_data[framename].at[0,'acctype']=self.langdict['acctype_name'][1] #set unknown

            self.folder_res[framename]=self.res_dir+framename
            self.plotting_list[framename]=""



    def bundle_holiday(self):
        #concat holiday data from different csv-files
        holidayvar_name=self.langdict['holidayvars_name'][0]
        self.basis_data[holidayvar_name]=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat","main cat","acctype"])
        for element_name in list(self.folder_res.keys()):
            if not (element_name==self.langdict['dataname_savecent'][0] or element_name==self.langdict['cashbookvars_name'][0]): #cashbook and savecentnames
                data_hol=self.basis_data[element_name].loc[self.basis_data[element_name]['main cat']==self.langdict['holiday_searchwords'][0]].copy()
                self.basis_data[holidayvar_name]=self.basis_data[holidayvar_name].append(data_hol,ignore_index=True)
                self.basis_data[holidayvar_name].drop_duplicates(subset=['time1','time2','text'],inplace=True,ignore_index=True) #drop dubplicates if existing
        
        if len(self.basis_data[holidayvar_name].index)>0:

            self.basis_data[holidayvar_name]=self.basis_data[holidayvar_name].sort_values(['time1'],ascending=False)

            self.basis_data[holidayvar_name]['acctype']=None #set all acctype values from imports to NaN
            self.basis_data[holidayvar_name].at[0,'acctype']=str(self.langdict['holiday_searchwords'][0]) #set account type to holiday search word

            self.folder_res[holidayvar_name]=self.res_dir+self.langdict['holidayvars_name'][1]
            self.plotting_list[holidayvar_name]='basic'
        
        else:
            del self.basis_data[holidayvar_name]



    def savecent_calculation(self):
        #account for difference between actucal cost value and full amount (rounding). Gives a number which can be invested every month. Since the data structure will be different, the results will be saved and plotted separately.
        savecentvar_name=self.langdict['dataname_savecent'][0]
        self.basis_data[savecentvar_name]=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat","main cat","savecent","acc_origin"])
        #get data from every imported csv and do savecent calculation
        for element_name in list(self.basis_data.keys()):# use all imported data except cashbook and holiday
            if not (element_name==savecentvar_name or element_name==self.langdict['holidayvars_name'][0] or element_name==self.langdict['cashbookvars_name'][0]): #cashbook and holiday names
                savecent_subset=self.basis_data[element_name].loc[self.basis_data[element_name]['val']<0].copy()
                savecent_subset['savecent']=np.ceil(savecent_subset['val'].abs())+savecent_subset['val']
                savecent_subset['acc_origin']=element_name
                self.basis_data[savecentvar_name]=self.basis_data[savecentvar_name].append(savecent_subset,ignore_index=True)
                self.basis_data[savecentvar_name].drop_duplicates(subset=['time1','time2', 'text'],inplace=True,ignore_index=True) # drop duplicate entries (determination by time1, time2 and text)

        if len(self.basis_data[savecentvar_name].index)>0:
            self.basis_data[savecentvar_name]=self.basis_data[savecentvar_name].sort_values(['time1'],ascending=False)
            self.basis_data[savecentvar_name].drop('acctype',axis=1,inplace=True) #drop account name column
            self.folder_res[savecentvar_name]=self.res_dir+savecentvar_name
            self.plotting_list[savecentvar_name]='basic'

            #categorization is done via month-cat-maker-function

        else:
            del self.basis_data[savecentvar_name]


    def cashbook_calculation(self):
    #Preparations
        cashbook_name=self.langdict['cashbookvars_name'][0]
        cashbook_subset=self.basis_data[cashbook_name].copy()
        #reformat acctype names 

        #rename bank account names to abbreviations for further processing
        for item in self.bank_fullnames:
            cashbook_subset.loc[cashbook_subset['acctype']==item,'acctype']=self.bank_shortnames[self.bank_fullnames.index(item)]

        cashbook_acctype=list(cashbook_subset["acctype"].unique())
        cashbook_errorlist=[]
        cashbook_successlist=[]
        #check for entries in the cashbook for every imported file with account existing acctype and filter relevant data points (date and cashcat); append if indicated
        for element_name in list(self.imported_acctypes.keys()):
            element_acctype=self.imported_acctypes[element_name]
            #create appendable subframe
            element_cashappend=pd.DataFrame(columns=["time1","time2","act","text","val","month","cat","main cat"])
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
                            subframe_append.drop(subframe_append.columns[[8,9]],axis=1,inplace=True)
                            subframe_sum=pd.DataFrame([[subframe_append['time1'].iloc[0],subframe_append['time2'].iloc[0],self.langdict['cashbookvars_name'][1],self.langdict['balance_cashbook'][0],abs(sum(subframe_append['val'])),subframe_append['month'].iloc[0],item,self.langdict['cashbookvars_name'][1]]],columns=list(subframe_append.columns))
                            subframe_append=subframe_append.append(subframe_sum,ignore_index=True)
                            element_cashappend= element_cashappend.append(subframe_append,ignore_index=True)
                            cashbook_successlist.append(element_name)
                        except:
                            cashbook_errorlist.append(element_name+' (Err08)')
                    else:
                        cashbook_errorlist.append(element_name+' (Err07)')

            else:
                pass#no action needed  

                #append cashbook entries to main data frame
            if len(element_cashappend.index)>0:
                element_cashappend['acctype']=None#add empty acctype column to make it compliant to basis data frames
                self.basis_data[element_name]=self.basis_data[element_name].append(element_cashappend,ignore_index=True) #append files
                self.basis_data[element_name].drop_duplicates(subset=['time1','time2', 'text'],inplace=True,ignore_index=True) # drop duplicate entries (determination by time1, time2 and text)
                self.basis_data[element_name]=self.basis_data[element_name].sort_values('time1',ascending=False).reset_index(drop=True) #sort resulting data frame by time
                
                del element_cashappend
            else:
                del element_cashappend


        #prepare cashbook entries for plotting
        #group by month
        #change back acc types:
        self.basis_data[cashbook_name]['val']=-self.basis_data[cashbook_name]['val'] #save cash payment values as costs     
        self.folder_res[cashbook_name]=self.res_dir+cashbook_name
        self.plotting_list[cashbook_name]='basic'

        #categorization is done via month-cat-maker-function
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

            subcats,main_cats=self.cat_data[element_name] #unpack both subframes //For holiday and savecent main_cats is empty. For cashbook main_cats==acctypes

            if element_name==self.langdict['dataname_savecent'][0]:
                self.basis_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetnames_savecent1'][0],index=False,header=self.langdict['sheetnames_savecent1'][1])
                self.month_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetnames_savecent2'][0],index=False,header=self.langdict['sheetnames_savecent2'][1])
                subcats.to_excel(writer_excel,sheet_name=self.langdict['sheetnames_savecent3'][0],index=False,header=self.langdict['sheetnames_savecent3'][1])

            elif element_name==self.langdict['cashbookvars_name'][0]:
                
                self.basis_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetnames_cashbook1'][0],index=False,header=self.langdict['sheetnames_cashbook1'][1])

                subcats.to_excel(writer_excel,sheet_name=self.langdict['sheetnames_cashbook2'][0],index=False,header=self.langdict['sheetnames_cashbook2'][1])
                main_cats.to_excel(writer_excel,sheet_name=self.langdict['sheetnames_cashbook3'][0],index=False,header=self.langdict['sheetnames_cashbook3'][1])
    
            else:
                self.basis_data[element_name].to_excel(writer_excel,sheet_name=self.langdict['sheetname_basis'][0],index=False,header=self.langdict['sheetname_basis'][1])

                if element_name==self.langdict['holidayvars_name'][0]: #handle holidays differently as acctype is not included

                    subcats.to_excel(writer_excel,sheet_name=self.langdict['sheetname_holidaycatdata'][0],index=False,header=self.langdict['sheetname_holidaycatdata'][1])
                else:

                    main_cats.to_excel(writer_excel,sheet_name=self.langdict['sheetname_maincatdata'][0],index=False,header=self.langdict['sheetname_maincatdata'][1])
                    subcats.to_excel(writer_excel,sheet_name=self.langdict['sheetname_catdata'][0],index=False,header=self.langdict['sheetname_catdata'][1])
     
            writer_excel.save()
