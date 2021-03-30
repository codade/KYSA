'''User Process script handles all inputs from the user, loads saved data and starts the relevant data processing functions, when necessary'''

import json
import os
import platform
import sys
import shutil
import gi
gi.require_version('Gtk', '3.0')

from cryptography.fernet import Fernet
from gi.repository import Gtk


from basefunctions import classifier
from basefunctions import data_processor as datp
from basefunctions import lang_script



#get path of home folder and define KYSA path for user data
if platform.system() == 'Windows':
    HOME_PATH = os.path.abspath(os.path.expanduser('~')) #homefolder
    PATH_KYSADIR = os.path.join(os.path.abspath(os.environ['LOCALAPPDATA']), 'KYSA') #local appdata folder

elif platform.system() == 'Darwin':
    HOME_PATH = os.path.expanduser('~/') #homnefolder
    PATH_KYSADIR = os.path.join(HOME_PATH, 'Library', 'Kysa') #user subfolder in Library main folder 

else:
    HOME_PATH = os.path.expanduser('~/') #homnefolder
    PATH_KYSADIR = os.path.join(HOME_PATH, '.kysa') #user folder


# Create Imports Paths
if not getattr(sys, 'frozen', False):
    #get local folder path for subfolder 'suppldata' if GUI Window is not frozen
    PATH_SUPPLDATA = os.path.join(os.getcwd(), 'suppldata')    
    PATH_WORKINGFLD = os.getcwd()    

else:
    #get local folder path for subfolder 'suppldata' if GUI Window is frozen
    PATH_SUPPLDATA = os.path.join(sys.prefix, 'suppldata')

    if platform.system() != 'Darwin':
        PATH_WORKINGFLD = os.getcwd() #current dir == in Windows where Main-Exe is located
    #Since Mac apps are a kind of folder and the exe is located three levels down inside the folder, one has to go up three levels to get the working folder
    else:
        #PATH_WORKINGFLD = os.path.abspath(sys.executable+'/../../../../') #needed for Excel Tables. Currently not working in Mac
        PATH_WORKINGFLD = os.getcwd()


PATH_PROGRESS_PIC = os.path.join(PATH_SUPPLDATA, 'KYSA-Progress_pic.png')
#set user data and protect key path, create the folder if not existing and copy user files into it
PATH_USERDATA = os.path.join(PATH_KYSADIR, 'userdata')
PATH_FOLDERKEY = os.path.join(PATH_USERDATA, 'suppl', 'protect')

if not os.path.exists(PATH_FOLDERKEY): #check if key folder exists
    os.makedirs(PATH_FOLDERKEY) # create key file folder if not existing and recursively all folders before (including user data folder)

    #copy user data files delivered with program in suppldata folder to newly created user data folder
    #get paths of relevant data
    PREFS_INAPP = os.path.join(PATH_SUPPLDATA, 'prefs.json')
    TRAINDATA_INAPP = os.path.realpath(os.path.join(PATH_SUPPLDATA, 'history_traindata.csv'))
    LONGTERMDATA_INAPP = os.path.join(PATH_SUPPLDATA, 'longterm_data.csv')
    PREFS_USERDATDIR = os.path.join(PATH_USERDATA, 'prefs.json')
    TRAINDATA_USERDATDIR = os.path.join(PATH_USERDATA, 'history_traindata.csv')
    LONGTERMDATA_USERDATDIR = os.path.join(PATH_USERDATA, 'longterm_data.csv')
    #copy files
    shutil.copy2(PREFS_INAPP, PREFS_USERDATDIR) #copy prefs file
    shutil.copy2(TRAINDATA_INAPP, TRAINDATA_USERDATDIR) #copy traindata file
    shutil.copy2(LONGTERMDATA_INAPP, LONGTERMDATA_USERDATDIR) #copy longterm data file

    
else:
    pass

#filepath for encryption key
PATH_ENCKEY = os.path.join(PATH_FOLDERKEY, 'history_data.key') 

