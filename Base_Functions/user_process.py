import time
import gi
import os
import sys
import platform
import json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from Base_Functions import GUI_GTK_final as guib
from Base_Functions import data_processor as datp

#import pref file

prefs_name="prefs.json"

if not hasattr(sys, "frozen"):
    prefs_path= os.path.join(os.getcwd(),"suppldata", prefs_name)

else:
    prefs_path= os.path.join(sys.prefix,"suppldata", prefs_name)



#--------------------------------------Platform specific constructions-------------------------


#get saved preferences from prefs file. Currently the location of the classtable, the result folder and the home directory is saved for better user experience.
with open(prefs_path, 'r') as f:
    prefs = json.load(f)

startcount=prefs['startcount']

if platform.system()=='Windows':

    if prefs['homedir']["win"]=='':
        home_dir=os.path.expanduser(os.getenv('USERPROFILE'))
    else:
        home_dir=prefs['homedir']["win"]
    #classdir
    if prefs['classdir']["win"]=='':
        class_dir=os.getcwd()
    else:
        class_dir=prefs['classdir']["win"]

    #res_dir
    res_dir=prefs['resdir']["win"]
elif platform.system()=='Linux':
    #import prefs files
    if prefs['classdir']["lin"]=='':
        class_dir=os.getcwd()
    else:
        class_dir=prefs['classdir']["lin"]
    if prefs['homedir']["lin"]=='':
        home_dir=os.path.expanduser('~/')
    else:
        home_dir=prefs['homedir']["lin"]
    #res_dir
    res_dir=prefs['resdir']["lin"]

else:#mac
    if prefs['classdir']["mac"]=='':
        class_dir=os.getcwd()
    else:
        class_dir=prefs['classdir']["mac"]
    if prefs['homedir']["mac"]=='':
        home_dir=os.path.expanduser('~')
    else:
        home_dir=prefs['homedir']["mac"]
    #res_dir
    res_dir=prefs['resdir']["mac"]



#---------------------------------------Message class--------------------------------------------


#this class holds all possible message functions to be called by other functions

class Message_Dialog():
    
    
    def info(self,master,title1,title2):
        #type of dialog and provided text (titles)
        dialog=Gtk.MessageDialog(parent=master,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title1)
        dialog.format_secondary_text(title2)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.run()

        dialog.destroy()
    
    def error(self,master,title1,title2):
        #type of dialog and provided text (titles)
        dialog=Gtk.MessageDialog(parent=master,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title1)
        dialog.format_secondary_text(title2)        
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.run()

        dialog.destroy()
    
    def warning(self,master,title1,title2):
        #type of dialog and provided text (titles)
        dialog=Gtk.MessageDialog(parent=master,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=title1)
        dialog.format_secondary_text(title2)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.run()

        dialog.destroy()
        
    
    def question(self,master,title1,title2):
        #type of dialog and provided text (titles)
        dialog=Gtk.MessageDialog(parent=master,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=title1)
        dialog.format_secondary_text(title2)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        
        response = dialog.run()

        #this message is interactive so it has to return different values depending on user action
        if response == Gtk.ResponseType.OK:
            returnvar=True
        elif response == Gtk.ResponseType.CANCEL:
            returnvar=False
        
        dialog.destroy()
        
        return returnvar

message=Message_Dialog()



#---------------------------------------Main Functions class-----------------------------------------



# main functions reverted on by GUI choices


class Main_Functions():

    def __init__(self,master):

        self.raw_dir=home_dir
        self.class_dir=class_dir
        self.res_dir=res_dir
        self.master=master
        self.filenames=[] #start with empty list of imported raw data

