
'''This file holds all relevant functions necessary for starting the data analysis.
An object class for all account data is established, which will hold the raw data after import,
the processed data and all subdata configuration necessary for plotting.
The account data is provided through the account identification process in account_ident.py
Necessary functions for holiday extraction, roundies calculation as well as merging and cashbook linkage are provided in the Accounts class
Excel file is exported at the end exported.'''


import datetime
import locale
import os
import platform

import numpy as np
import pandas as pd

from basefunctions import account_ident




if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, 'German')
    FOLDER_SEP = '\\'

elif platform.system() == 'Darwin':
    locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
    FOLDER_SEP = '/'

else:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    FOLDER_SEP = '/'

#_______________________________________ read in longterm data for training machine learning algorithm _______________

def longtermdata_import(path, decrypt_success):


    if decrypt_success:
        longterm_data = pd.read_csv(path, sep=';', parse_dates=[0, 1])
    else:
        empty_dataframe = {'time1':np.datetime64, 'time2':np.datetime64, 'act':str, 'text':str, 'val':float, 'month':str, 'cat':str, 'main cat':str, 'acc_name':str}
        longterm_data = pd.DataFrame(columns=empty_dataframe.keys()).astype(empty_dataframe)

    #extract saved account names in longterm_data
    saved_accnames = list(longterm_data['acc_name'].unique())
    saved_dataframe = {} #stored dataframes from import
    for account_name in saved_accnames: #iterate through list with indices
        saved_dataframe[account_name] = longterm_data.loc[longterm_data['acc_name'] == account_name] #get saved dataframes

    return saved_dataframe


def longterm_export(path, saved_dataframe):#needs to be outside class in case program is closed before data integration

    longterm_data = pd.DataFrame(columns=['time1', 'time2', 'act', 'text', 'val', 'month', 'cat', 'main cat', 'acc_name'])
    for account_name in saved_dataframe.keys():
        account_name_concat = saved_dataframe[account_name]
        account_name_concat['acc_name'] = account_name #set account name in dataframe to be saved
        longterm_data = pd.concat([longterm_data, account_name_concat]) #concatinated data

    longterm_data.to_csv(path, index=False, sep=';') #export data