#load preferences
PATH_PREFS = os.path.join(PATH_USERDATA, 'prefs.json')
PATH_TRAINDATA_ENCR = os.path.join(PATH_USERDATA, 'history_traindata.csv') # path to training data for machine classifier encrypted
PATH_TRAINDATA_DECR = os.path.join(PATH_USERDATA, 'history_traindata_decrypted.csv') # path to training data for machine classifier decrypted
PATH_LONGTERMDATA_ENCR = os.path.join(PATH_USERDATA, 'longterm_data.csv') # path to saved longterm data encrypted
PATH_LONGTERMDATA_DECR = os.path.join(PATH_USERDATA, 'longterm_data_decrypted.csv')

#--------------------------------------Platform specific constructions-------------------------

#get saved preferences from prefs file. Currently the location of the classtable, the result folder and the home directory is saved for better user experience.
with open(PATH_PREFS, 'r') as pref_load:
    PREFS = json.load(pref_load)

STARTCOUNT = PREFS['startcount']

LANG_CHOICE = PREFS['lang_set']#language choice

CURRENCY_CHOICE = PREFS['currency_set'] #currency sign

DEVEL_MODE = PREFS['devel_mode'] #development mode prevents deletion of decrypted longterm / history_traindata

ACCOUNT_NAMES = PREFS['accnames'] #account names

#-----------------------------------------Choose Dictionary set currency and integrate cryptokey-----------------------


#initialiselang class

LANGDICT_CLASS = lang_script.LanguageDictionary(CURRENCY_CHOICE)

if LANG_CHOICE == 'eng':
    LANGDICT_USED = LANGDICT_CLASS.lang_eng
else:
    LANGDICT_USED = LANGDICT_CLASS.lang_deu

LANGDICT_MFUNC = LANGDICT_USED['Main_Func_vars']

#Generate encryption key with first startup:

try:
    #load key if existing (relevant also for STARTCOUNT==0)
    KEYFILE = open(PATH_ENCKEY, 'rb')
    KEY_TRAINDATA = KEYFILE.read()
except:
    #create new key
    KEY_TRAINDATA = Fernet.generate_key()
    KEYFILE = open(PATH_ENCKEY, 'wb') #wb = write bytes
    KEYFILE.write(KEY_TRAINDATA)
    KEYFILE.close()
    #try hiding file (currrently only working under Windows)
    os.system(f' attrib +h "{PATH_ENCKEY}"')


#-----------------------------------------Import Platform specific values---------------------


if platform.system() == 'Windows':

    if PREFS['lastusedir']['win'] == '':
        DIR_LASTUSE = HOME_PATH
    else:
        DIR_LASTUSE = PREFS['lastusedir']['win']
    #classdir
    if PREFS['classdir']['win'] == '':
        DIR_CLASSTBL = PATH_WORKINGFLD+'\\Excel-Tables'
    else:
        DIR_CLASSTBL = PREFS['classdir']['win']

    #res_dir
    DIR_RESULT = PREFS['resdir']['win']
elif platform.system() == 'Linux':
    #import PREFS files
    if PREFS['classdir']['lin'] == '':
        DIR_CLASSTBL = PATH_WORKINGFLD+'/Excel-Tables'
    else:
        DIR_CLASSTBL = PREFS['classdir']['lin']

    if PREFS['lastusedir']['lin'] == '':
        DIR_LASTUSE = HOME_PATH
    else:
        DIR_LASTUSE = PREFS['lastusedir']['lin']
    #DIR_RESULT
    DIR_RESULT = PREFS['resdir']['lin']

else:#mac

    if PREFS['classdir']['mac'] == '':
        DIR_CLASSTBL = PATH_WORKINGFLD+'/Excel-Tables'
    else:
        DIR_CLASSTBL = PREFS['classdir']['mac']
    if PREFS['lastusedir']['mac'] == '':
        DIR_LASTUSE = HOME_PATH
    else:
        DIR_LASTUSE = PREFS['lastusedir']['mac']
    #DIR_RESULT
    DIR_RESULT = PREFS['resdir']['mac']




#---------------------------------------Message class--------------------------------------------


#this class holds all possible message functions to be called by other functions