######################################################### File Selection Part #################################
    
    def save_prefs(self):
        # save prefs when proceeding analysis or closing main window
        #sace changes to prefs file
        if platform.system()=='Windows': #windows prefs  

            prefs['resdir']["win"]=self.res_dir
            prefs['homedir']["win"]=self.raw_dir
            prefs['classdir']["win"]=self.class_dir

        elif platform.system()=='Linux': #linux prefs

            prefs['resdir']["lin"]=self.res_dir
            prefs['homedir']["lin"]=self.raw_dir
            prefs['classdir']["lin"]=self.class_dir

        else:#Mac prefs

            prefs['resdir']["mac"]=self.res_dir
            prefs['homedir']["mac"]=self.raw_dir
            prefs['classdir']["mac"]=self.class_dir

        prefs['startcount']=startcount


        with open(prefs_path, 'w') as f:
            json.dump(prefs, f)



    def filebrowser(self,purpose):     
        #open a window for file/folder selection   

        fileextension=5 #default value for data imports
        filetype="xls_analyse"#default value as only difference is csv raw data import
        if purpose=='raw_data_csv':
            dialog = Gtk.FileChooserDialog(title="Csv-Dateien auswählen", parent=self.master,action=Gtk.FileChooserAction.OPEN)
            filetype="csv_analyse"
            fileextension=4
            dialog.set_select_multiple(True)
        elif purpose=='raw_data_excel':
            dialog = Gtk.FileChooserDialog(title="Excel-Dateien auswählen", parent=self.master,action=Gtk.FileChooserAction.OPEN)
                                
            dialog.set_select_multiple(True)

        elif purpose=="concat_longterm":
            dialog = Gtk.FileChooserDialog(title="Excel-Dateien für Verknüfung mit csv-Dateien auswählen", parent=self.master,action=Gtk.FileChooserAction.OPEN)
            
        elif purpose=="cashbook":
            dialog = Gtk.FileChooserDialog(title="Haushaltsbuch-Excel-Datei auswählen", parent=self.master,action=Gtk.FileChooserAction.OPEN)
        
        #folder slection
        elif purpose=='classdir':
            dialog = Gtk.FileChooserDialog(title="Ordner mit Zuordnungstabelle auswählen", parent=self.master,action=Gtk.FileChooserAction.SELECT_FOLDER)
        
        elif purpose=='resdir':
            dialog = Gtk.FileChooserDialog(title="Ablageordner für Ergebnisse auswählen", parent=self.master,action=Gtk.FileChooserAction.SELECT_FOLDER)
        
               #g
        #add relevant buttons
        dialog.resize(200, 150)
        dialog.add_buttons(
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_APPLY,
        Gtk.ResponseType.OK)

        #set current folder, so that the user is brought back to the same folder when opening filebrowser again

        if not (purpose=='classdir' or purpose=='resdir'):
            dialog.set_current_folder(self.raw_dir) #folder which is preselected and will be displayed
            self.add_filters(dialog,filetype)
            response = dialog.run()

        #do filename filepath splitting depending on choice. Splitting is necessary for data import and processing (data_processor.py)
            if response == Gtk.ResponseType.OK:
                self.filenames=[]
                #set filelist as selected files
                filelist=dialog.get_filenames()
                #get directory (double check in windows)
                self.raw_dir=os.path.split(filelist[0])[0]

                #extract filenames and create list
                for path in filelist:
                    filename=os.path.split(path)[1][:-fileextension]
                    self.filenames.append((filename,path))

            elif response == Gtk.ResponseType.CANCEL:
                self.filenames=[]

        else: #different handling for folder selection (classtable and result direction)
            if purpose=='classdir':
                dialog.set_current_folder(self.class_dir) #folder which is preselected and will be displayed

            elif purpose=='resdir':
                dialog.set_current_folder(self.res_dir)#folder which is preselected and will be displayed
            
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                if purpose=='classdir':
                    self.class_dir=dialog.get_filename()
                else:
                    self.res_dir=dialog.get_filename()


            elif response == Gtk.ResponseType.CANCEL:
                if purpose=='classdir':
                    self.class_dir=""
                else:
                    self.res_dir=""

        dialog.destroy()



    def add_filters(self, dialog,filetype): #filters are necessary to display only the desired files in browser
        #add file extension names (csv,xlsx and all)
        if filetype=="csv_analyse":
            filter_csv = Gtk.FileFilter()
            filter_csv.set_name("CSV Dateien")
            filter_csv.add_pattern('*.csv')
            dialog.add_filter(filter_csv)

        elif filetype=="xls_analyse":
            filter_xls = Gtk.FileFilter()
            filter_xls.set_name("Excel Dateien")
            filter_xls.add_mime_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            dialog.add_filter(filter_xls)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Alle Dateien")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
 