class AccountsData:

    def __init__(self, dir_result, classifier_class, langdict, saved_dataframe):

        self.langdict = langdict

        ## set language variable
        if self.langdict['result_pathvars'][0] == 'Ergebnisse_':
            self.lang_choice = 'deu'
        else:
            self.lang_choice = 'eng'
            #change locale to English
            if platform.system() == 'Windows':
                locale.setlocale(locale.LC_ALL, 'English')
            elif platform.system() == 'Darwin':
                locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
            else:
                locale.setlocale(locale.LC_ALL, 'en_US.utf8')

        self.current_date = datetime.datetime.now().strftime("%b'%y")
        self.acc_names_rec = {} #longterm excel, excel and csv files
        self.folder_sep = FOLDER_SEP
        self.dir_result = dir_result+FOLDER_SEP+self.langdict['result_pathvars'][0]+self.current_date+FOLDER_SEP #adjusted complete path
        self.folder_res = {}
        self.raw_data = {}
        self.raw_data_header = {}
        self.basis_data = {}
        self.month_data = {}
        self.cat_data = {}
        self.plotting_list = {}
        self.error_codes = {}
        self.classifier = classifier_class
        self.saved_dataframe = saved_dataframe



    def process_data(self, raw_fileinfo, import_type):

        #unpack tuple with fileinformation
        filename, filepath = raw_fileinfo
        ##read in csv-files from different account_types

        ##start functions for getting csv account type info and data input & adjustment
        if import_type == 'csv_analyse':

            #get account information
            while True:
                try:
                    acctypename_importedfile, raw_data, account_infos = account_ident.account_info_identifier(filepath)

                except:
                    self.error_codes[filename] = 'Err01'
                    break

                ##unpack account read-in info tuple
                header_columns, column_join, column_drop, acc_subtype, plot_info = account_infos #acc_subtype ('giro' or 'credit') currently not used, but kept in tuple list for possible later use

                self.raw_data[filename] = raw_data
                self.raw_data_header[filename] = header_columns

                #data preprocess
                try:
                    #select Euro entrys
                    if "Währung" in header_columns:
                        self.basis_data[filename] = self.raw_data[filename][self.raw_data[filename]["Währung"] == "EUR"].copy()
                    elif "currency" in header_columns:
                        self.basis_data[filename] = self.raw_data[filename][self.raw_data[filename]["currency"] == "EUR"].copy()
                    else:
                        self.basis_data[filename] = self.raw_data[filename].copy()

                    ##do adjustment to transactions info (join columns to get more info) for categorization. Output is forced to be string datype
                    if column_join[0] == 'yes':
                        self.basis_data[filename]['text'] = self.basis_data[filename][self.basis_data[filename].columns[column_join[1]]].apply(lambda x: str(' || '.join(x.dropna())), axis=1)
                    else:
                        pass

                    ##drop columns if necessary and reaarange columns
                    if column_drop[0] == 'yes':
                        self.basis_data[filename].drop(self.basis_data[filename].columns[column_drop[1]], axis=1, inplace=True)
                        self.basis_data[filename] = self.basis_data[filename].reindex(columns=self.basis_data[filename].columns[column_drop[2]])
                    else:
                        pass

                    ##insert "act" column if necessary (currently only dkb_credit)
                    if len(self.basis_data[filename].columns) == 4:
                        self.basis_data[filename].insert(2, 'act', self.langdict['act_value'][0])
                    else:
                        pass

                    self.basis_data[filename].columns = ["time1", "time2", "act", "text", "val"]

                    #delete row with time1&time2 empty
                    self.basis_data[filename] = self.basis_data[filename].drop(self.basis_data[filename][(self.basis_data[filename]['time1'].isna())&(self.basis_data[filename]['time2'].isna())].index)
                    #adjust for missing time values in "time1"-columns
                    self.basis_data[filename]['time1'].mask(self.basis_data[filename]['time1'].isna(), self.basis_data[filename]['time2'], inplace=True) ##new
                    #make month-column and categorize
                    self.basis_data[filename]['month'] = self.basis_data[filename]['time1'].apply(lambda dates: dates.strftime('%b %Y'))

                except:
                    self.error_codes[filename] = 'Err02'
                    break

                #check if all transaction values is Null. If yes, abort and give errorcode '03'
                if self.basis_data[filename]['val'].isna().all():
                    self.error_codes[filename] = 'Err03'
                    break
                else:
                    pass
                #try categorization else give error code '04'

                try:
                    self.basis_data[filename] = self.classifier.categorize_rawdata(self.basis_data[filename], 'csvdata')
                except:
                    self.error_codes[filename] = 'Err04'
                    break

                #add account name to dictionary with imported data files and their respective account names (for cashbook, savecent and long term data saving)
                self.acc_names_rec[filename] = acctypename_importedfile
                #add variables for subsequent handling and plotting
                self.plotting_list[filename] = plot_info

                self.folder_res[filename] = self.dir_result+filename
                break


        #Plot manually manipulated excel files
        elif import_type == 'xls_analyse':

            #read excel
            try:
                raw_data = pd.read_excel(filepath, sheet_name=self.langdict['sheetname_basis'][0], engine='openpyxl') #main category is not read-in but separately assigned)


                try:
                    testname = raw_data[raw_data.columns[8]][0] #get account name if existing

                    #check if testname is nan-value (as nan are not identical it can be checked with !=)
                    if testname != testname: #if imported account name field is Nan-value use "not assigned"
                        acctypename_importedfile = self.langdict['accname_labels'][1] #set acctypename to not assigned
                    else:
                        acctypename_importedfile = testname #take name which was read in

                except: # if bank name is not existing set it to not assigned#
                    acctypename_importedfile = self.langdict['accname_labels'][1]


                raw_data = raw_data[raw_data.columns[range(0, 7)]].copy()
                raw_data.dropna(subset=raw_data.columns[[0, 4]], inplace=True) #delete rows where value in time1 or val column is empty

                #check if raw data is in the right data format and contains at least one row
                if (raw_data.columns.tolist() == self.langdict['sheetname_basis'][1][:-2]) and (len(raw_data) != 0):
                #headers must be identical to those outputted via excel
                    raw_data.columns = ["time1", "time2", "act", "text", "val", 'month', 'cat']

                    #save histo data to saved file

                    histo_data = raw_data[['act', 'text', 'cat']].copy() #get a copy of relevant data for categorization
                    self.classifier.machineclassifier.adjust_histo_data(histo_data) # add data to existing history dataset
                    del histo_data

                    self.basis_data[filename] = raw_data.copy()
                    self.basis_data[filename] = self.classifier.assign_maincats(self.basis_data[filename]) #assign main categories

                    self.acc_names_rec[filename] = acctypename_importedfile #add account name to dictionary with imported data files and their respective account names (for cashbook, savecent and long term data saving)

                    self.plotting_list[filename] = 'normal'
                    self.folder_res[filename] = self.dir_result+filename
                else:
                    self.error_codes[filename] = 'Err01'

                del raw_data

            except:
                self.error_codes[filename] = 'Err01'

        # Excel file for concatenation
        elif import_type == 'xls_longterm':

            #Longterm analysis: Read-in excel to concat csvs
            try:
                raw_data = pd.read_excel(filepath, sheet_name=self.langdict['sheetname_basis'][0], engine='openpyxl') #main category is not read-in but separately assigned)

                #variabel "assigned_accname" does not need to be checked, as it is always 'use_acctype' for longterm excel concat
                try:#try to get the account name from excel
                    testname = raw_data[raw_data.columns[8]][0] #get account name if existing
                    #check if testname is nan-value (as nan are not identical it can be checked with !=)
                    if testname != testname: #if imported account name field is Nan-value use "not assigned"
                        acctypename_importedfile = self.langdict['accname_labels'][1] #set acctypename to not assigned
                    else:
                        acctypename_importedfile = testname #take name which was read in
                except: # if bank name is not existing set it to not assigned#
                    acctypename_importedfile = self.langdict['accname_labels'][1]

                raw_data = raw_data[raw_data.columns[range(0, 7)]].copy()
                raw_data.dropna(subset=raw_data.columns[[0, 4]], inplace=True) #delete rows where value in time1 or val column is empty

                #check if raw data is in the right data format and contains at least one row
                if (raw_data.columns.tolist() == self.langdict['sheetname_basis'][1][:-2]) and (len(raw_data) != 0):

                #headers must be identical to those outputted via excel
                    raw_data.columns = ["time1", "time2", "act", "text", "val", 'month', 'cat']

                    #save histo data to saved file
                    histo_data = raw_data[['act', 'text', 'cat']].copy() #get a copy of relevant data for categorization
                    self.classifier.machineclassifier.adjust_histo_data(histo_data) # add data to existing history dataset
                    del histo_data

                    self.basis_data[filename] = raw_data.copy()
                    self.basis_data[filename] = self.classifier.assign_maincats(self.basis_data[filename]) #assign main categories

                    #account names for excel-extraimport only needed because of concatination function searching for identical "acc-name" values
                    self.basis_data[filename]['acc_name'] = None #create acctype column and set values to Nan
                    self.basis_data[filename].at[0, 'acc_name'] = acctypename_importedfile #set account name to basis dataframe for possible concatination


                else:
                    self.error_codes[filename] = 'Err01'

                del raw_data

            except:
                self.error_codes[filename] = 'Err01'

              # Excel file for concatenation

        elif import_type == 'xls_cashbook':

            #cashbok analysis: Read-in to append info to csvs
            try:
                raw_data = pd.read_excel(filepath, sheet_name=self.langdict['cashbookvars_name'][0], usecols=[0, 1, 2, 3, 4, 5], engine='openpyxl')
                raw_data.columns = ["time1", "text", "val", "cat", "acc_name", "cashcat"]
                raw_data = raw_data[raw_data['time1'].isna() == False]
                #adjust categories if no value is set

                if raw_data[['time1', 'text', 'val']].isnull().values.any() == False:#reject cashbook if there are empty values in date, value or text

                    raw_data['val'] = -raw_data['val']
                    raw_data["time2"] = raw_data["time1"]
                    raw_data['month'] = raw_data['time1'].apply(lambda dates: dates.strftime('%b %Y'))
                    raw_data['act'] = self.langdict['cashbookvars_name'][1]

                    #do categorization for empty values in cashbook, get main cats and reorder dataframe
                    raw_data = self.classifier.categorize_rawdata(raw_data, 'cashbook')
                    raw_data = raw_data.reindex(columns=raw_data.columns[[0, 6, 8, 1, 2, 7, 3, 9, 4, 5]])
                    self.basis_data[self.langdict['cashbookvars_name'][0]] = raw_data.copy()

                else:
                    self.error_codes[filename] = 'Err01'

                del raw_data
            except:
                self.error_codes[filename] = 'Err01'


        else:#no action needed
            pass

    def assign_fileaccnames(self, assign_list):

        for entry in assign_list:
            #entry[0] equals filename / entry[1] account name
            #set account name to dictionary holding all account names (needed for cashbook, longterm and savecent)
            self.acc_names_rec[entry[0]] = entry[1] 
            
            #create account name column for excel export
            self.basis_data[entry[0]]['acc_name'] = None #create account name column and set values to Nan
            self.basis_data[entry[0]].at[0, 'acc_name'] = entry[1] #set account name to basis dataframe (will be exported to excel)


    def sorting_processor(self, element_name, balance_row_name, group_name, value_name):

        basis_data_subset = self.basis_data[element_name].copy() #create subset

        #make month data
        self.month_data[element_name] = basis_data_subset.groupby('month', sort=False)[value_name].sum().reset_index() ##get monthly overview

        if element_name == self.langdict['dataname_savecent'][0]: #do sorting of month data differently for savecents
            self.month_data[element_name] = self.month_data[element_name].sort_values([value_name], ascending=False)
            self.month_data[element_name].columns = ['month', 'val']

        else: #sort monthly data for all other dataframes starting with first month up respective left in monthplot
            self.month_data[element_name] = self.month_data[element_name][::-1]

        month_number = self.month_data[element_name]['month'].nunique()

        #process data and aggregate based on sorting type(category/main category)
        grouped_data = basis_data_subset.groupby(group_name, sort=False)[value_name].sum().reset_index()

        balance_row = pd.DataFrame([[balance_row_name, sum(basis_data_subset[value_name])]], columns=list(grouped_data.columns))
        grouped_data = grouped_data.sort_values([value_name], ascending=False).reset_index(drop=True) #sort by values to have all positive values at top (necessary to get indices
        income_data = grouped_data.loc[(grouped_data[value_name] > 0)].copy() #get positive valued entries

        #get negative valued entries based on length of positive valued dataframe
        if len(income_data.index) > 0:
            cost_data = grouped_data[income_data.index[-1]+1:].copy()
        else:
            cost_data = grouped_data[0:].copy()

        cost_data = cost_data.sort_values([value_name]) # sort negative valued dataframe, with most negative at top
        result_data = income_data.append(cost_data, ignore_index=True) #append negative dataframe to positive dataframe
        result_data = result_data.append(balance_row, ignore_index=True) # add balance row
        result_data['val_month'] = result_data[value_name]/(month_number) #create value per month

        return result_data


    def month_cat_maker(self):

        ##categorize data and sort ascending. Same goes for monthly data
        for element_name in list(self.folder_res.keys()):

            if element_name == self.langdict['dataname_savecent'][0]:
                main_cats = "empty"
                subcats = self.sorting_processor(element_name, self.langdict['balance_savecent'][0], 'acc_origin', 'savecent')
                subcats.columns = ['cat', 'val', 'val_month']

            elif element_name == self.langdict['cashbookvars_name'][0]:
                subcats = self.sorting_processor(element_name, self.langdict['balance_cashbook'][1], 'cat', 'val')
                main_cats = self.sorting_processor(element_name, self.langdict['balance_cashbook'][1], 'acc_name', 'val') #main cats equals account name sorting
                #rename columns maincat cashbook from 'acc_name' to 'cat'
                main_cats.columns = ['cat', 'val', 'val_month']

            elif element_name == self.langdict['holidayvars_name'][0]:
                main_cats = "empty"
                subcats = self.sorting_processor(element_name, self.langdict['balance_holiday'][0], 'cat', 'val')

            else: #make cat data and month data for all other dataframes
                main_cats = self.sorting_processor(element_name, self.langdict['balance_normal'][0], 'main cat', 'val') # create sorted dataframe for main categories
                subcats = self.sorting_processor(element_name, self.langdict['balance_normal'][0], 'cat', 'val') # create sorted dataframe for categories
                subcats = self.classifier.assign_maincats(subcats) #add main category column to cat data for later use
                subcats.loc[subcats['cat'] == self.langdict['balance_normal'][0], 'main cat'] = self.langdict['balance_normal'][0] #adjust main category for balance category
                subcats = subcats.reindex(columns=['main cat', 'cat', 'val', 'val_month'])#reorder columns

            self.cat_data[element_name] = (subcats, main_cats)


    #take saved long term data into data evaluation process
    def longterm_evaluate(self): #this function is only called, when user opts for long term data evaluation


        for account_name in self.saved_dataframe.keys():

            account_dataframe = self.saved_dataframe[account_name].copy()

            account_dataframe.reset_index(drop=True, inplace=True) #reset index to be able to place acc_name on index 0
            account_dataframe['acc_name'] = None # clear account name
            account_dataframe.at[0, 'acc_name'] = account_name#set new account type for this subframe
            longterm_data_name = self.langdict['longterm_name'][0]+account_name # "Longterm_"+account fullname

            self.basis_data[longterm_data_name] = account_dataframe #add longterm basis data to be analysed
            self.acc_names_rec[longterm_data_name] = account_name #add longterm data name to recorded account names list--> makes cashbook evaluation possible
            self.plotting_list[longterm_data_name] = 'normal' #set plotting info
            self.folder_res[longterm_data_name] = self.dir_result+longterm_data_name # create export folder

    # add newly added data to longterm data
    def longterm_savedata(self):
        #update saved longterm data, evaluate and output if user opted for it
        #convert saved dataframes in dict entries into lists
        for saved_element in self.saved_dataframe.keys():
            self.saved_dataframe[saved_element] = [self.saved_dataframe[saved_element]]

        #get basis dataframe for every assigned account name
        for element_name in self.acc_names_rec.keys():
            if self.acc_names_rec[element_name] != self.langdict['accname_labels'][1]: #check if the name is 'not assigned'. If yes skip, else import basis data
                try: #if list with account name already exists, add dataframe
                    self.saved_dataframe[self.acc_names_rec[element_name]].append(self.basis_data[element_name])
                except: #create list for account name with dataframe
                    self.saved_dataframe[self.acc_names_rec[element_name]] = [self.basis_data[element_name]]
            else:
                pass #nothing to do

        #generate new dataframes
        longterm_data_prep = {}
        for account_name in self.saved_dataframe.keys():

            account_name_concat = pd.concat(self.saved_dataframe[account_name]) #concat data for every account and list it
            account_name_concat.drop_duplicates(subset=['time1', 'text', 'val'], inplace=True, ignore_index=True) #get rid of doubled entry rows with respect to time1,text and value
            account_name_concat = account_name_concat.sort_values(['time1'], ascending=False).reset_index(drop=True) #sort values by booking date and reset index


            longterm_data_prep[account_name] = account_name_concat #save concatted datframe to dict to be able to concat all data frames and store it as csv in longterm export
        return longterm_data_prep


    def concatter(self, concat_list):

        #create list to find concat choice in datasets
        for item in concat_list:
            #tuple unpack concat choice values
            framename, concat_choice = item
            #get names for new datasets
            concat_dataframes = []
            accountnames = []# determine wether all dataframe have same account type or not
            for choicename in concat_choice:
                concat_dataframes.append(self.basis_data[choicename])
                accountnames.append(self.basis_data[choicename][self.basis_data[choicename].columns[8]][0])#read account name of dataframes to be concatinated and save it to list
            #concat and add to data-object
            self.basis_data[framename] = pd.concat(concat_dataframes)
            self.basis_data[framename].drop_duplicates(subset=['time1', 'text', 'val'], inplace=True, ignore_index=True) #get rid of doubled entry rows with respect to time1, text and value
            self.basis_data[framename] = self.basis_data[framename].sort_values(['time1'], ascending=False).reset_index(drop=True)#sort values by booking date and reset index

            #add account name
            self.basis_data[framename]['acc_name'] = None #clear account name column
            if all(elem == accountnames[0] for elem in accountnames): #if all entries in accountnames are identical,  take first value of list else write unclear
                self.basis_data[framename].at[0, 'acc_name'] = accountnames[0] #set account name
            else:
                self.basis_data[framename].at[0, 'acc_name'] = self.langdict['accname_labels'][1] #set account name to not assigned

            self.folder_res[framename] = self.dir_result+framename
            self.plotting_list[framename] = 'normal'



    def bundle_holiday(self):
        #concat holiday data from different csv-files
        holidayvar_name = self.langdict['holidayvars_name'][0]
        self.basis_data[holidayvar_name] = pd.DataFrame(columns=["time1", "time2", "act", "text", "val", "month", "cat", "main cat", "acc_name"])
        for element_name in list(self.folder_res.keys()):
            if not element_name in (self.langdict['dataname_savecent'][0], self.langdict['cashbookvars_name'][0]): #cashbook and savecentnames
                data_hol = self.basis_data[element_name].loc[self.basis_data[element_name]['main cat'] == self.langdict['holiday_searchwords'][0]].copy()
                self.basis_data[holidayvar_name] = self.basis_data[holidayvar_name].append(data_hol, ignore_index=True)
                self.basis_data[holidayvar_name].drop_duplicates(subset=['time1', 'time2', 'text', 'val'], inplace=True, ignore_index=True) #drop dubplicates if existing

        if len(self.basis_data[holidayvar_name].index) > 0:

            self.basis_data[holidayvar_name] = self.basis_data[holidayvar_name].sort_values(['time1'], ascending=False)

            self.basis_data[holidayvar_name]['acc_name'] = None #set all account name values from imports to NaN
            self.basis_data[holidayvar_name].at[0, 'acc_name'] = self.langdict['accname_labels'][1]  #set account type to not assigned

            self.folder_res[holidayvar_name] = self.dir_result+self.langdict['holidayvars_name'][1]
            self.plotting_list[holidayvar_name] = 'basic'

        else:
            del self.basis_data[holidayvar_name]



    def savecent_calculation(self):
        #account for difference between actucal cost value and full amount (rounding). Gives a number which can be invested every month. Since the data structure will be different,  the results will be saved and plotted separately.
        savecentvar_name = self.langdict['dataname_savecent'][0]
        self.basis_data[savecentvar_name] = pd.DataFrame(columns=["time1", "time2", "act", "text", "val", "month", "cat", "main cat", "savecent", "acc_origin"])
        #get data from every imported csv and do savecent calculation
        for element_name in list(self.basis_data.keys()):# use all imported data except cashbook and holiday
            if not element_name in (savecentvar_name, self.langdict['holidayvars_name'][0], self.langdict['cashbookvars_name'][0]): #cashbook and holiday names
                savecent_subset = self.basis_data[element_name].loc[self.basis_data[element_name]['val'] < 0].copy()
                savecent_subset['savecent'] = np.ceil(savecent_subset['val'].abs())+savecent_subset['val']
                savecent_subset['acc_origin'] = element_name
                self.basis_data[savecentvar_name] = self.basis_data[savecentvar_name].append(savecent_subset, ignore_index=True)
                self.basis_data[savecentvar_name].drop_duplicates(subset=['time1', 'time2', 'text', 'val'], inplace=True, ignore_index=True) # drop duplicate entries (determination by time1,  time2 and text)

        if len(self.basis_data[savecentvar_name].index) > 0:
            self.basis_data[savecentvar_name] = self.basis_data[savecentvar_name].sort_values(['time1'], ascending=False)
            self.basis_data[savecentvar_name].drop('acc_name', axis=1, inplace=True) #drop account name column
            self.folder_res[savecentvar_name] = self.dir_result+savecentvar_name
            self.plotting_list[savecentvar_name] = 'basic'

            #categorization is done via month-cat-maker-function

        else:
            del self.basis_data[savecentvar_name]


    def cashbook_calculation(self):
    #Preparations
        cashbook_name = self.langdict['cashbookvars_name'][0]
        cashbook_subset = self.basis_data[cashbook_name].copy()
        #reformat account names

        #rename bank account names to abbreviations for further processing

        cashbook_accnames = list(cashbook_subset["acc_name"].unique())
        cashbook_errorlist = []
        cashbook_successlist = []
        #check for entries in the cashbook whether this account name was imported and filter relevant data points (date and cashcat); append if indicated
        for element_name in list(self.acc_names_rec.keys()):
            element_accname = self.acc_names_rec[element_name]
            #create appendable subframe
            element_cashappend = pd.DataFrame(columns=["time1", "time2", "act", "text", "val", "month", "cat", "main cat"])
            if element_accname in cashbook_accnames:#check if there are entries in the cashbook for this file
                subframe = cashbook_subset[cashbook_subset['acc_name'] == element_accname] #get subframe of cashbook corresponding to account name

                #do preparations for data filtering
                cashcat_names_subframe = list(subframe["cashcat"].unique())
                start_date = self.basis_data[element_name]['time1'].iloc[-1]
                end_date = self.basis_data[element_name]['time1'].iloc[0]

                #create appendable subframe
                #loop through cash categories and get relevant data points. Set Errorcodes if necessary
                for item in cashcat_names_subframe:
                    if item in list(self.basis_data[element_name]['cat'].unique()): #check if used cash category in cashbook exists in transactions' categories if not set errorcode 05
                        try:
                            subframe_append = subframe[(subframe['cashcat'] == item)&(subframe["time1"].between(start_date, end_date))].copy()
                            subframe_append.drop(subframe_append.columns[[8, 9]], axis=1, inplace=True)
                            subframe_sum = pd.DataFrame([[subframe_append['time1'].iloc[0], subframe_append['time2'].iloc[0], self.langdict['cashbookvars_name'][1], self.langdict['balance_cashbook'][0], abs(sum(subframe_append['val'])), subframe_append['month'].iloc[0], item, self.langdict['cashbookvars_name'][1]]], columns=list(subframe_append.columns))
                            subframe_append = subframe_append.append(subframe_sum, ignore_index=True)
                            element_cashappend = element_cashappend.append(subframe_append, ignore_index=True)
                            if not element_name in cashbook_successlist: #add element name only once
                                cashbook_successlist.append(element_name)
                        except:
                            if not element_name in cashbook_successlist: #add element name only, if it is not in successlist
                                cashbook_errorlist.append(element_name+' (Err06)') # if transaction dates in cashbook and dataframe differ, discard cashbook info and set errorcode 06
                    else:
                        if not element_name in cashbook_successlist: #add element name only, if it is not in successlist
                            cashbook_errorlist.append(element_name+' (Err05)')

            else:
                pass#no action needed

                #append cashbook entries to main data frame
            if element_cashappend.size > 0:
                element_cashappend['acc_name'] = None#add empty account name column to make it compliant to basis data frames
                self.basis_data[element_name] = self.basis_data[element_name].append(element_cashappend, ignore_index=True) #append files
                self.basis_data[element_name].drop_duplicates(subset=['time1', 'time2', 'text', 'val'], inplace=True, ignore_index=True) # drop duplicate entries (determination by time1,  time2 and text)
                self.basis_data[element_name] = self.basis_data[element_name].sort_values('time1', ascending=False).reset_index(drop=True) #sort resulting data frame by time

                del element_cashappend
            else:
                del element_cashappend


        #prepare cashbook entries for plotting
        self.folder_res[cashbook_name] = self.dir_result+cashbook_name
        self.plotting_list[cashbook_name] = 'basic'

        #categorization is done via month-cat-maker-function
        return (cashbook_errorlist, cashbook_successlist)


    def makefolder_excel(self):
        ## Create folders and export data into excel with several subsheets


        for element_name in list(self.folder_res.keys()):
            result_dir = self.folder_res[element_name]

            try:
                if not os.path.exists(result_dir):
                    os.makedirs(result_dir)
            except OSError:
                print('Error: Creating directory. ' + result_dir)

            #set excel writer depending on language choice
            if self.lang_choice == 'deu': #german date format
                writer_excel = pd.ExcelWriter(result_dir+self.folder_sep+element_name+self.langdict['result_pathvars'][1]+'.xlsx', engine='xlsxwriter', datetime_format="dd.mm.yyyy")

            else:#english date format
                writer_excel = pd.ExcelWriter(result_dir+self.folder_sep+element_name+self.langdict['result_pathvars'][1]+'.xlsx', engine='xlsxwriter', datetime_format="yyyy-mm-dd")

            #export data
            if element_name in self.raw_data:
                self.raw_data[element_name].to_excel(writer_excel, sheet_name=self.langdict['sheetname_rawdata'][0], index=False, header=self.raw_data_header[element_name])
            else:#no action needed
                pass

            subcats, main_cats = self.cat_data[element_name] #unpack both subframes //For holiday and savecent main_cats is empty. For cashbook main_cats == acoount names

            if element_name == self.langdict['dataname_savecent'][0]:
                self.basis_data[element_name].to_excel(writer_excel, sheet_name=self.langdict['sheetnames_savecent1'][0], index=False, header=self.langdict['sheetnames_savecent1'][1])
                self.month_data[element_name].to_excel(writer_excel, sheet_name=self.langdict['sheetnames_savecent2'][0], index=False, header=self.langdict['sheetnames_savecent2'][1])
                subcats.to_excel(writer_excel, sheet_name=self.langdict['sheetnames_savecent3'][0], index=False, header=self.langdict['sheetnames_savecent3'][1])


            elif element_name == self.langdict['cashbookvars_name'][0]:

                self.basis_data[element_name].to_excel(writer_excel, sheet_name=self.langdict['sheetnames_cashbook1'][0], index=False, header=self.langdict['sheetnames_cashbook1'][1])

                subcats.to_excel(writer_excel, sheet_name=self.langdict['sheetnames_cashbook2'][0], index=False, header=self.langdict['sheetnames_cashbook2'][1])
                main_cats.to_excel(writer_excel, sheet_name=self.langdict['sheetnames_cashbook3'][0], index=False, header=self.langdict['sheetnames_cashbook3'][1])

            else:
                self.basis_data[element_name].to_excel(writer_excel, sheet_name=self.langdict['sheetname_basis'][0], index=False, header=self.langdict['sheetname_basis'][1])


                if element_name == self.langdict['holidayvars_name'][0]: #handle holidays differently as labeling for subcategories differ (no main cats)

                    subcats.to_excel(writer_excel, sheet_name=self.langdict['sheetname_holidaycatdata'][0], index=False, header=self.langdict['sheetname_holidaycatdata'][1])


                else:

                    main_cats.to_excel(writer_excel, sheet_name=self.langdict['sheetname_maincatdata'][0], index=False, header=self.langdict['sheetname_maincatdata'][1])
                    subcats.to_excel(writer_excel, sheet_name=self.langdict['sheetname_catdata'][0], index=False, header=self.langdict['sheetname_catdata'][1])




            #_______________________________________Adjust formatting of value columns in excel sheets__________________________
            #set  workbook format for transaction values
            bk_format = writer_excel.book.add_format({'num_format': '_-* #,##0.00_-;[Red]-* #,##0.00_-'}) # color payments red and set alg. sign at cell beginning, income is colored black

            for col in (1, 2):
                 # change format of transaction values for outputted "processed data" for all excel exports
                writer_excel.sheets[self.langdict['sheetname_basis'][0]].set_column(4, 4, 10, bk_format) # 'processed data' excel sheet

                #do value formatting for savecent excel file
                if element_name == self.langdict['dataname_savecent'][0]:
                    writer_excel.sheets[self.langdict['sheetname_basis'][0]].set_column(8, 8, 8, bk_format) # savecent column in "processed data"
                    writer_excel.sheets[self.langdict['sheetnames_savecent2'][0]].set_column(1, 1, 8, bk_format) #roundies per month
                    writer_excel.sheets[self.langdict['sheetnames_savecent3'][0]].set_column(col, col, 10, bk_format) #roundies by origin

                #do value formatting for cashbook excel sheets
                elif element_name == self.langdict['cashbookvars_name'][0]:
                    writer_excel.sheets[self.langdict['sheetnames_cashbook2'][0]].set_column(col, col, 10, bk_format) # listing by categories
                    writer_excel.sheets[self.langdict['sheetnames_cashbook3'][0]].set_column(col, col, 10, bk_format) #listing by cash origin

                #do value formatting for holiday excel sheets
                elif element_name == self.langdict['holidayvars_name'][0]:
                    writer_excel.sheets[self.langdict['sheetname_holidaycatdata'][0]].set_column(col, col, 10, bk_format) #listing by categories

                #do value formatting for all other exported excel sheets
                else:
                    writer_excel.sheets[self.langdict['sheetname_catdata'][0]].set_column(col+1, col+1, 10, bk_format) #listing by categories (value columns are 2 and 3)
                    writer_excel.sheets[self.langdict['sheetname_maincatdata'][0]].set_column(col, col, 10, bk_format) #listing by main categories

            #save excel
            writer_excel.save()