class UserMessageDialog():


    def info(self, master, title1, title2):
        #type of dialog and provided text (titles)
        dialog = Gtk.MessageDialog(parent=master,
                                   flags=0,
                                   message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK,
                                   text=title1)
        dialog.format_secondary_text(title2)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.run()

        dialog.destroy()

    def error(self, master, title1, title2):
        #type of dialog and provided text (titles)
        dialog = Gtk.MessageDialog(parent=master,
                                   flags=0,
                                   message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.OK,
                                   text=title1)
        dialog.format_secondary_text(title2)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.run()

        dialog.destroy()

    def warning(self, master, title1, title2):
        #type of dialog and provided text (titles)
        dialog = Gtk.MessageDialog(parent=master,
                                   flags=0,
                                   message_type=Gtk.MessageType.WARNING,
                                   buttons=Gtk.ButtonsType.OK,
                                   text=title1)
        dialog.format_secondary_text(title2)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.run()

        dialog.destroy()


    def question(self, master, title1, title2):
        #type of dialog and provided text (titles)
        dialog = Gtk.MessageDialog(parent=master,
                                   flags=0,
                                   message_type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.OK_CANCEL,
                                   text=title1)
        dialog.format_secondary_text(title2)
        dialog.set_position(Gtk.WindowPosition.CENTER)

        response = dialog.run()

        #this message is interactive so it has to return different values depending on user action
        if response == Gtk.ResponseType.OK:
            returnvar = True
        elif response == Gtk.ResponseType.CANCEL:
            returnvar = False

        dialog.destroy()

        return returnvar

message = UserMessageDialog()



#---------------------------------------Main Functions class-----------------------------------------



# main functions reverted on by GUI choices


class MainFunctions():

    def __init__(self, master):

        self.raw_dir = DIR_LASTUSE
        self.dir_classtbl = DIR_CLASSTBL
        self.dir_result = DIR_RESULT
        self.master = master
        self.filenames = [] #start with empty list of imported raw data
        self.decrypt_datasets()


######################################################### File Selection Part #################################

    def save_prefs(self):
        # save prefs when proceeding analysis or closing main window
        #save changes to prefs file
        if platform.system() == 'Windows':#windows prefs

            PREFS['resdir']['win'] = self.dir_result
            PREFS['lastusedir']['win'] = self.raw_dir
            PREFS['classdir']['win'] = self.dir_classtbl

        elif platform.system() == 'Linux': #linux prefs

            PREFS['resdir']['lin'] = self.dir_result
            PREFS['lastusedir']['lin'] = self.raw_dir
            PREFS['classdir']['lin'] = self.dir_classtbl

        else:#Mac prefs

            PREFS['resdir']['mac'] = self.dir_result
            PREFS['lastusedir']['mac'] = self.raw_dir
            PREFS['classdir']['mac'] = self.dir_classtbl

        PREFS['startcount'] = STARTCOUNT
        PREFS['lang_set'] = LANG_CHOICE
        PREFS['currency_set'] = CURRENCY_CHOICE
        PREFS['accnames'] = ACCOUNT_NAMES
        with open(PATH_PREFS, 'w') as pref_save:
            json.dump(PREFS, pref_save)



    def filebrowser(self, purpose):
        #open a window for file/folder selection

        fileextension = 5 #default value for data imports
        filetype = 'xls_analyse'#default value as only difference is csv raw data import
        if purpose == 'raw_data_csv':
            dialog = Gtk.FileChooserDialog(title=LANGDICT_MFUNC['filechooser_csv'][0], parent=self.master, action=Gtk.FileChooserAction.OPEN)
            filetype = 'csv_analyse'
            fileextension = 4
            dialog.set_select_multiple(True)
        elif purpose == 'raw_data_excel':
            dialog = Gtk.FileChooserDialog(title=LANGDICT_MFUNC['filechooser_xlsx'][0], parent=self.master, action=Gtk.FileChooserAction.OPEN)

            dialog.set_select_multiple(True)

        elif purpose == 'concat_longterm':
            dialog = Gtk.FileChooserDialog(title=LANGDICT_MFUNC['filechooser_longterm'][0], parent=self.master, action=Gtk.FileChooserAction.OPEN)

        elif purpose == 'cashbook':
            dialog = Gtk.FileChooserDialog(title=LANGDICT_MFUNC['filechooser_cashbook'][0], parent=self.master, action=Gtk.FileChooserAction.OPEN)

        #folder slection
        elif purpose == 'classdir':
            dialog = Gtk.FileChooserDialog(title=LANGDICT_MFUNC['filechooser_classdir'][0], parent=self.master, action=Gtk.FileChooserAction.SELECT_FOLDER)

        elif purpose == 'resdir':
            dialog = Gtk.FileChooserDialog(title=LANGDICT_MFUNC['filechooser_resdir'][0], parent=self.master, action=Gtk.FileChooserAction.SELECT_FOLDER)

               #g
        #add relevant buttons
        dialog.resize(200, 150)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_APPLY,
            Gtk.ResponseType.OK)

        #set current folder, so that the user is brought back to the same folder when opening filebrowser again

        if not purpose in ('classdir', 'resdir'):
            dialog.set_current_folder(self.raw_dir) #folder which is preselected and will be displayed
            self.add_filters(dialog, filetype)
            response = dialog.run()

        #do filename filepath splitting depending on choice. Splitting is necessary for data import and processing (data_processor.py)
            if response == Gtk.ResponseType.OK:
                self.filenames = []
                #set filelist as selected files
                filelist = dialog.get_filenames()
                #get directory (double check in windows)
                self.raw_dir = os.path.split(filelist[0])[0]

                #extract filenames and create list
                for path in filelist:
                    filename = os.path.split(path)[1][:-fileextension]
                    self.filenames.append((filename, path)) 

            elif response == Gtk.ResponseType.CANCEL:
                self.filenames = []

        else: #different handling for folder selection (classtable and result direction)
            if purpose == 'classdir':
                dialog.set_current_folder(self.dir_classtbl) #folder which is preselected and will be displayed

            elif purpose == 'resdir':
                dialog.set_current_folder(self.dir_result)#folder which is preselected and will be displayed

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if purpose == 'classdir':
                    self.dir_classtbl = dialog.get_filename()
                else:
                    self.dir_result = dialog.get_filename()


            elif response == Gtk.ResponseType.CANCEL:
                if purpose == 'classdir':
                    self.dir_classtbl = ''
                else:
                    self.dir_result = ''

        dialog.destroy()



    def add_filters(self, dialog, filetype): #filters are necessary to display only the desired files in browser
        #add file extension names (csv,xlsx and all)
        if filetype == 'csv_analyse':
            filter_csv = Gtk.FileFilter()
            filter_csv.set_name(LANGDICT_MFUNC['filechooser_filter1'][0])
            filter_csv.add_pattern('*.csv')
            dialog.add_filter(filter_csv)

        elif filetype == 'xls_analyse':
            filter_xls = Gtk.FileFilter()
            filter_xls.set_name(LANGDICT_MFUNC['filechooser_filter2'][0])
            filter_xls.add_mime_type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            dialog.add_filter(filter_xls)

        filter_any = Gtk.FileFilter()
        filter_any.set_name(LANGDICT_MFUNC['filechooser_filter3'][0])
        filter_any.add_pattern('*')
        dialog.add_filter(filter_any)