######################################################### Data Validation Part #################################

    def start_analysis(self,user_choice):

        self.choice_dtype,self.choice_hol,self.choice_sav,self.choice_conc,self.choice_conc_xls,self.choice_cash=user_choice #tuple unpacking of user selection

        proceed=False #set continuation parameter

        #do check up loops, if necessary raw data was provided by user

        if self.filenames==[]:
            message.error(self.master,'Fehlende Rohdaten','Bitte wählen Sie mindestens eine Datei aus!')
        elif (len(self.filenames)==1) and (self.choice_conc_xls==False and self.choice_conc==True):
            message.warning(self.master,'Unplausible Auswahl','Es wurde nur eine Datei eingegeben, aber die Rohdaten-Zusammenführung gewählt.')
        else:
            #check for classtable being present. if not start classtable selection
            classtbl_success=self.set_classtable('import')

            if classtbl_success:
                if self.res_dir=="":
                    self.res_dir=self.raw_dir
                else:
                    pass #res dir was set by user
                
                #start account analysis class
                self.accounts_data=datp.Accounts_Data(self.res_dir,self.import_classtable)
                
                #do data import check_up
                import_list=self.dataimport_check('raw_data')

                if not import_list==[]: #if import was successful
                
                    proceed=True


                else:
                    pass
            else:#no program start if classtable not importable
                pass       

        return proceed

  

    def dataimport_check(self,purpose):
        # data import is used several times in program. Therefore purpose variable is used

        if purpose=='raw_data':
            importtype=self.choice_dtype

        elif purpose=='concat_longterm':
            importtype='xls_longterm'

        elif purpose=='cashbook':
            importtype='xls_cashbook'

        successlist=[]
        errorlist=[]

        for item in self.filenames:
            
            self.accounts_data.process_data(item,importtype) #does data import, check and classification
            
            ## check if import went through
            if item[0] in self.accounts_data.error_codes.keys():
                errorlist.append(item[0]+' ('+self.accounts_data.error_codes[item[0]]+')')
            
            else:
                successlist.append(item[0])
        
        if successlist==[]:
            BOLD="\033[1m"  ##not used
            errorcodes=', '.join([item for item in list(set(self.accounts_data.error_codes.values()))])
            messagetext=f"Es konnte keine der ausgewählten Dateien verarbeitet werden!\n\nWählen Sie neue Dateien!\n\nFehlercode(s):\n\n({errorcodes})"
            message.error(self.master,'Fehler beim Datenimport!',messagetext)   
        elif errorlist==[]:

            messagetext='Alle Dateien wurden erfolgreich importiert!'
            message.info(self.master,'Datenimport abgeschlossen!',messagetext) 
        
        else:
            successlisttext=('• '+'\n• '.join([item for item in successlist]))
            errorlisttext=('• '+'\n• '.join([item for item in errorlist]))
            messagetext=f'Es wurde:\n\n{successlisttext}\n\nerfolgreich eingelesen.\n\n\nFolgende Dateien konnten nicht verarbeitet werden:\n\n{errorlisttext}'
            message.info(self.master,'Datenimport abgeschlossen!',messagetext) 


        return successlist

######################################################### Extraimport Part #################################

#only used if concat with existent xls file or cashbook was selected

    def excel_extraimport(self,purpose):
        
        import_list=[]

        if purpose=='concat_longterm':
            userchoice=message.question(self.master,'Zusätzliche Excel-Dateien einlesen','Bitte wählen Sie im folgenden Schritt die Excel-Dateien für die Zusammenführung mit den csv-Daten aus oder brechen ab.')
            
        elif purpose=='cashbook':
            userchoice=message.question(self.master,'Haushaltsbuch einlesen','Bitte wählen Sie im folgenden Schritt die Excel-Dateien mit den Bargeldzahlungen aus oder brechen ab.')


        while userchoice:
            self.filebrowser(purpose)
            self.accounts_data.error_codes={} ## empty error-dict while loop is active
            
            if self.filenames==[]:
                break
            else:
                import_list=self.dataimport_check(purpose)

                if import_list==[]:
                    continue
                else:
                    break

        #set method attributes for extra excelimports to be processed by calcculation thread
        if purpose=='cashbook' and not import_list==[]: # if files are imported and cashbook selected start cashbook checkup
            self.cashbook_userinfo()

        elif purpose=='concat_longterm':
            self.longterm_import=import_list #save import list for further processing through process script
        

    def cashbook_userinfo(self):
        #check for entries in cashbook and connect relevant data with imported raw csv-data (done in data_processor.py)

        errorlist_csb,successlist_csb=self.accounts_data.cashbook_calculation()#start cashbook calculation

        #check error and successlist provided by data_processor cashbook function
        if not (errorlist_csb==[] and successlist_csb==[]):
            #give user feedback to cash book evaluation

            if errorlist_csb==[]:  #cashbook data was found and connected for all imported account types
                successlisttext=('• '+'\n• '.join([item for item in successlist_csb]))
                messagetext=f'Zu folgenden importierten Rohdateien konnten passende Daten aus dem Haushaltsbuch hinzugefügt werden:\n\n{successlisttext}'
                message.info(self.master,'Verknüpfung erfolgreich!',messagetext) 
            
            elif successlist_csb==[]: #cashbook data was not found and for any imported account type
                errorlisttext=('• '+'\n• '.join([item for item in errorlist_csb]))
                messagetext=f'Es konnten keine Daten aus dem Haushaltsbuch verknüpft werden.\nFolgende Codes weisen auf die Gründe hin:\n\n{errorlisttext}'
                message.error(self.master,'Verknüpfung fehlgeschlagen',messagetext) 
                
            else: #cashbook data was found and connected for some imported account types
                successlisttext=('• '+'\n• '.join([item for item in successlist_csb]))
                errorlisttext=('• '+'\n• '.join([item for item in errorlist_csb]))
                messagetext=f'Die Verknüpfung von Daten aus dem Haushaltsbuch war für folgende Rohdateien erfolgreich:\n\n{successlisttext}!\n\n\nBei folgende Rohdateien schlug der Abgleich fehl:\n\n{errorlisttext}'
                message.error(self.master,'Verknüpfung teilweise erfolgreich!',messagetext)

        else:
            messagetext='Es wurden für die importierten Rohdaten keine korrespondierenden Daten im Haushaltsbuch gefunden.'
            message.info(self.master,'Keine Verknüpfung erfolgt',messagetext) 