######################################################### Transaction History Encryption Part #################################

    def decrypt_datasets(self):

        #decrypt historic data

        #files must be present!
        with open(PATH_TRAINDATA_ENCR, 'rb') as train_encr_load: #open transaction history
            traindata_encr = train_encr_load.read()

        with open(PATH_LONGTERMDATA_ENCR, 'rb') as longterm_encr_load: #open long term data history
            longtermdata_encr = longterm_encr_load.read()

        try:#try decrypting training and longterm data files
                #decrypt data
            fernet = Fernet(KEY_TRAINDATA)
            traindata_decr = fernet.decrypt(traindata_encr)
            longtermdata_decr = fernet.decrypt(longtermdata_encr)
            decrypt_success = True

        except:
            #decryption doesn't work (also if STARTCOUNT == 0)
            traindata_decr = traindata_encr
            longtermdata_decr = longtermdata_encr
            #adaption for first startup with german language as decrypted basis history dataset exists for this language
            if STARTCOUNT == 0 and LANG_CHOICE == 'deu': #The existing basis history dataset will be read-in
                decrypt_success = True
            else:# not STARTCOUNT = 0 or german language set but sill error
                decrypt_success = False

        #write files as decrypted csv to read it in in classifier and data processor functions
        with open(PATH_TRAINDATA_DECR, 'wb') as train_decr_save:
            train_decr_save.write(traindata_decr)

        with open(PATH_LONGTERMDATA_DECR, 'wb') as longterm_decr_save:
            longterm_decr_save.write(longtermdata_decr)

        #import training data and saved longterm data
        training_data = classifier.traindata_import(PATH_TRAINDATA_DECR, decrypt_success, LANG_CHOICE)
        self.saved_dataframe = datp.longtermdata_import(PATH_LONGTERMDATA_DECR, decrypt_success)

        #delete temporarly saved dexrypted files
        os.remove(PATH_TRAINDATA_DECR)#delete decrypted history data file
        os.remove(PATH_LONGTERMDATA_DECR)#delete decrypted longterm data file

        # initialise machine learning algorithm
        self.init_machineclassifier = classifier.MachineClassifier(training_data, LANG_CHOICE) #initaliaze machine learning classifier with training data



    def encrypt_datasets(self):
        #save history data to temporary csv-file
        self.init_machineclassifier.traindata_export(PATH_TRAINDATA_DECR) #function to save altered training data

        datp.longterm_export(PATH_LONGTERMDATA_DECR, self.saved_dataframe)
        #  Open the generated training data file to encrypt it
        with open(PATH_TRAINDATA_DECR, 'rb') as train_decr_load:
            traindata_decr = train_decr_load.read()

        with open(PATH_LONGTERMDATA_DECR, 'rb') as longterm_decr_load:
            longtermdata_decr = longterm_decr_load.read()

        #check for development mode and if False delte decrypted data
        if not DEVEL_MODE:
            os.remove(PATH_TRAINDATA_DECR) #delete decrypted history data
            os.remove(PATH_LONGTERMDATA_DECR) #delete decrypted history data
        else:
            pass #nothing to do

        #encrypt files
        fernet = Fernet(KEY_TRAINDATA)
        traindata_encr = fernet.encrypt(traindata_decr)
        longtermdata_encr = fernet.encrypt(longtermdata_decr)

        # Write the encrypted data files to csvs
        with open(PATH_TRAINDATA_ENCR, 'wb') as train_encr_save:
            train_encr_save.write(traindata_encr)

        with open(PATH_LONGTERMDATA_ENCR, 'wb') as longterm_encr_save:
            longterm_encr_save.write(longtermdata_encr)

######################################################### Data Validation Part #################################

    def start_analysis(self, user_choice):

        self.choice_dtype, self.choice_hol, self.choice_sav, self.choice_conc, self.choice_cash, self.choice_longterm, self.choice_conc_xls = user_choice #tuple unpacking of user selection
        proceed = False #set continuation parameter

        #set result folder
        if self.dir_result == '':
            self.dir_result = self.raw_dir
        else:
            pass #res dir was set by user

        if self.classtbl_success:
             #start analysis if longterm data was selected and no raw files were chosen
            if self.choice_longterm and self.filenames == []: #if only longterm analysis is selected (no imported files) and saved data is existing
                self.accounts_data = datp.AccountsData(self.dir_result, self.classifier_process, LANGDICT_USED['Data_Proc_vars'], self.saved_dataframe)
                proceed = True
                self.data_preparation() #start data preparation

            #if above condition does not hold start check-ups and if successful analysis
            else: #normal data import and analysis checkups
                #do check up loops, if necessary raw data was provided by user
                #give message and stop analysis if no file was selected
                if self.filenames == []:
                    message.error(self.master, LANGDICT_MFUNC['start_analysis_err1'][0], LANGDICT_MFUNC['start_analysis_err1'][1])

                #give message and stop analysis process if concatination is selected and only one file is selected with no extra excel import or longterm-data
                elif (len(self.filenames) == 1) and (not self.choice_conc_xls and self.choice_conc) and not self.choice_longterm:
                    message.warning(self.master, LANGDICT_MFUNC['start_analysis_err2'][0], LANGDICT_MFUNC['start_analysis_err2'][1])

                else:

                    #start account analysis class
                    self.accounts_data = datp.AccountsData(self.dir_result, self.classifier_process, LANGDICT_USED['Data_Proc_vars'], self.saved_dataframe)

                    message.info(self.master, LANGDICT_MFUNC['start_analysis_info'][0], LANGDICT_MFUNC['start_analysis_info'][1])
                    
                    #create data import tuple
                    import_datatuple = (self.accounts_data, self.filenames, self.choice_dtype)

                    #start import in subprocess
                    self.master.progresswin.queue.put(('rawimport_start', import_datatuple))
                    proceed = True

        else:#no program start if classtable not imported
            self.set_classtable('import') #try import of classtable


        return proceed


    def dataimport_check(self):
        # data import is used several times in program. Therefore purpose variable is used

        successlist = []
        errorlist = []


        for item in self.filenames:
            ## check if import went through
            if item[0] in self.accounts_data.error_codes.keys():
                errorlist.append(item[0]+' ('+self.accounts_data.error_codes[item[0]]+')')

            else:
                successlist.append(item[0])

        if successlist == []:

            errorcodes = ', '.join([item for item in list(set(self.accounts_data.error_codes.values()))])
            message.error(self.master, LANGDICT_MFUNC['importcheck_err'][0], eval(f"f'''{LANGDICT_MFUNC['importcheck_err'][1]}'''"))   #eval function transforms f-string statements to be interpreted as f-strings

        elif errorlist == []:

            message.info(self.master, LANGDICT_MFUNC['importcheck_succall'][0], LANGDICT_MFUNC['importcheck_succall'][1])

        else:
            successlisttext = ('• '+'\n• '.join([item for item in successlist]))
            errorlisttext = ('• '+'\n• '.join([item for item in errorlist]))
            message.info(self.master, LANGDICT_MFUNC['importcheck_succpart'][0], eval(f"f'''{LANGDICT_MFUNC['importcheck_succpart'][1]}'''")) #eval function transforms f-string statements to be interpreted as f-strings


        return successlist