######################################################### Classtable Edit #################################

#set direction for classtable and check if classtable can be read

    def set_classtable(self,purpose):

        if purpose=='import':
            try:
                self.import_classtable=datp.Classifier(self.class_dir)
                classtbl_success=True
            except:
                message.error(self.master,'Zuordnungstabelle nicht gefunden!','Wählen Sie den neuen Ordner, in dem sich die Zuordnungstabelle befindet!')
                classtbl_success=False
        else:
            classtbl_success=False

        while not classtbl_success:
            self.filebrowser('classdir')
            if not self.class_dir=="":
                try:
                    self.import_classtable=datp.Classifier(self.class_dir)
                    message.info(self.master,'Zuordnungstabelle erfolgreich gespeichert!','')
        

                    #break loop    
                    classtbl_success=True
                    break
                except:
                    message.info(self.master,'Fehler beim Import','Im gewählten Ordner wurde keine Zuordnungstabelle gefunden.')
                    continue
            else:
                classtbl_success=False
                break
                

        return classtbl_success



######################################################## Main Data Preprocessing based on user selection ###########################

#this function is called by the Main GUI, when user hits run and all check ups report no error
#it does the necessary preparations (extra data import for cashbook and concatenation) and savecent/holiday calculations
#Main GUI Window is closed after successful function execution


    def data_preparation(self):
        
        #show progressbar throughout function
        progress=guib.ProgressBarWindow() 

        #action for cashbook
        if self.choice_cash==True:
            self.excel_extraimport('cashbook')
            
        # #concat holiday data
        if self.choice_hol==True:
            self.accounts_data.bundle_holiday()
        
        #action if savecent_calculation if selected
        if self.choice_sav==True:
            self.accounts_data.savecent_calculation()

        #concat data if selected
        if self.choice_conc==True or self.choice_conc_xls==True:
            ##import long term excel if selected
            progress.activity_mode=False #stop pulsation of progressbar
            self.longterm_import=[]
            if self.choice_conc_xls==True: #import existing excels for concatenation
                self.excel_extraimport('concat_longterm')

            processed_files=list(self.accounts_data.folder_res.keys())
            exclude_list=["Sparcents","Haushaltsbuch"] #exclude davecents and cashbooks from concat choice, as these can't be merged with existing data
            for item in exclude_list:
                if item in processed_files:
                    processed_files.remove(item) #get sublist without savecent/cashbook
            else:
                pass 

            concat_basislist=processed_files+self.longterm_import  #longterm import list created in progress script

            #open concat window
            concat_choice=guib.Concat_Window(concat_basislist)
            Gtk.main()#makes process halt until concat window is closed
            
            progress.activity_mode=True #restart pulsation of progressbar

            if not concat_choice.concat_list==[]:
                self.accounts_data.concatter(concat_choice.concat_list) # do concatenation, if choice was entered correctly by user
                   
        else:#no action needed
            pass

        #start subprocess of data processing, making categorical and monthly grouping and sorting (data_processor.py) 
        self.accounts_data.month_cat_maker()
        progress.close()

        