######################################################### Extraimport Part #################################

#only used if concat with existent xls file or cashbook was selected

    def excel_extraimport(self, purpose):

        import_list = []

        if purpose == 'concat_longterm':
            userchoice = message.question(self.master, LANGDICT_MFUNC['extraimport_longterm'][0], LANGDICT_MFUNC['extraimport_longterm'][1])
            importtype = 'xls_longterm'

        elif purpose == 'cashbook':
            userchoice = message.question(self.master, LANGDICT_MFUNC['extraimport_cashbook'][0], LANGDICT_MFUNC['extraimport_cashbook'][1])
            importtype = 'xls_cashbook'


        while userchoice:
            self.filebrowser(purpose)
            self.accounts_data.error_codes = {} ## empty error-dict while loop is active

            if self.filenames == []:
                break
            else:
                for item in self.filenames:
                    self.accounts_data.process_data(item, importtype)
                import_list = self.dataimport_check()

                if import_list == []:
                    continue
                else:
                    break

        #set method attributes for extra excelimports to be processed by calcculation thread
        if purpose == 'cashbook' and import_list != []: # if files are imported and cashbook selected start cashbook checkup
            self.cashbook_userinfo()

        elif purpose == 'concat_longterm':
            self.longterm_import = import_list #save import list for further processing through process script


    def cashbook_userinfo(self):
        #check for entries in cashbook and connect relevant data with imported raw csv-data (done in data_processor.py)

        errorlist_csb, successlist_csb = self.accounts_data.cashbook_calculation()#start cashbook calculation

        #check error and successlist provided by data_processor cashbook function
        if errorlist_csb != [] or successlist_csb != []:
            #give user feedback to cash book evaluation

            if errorlist_csb == []:  #cashbook data was found and connected for all imported account types
                successlisttext = ('• '+'\n• '.join([item for item in successlist_csb]))
                message.info(self.master, LANGDICT_MFUNC['cashbookinfo_succ'][0], eval(f"f'''{LANGDICT_MFUNC['cashbookinfo_succ'][1]}'''")) #eval function transforms f-string statements to be interpreted as f-strings

            elif successlist_csb == []: #cashbook data was not found and for any imported account type
                errorlisttext = ('• '+'\n• '.join([item for item in errorlist_csb]))
                message.error(self.master, LANGDICT_MFUNC['cashbookinfo_err'][0], eval(f"f'''{LANGDICT_MFUNC['cashbookinfo_err'][1]}'''")) #eval function transforms f-string statements to be interpreted as f-strings

            else: #cashbook data was found and connected for some imported account types
                successlisttext = ('• '+'\n• '.join([item for item in successlist_csb]))
                errorlisttext = ('• '+'\n• '.join([item for item in errorlist_csb]))
                message.error(self.master, LANGDICT_MFUNC['cashbookinfo_succpart'][0], eval(f"f'''{LANGDICT_MFUNC['cashbookinfo_succpart'][1]}'''")) #eval function transforms f-string statements to be interpreted as f-strings

        else:

            message.info(self.master, LANGDICT_MFUNC['cashbookinfo_nodata'][0], LANGDICT_MFUNC['cashbookinfo_nodata'][1])

######################################################### Classtable Edit #################################

#set direction for classtable and check if classtable can be read

    def set_classtable(self, purpose):

        if purpose == 'import':
            try:
                self.classifier_process = classifier.ClassificationProcess(self.dir_classtbl, self.init_machineclassifier, LANGDICT_USED['Classifier_vars'])
                self.classtbl_success = True
            except:
                message.error(self.master, LANGDICT_MFUNC['classtableimport_notexist'][0], LANGDICT_MFUNC['classtableimport_notexist'][1])
                self.classtbl_success = False
        else:
            self.classtbl_success = False

        while not self.classtbl_success:
            self.filebrowser('classdir')
            if self.dir_classtbl != '':
                try:
                    self.classifier_process = classifier.ClassificationProcess(self.dir_classtbl, self.init_machineclassifier, LANGDICT_USED['Classifier_vars'])
                    message.info(self.master, LANGDICT_MFUNC['classtableimport_succ'][0], LANGDICT_MFUNC['classtableimport_succ'][1])

                    #break loop
                    self.classtbl_success = True
                    break
                except:
                    message.info(self.master, LANGDICT_MFUNC['classtableimport_err'][0], LANGDICT_MFUNC['classtableimport_err'][1])
                    continue
            else:
                self.classtbl_success = False
                break



######################################################## Main Data Preprocessing based on user selection ###########################

#this function is called by the Main GUI, when user hits run and all check ups report no error
#it does the necessary preparations (extra data import for cashbook and concatenation) and savecent/holiday calculations
#Main GUI Window is closed after successful function execution

    def data_preparation(self):
        #inform user that data preparation starts
        message.info(self.master, LANGDICT_MFUNC['data_prep_start'][0], LANGDICT_MFUNC['data_prep_start'][1])
        self.master.progresswin.activity_mode = True
        #show progressbar throughout function
        
        if self.choice_longterm: #extract saved data and evaluate it
            self.accounts_data.longterm_evaluate()
        #action for cashbook
        if self.choice_cash:
            self.master.progresswin.activity_mode = False
            self.excel_extraimport('cashbook')
            self.master.progresswin.activity_mode = True

        # #concat holiday data
        if self.choice_hol:
            self.accounts_data.bundle_holiday()

        #action if savecent_calculation if selected
        if self.choice_sav:
            self.accounts_data.savecent_calculation()

        #concat data if selected
        if self.choice_conc or self.choice_conc_xls:
            ##import long term excel if selected
            self.master.progresswin.activity_mode = False #stop pulsation of progressbar
            self.longterm_import = []
            if self.choice_conc_xls: #import existing excels for concatenation
                self.excel_extraimport('concat_longterm')

            processed_files = list(self.accounts_data.folder_res.keys())
            exclude_list = [LANGDICT_MFUNC['excludelist'][0], LANGDICT_MFUNC['excludelist'][1]] #exclude davecents and cashbooks from concat choice, as these can't be merged with existing data
            for item in exclude_list:
                if item in processed_files:
                    processed_files.remove(item) #get sublist without savecent/cashbook

            concat_basislist = processed_files+self.longterm_import  #longterm import list created in progress script

            #open concat window
            #check if concat_basislist has more than one entry:
            if len(concat_basislist) > 1:
                concat_choice = self.master.open_concatwindow(concat_basislist)
                concat_choicelist = concat_choice.concat_list
            else:
                concat_choicelist = [] #skip concatting and create empty list

            self.master.progresswin.activity_mode = True #restart pulsation of progressbar

            if concat_choicelist != []:
                self.accounts_data.concatter(concat_choicelist) # do concatenation, if choice was entered correctly by user

            else:
                pass
        else:#no action needed
            pass

        # update long-term data with freshly added data
        self.saved_dataframe = self.accounts_data.longterm_savedata()

        #start subprocess of data processing, making categorical and monthly grouping and sorting (data_processor.py)
        self.accounts_data.month_cat_maker()
        
        self.master.progresswin.queue.put(('start_export', self.accounts_data)) #start plotting in subprocess #set starting signal for plotting process

