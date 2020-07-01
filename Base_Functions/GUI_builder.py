'''This file has all the relevant information for creating a basic GUI and interact with analyzing scripts'''


from Base_Functions import data_processor

import os
import platform
import sys
import tkinter as tk
from tkinter import messagebox
import tkfilebrowser as tkbrowse

#check which os is running and adjust folder structure
if platform.system()=='Windows':
    homefolder=os.path.expanduser(os.getenv('USERPROFILE'))
    folder_sep='\\'

else:
    folder_sep='/'
    homefolder='~/'



#start Main window to get basic information and do data import
class Main_Window():
    
    def __init__(self):
        
        self.start_window = tk.Tk()


        self.windowWidth = self.start_window.winfo_reqwidth()
        self.windowHeight = self.start_window.winfo_reqheight()


        iconFile='KYSA-Icon_64.ico'
        if not hasattr(sys, "frozen"):
            iconFile = os.path.join(os.getcwd(), iconFile)
        else:
            iconFile = os.path.join(sys.prefix, iconFile)
        
        self.start_window.iconbitmap(default=self.resource_path(iconFile))
 
        # Gets both half the screen width/height and window width/height
        positionRight_main = int(self.start_window.winfo_screenwidth()/3 - self.windowWidth/4)
        positionDown_main = int(self.start_window.winfo_screenheight()/3 - self.windowHeight/4)
 
        #Positions the window in the center of the page.
        self.start_window.geometry(f"+{positionRight_main}+{positionDown_main}")






        #self.start_window.geometry("+400+250")

        self.start_window.protocol("WM_DELETE_WINDOW",self.close_program)

        self.start_window.title("KYSA - Know Your Spendings")
       
        self.importtype_var=tk.StringVar()
        self.holiday_var = tk.IntVar()
        self.savecent_var=tk.IntVar()
        self.csv_concat_var=tk.IntVar()
        self.xlsx_concat_var = tk.IntVar()
        self.filelist=[]
        #start variable
        
        self.importtype_var.set('csv_analyse')
        self.fileextension=4
        self.filetype=("CSV Datei","*.csv")            
        self.infocounter=0
            
        # Create Menu
        menu_container = tk.Menu(self.start_window)
        start_menu = tk.Menu(menu_container, tearoff=0)# Start Menu
        # Order menu entries (Info & quit)
        start_menu.add_command(label="Info", command=self.action_get_info_dialog)
        start_menu.add_separator() # Fügt eine Trennlinie hinzu
        start_menu.add_command(label="Beenden", command=self.close_program)
        # Create Drop-Down Menu
        menu_container.add_cascade(label="Menü", menu=start_menu)
        # integrate menu with window
        self.start_window.config(menu=menu_container)     
        
        
        #create radiobutton for csv/excel choice
        tk.Label(self.start_window, text="Sollen *.csv oder *.xlsx Daten eingelesen werden",justify='left',wraplength=240,pady=10,font='Helvetica 12').grid(rowspan=2,column=0,padx=5, sticky='W')
        tk.Radiobutton(self.start_window, text='csv',variable=self.importtype_var,value='csv_analyse',command=self.set_checkboxes, font='Helvetica  11',padx=8).grid(row=0,column=1, sticky='W')
        tk.Radiobutton(self.start_window, text='xlsx',variable=self.importtype_var,value='xls_analyse',command=self.set_checkboxes,font='Helvetica  11',padx=8).grid(row=1,column=1, sticky='W')

        #create checkbox for holiday extraction
        tk.Label(self.start_window, text="Urlaube separat auswerten",wraplength=240,pady=10,font='Helvetica 12').grid(row=2,column=0,padx=5, sticky='W')
        tk.Checkbutton(self.start_window, variable=self.holiday_var,padx=10,pady=10).grid(row=2,column=1, sticky='W')
        
        #create checkbox for savecent calculation
        tk.Label(self.start_window, text="Sparcents ausgeben (nur csv)",wraplength=240,pady=10,font='Helvetica 12').grid(row=3,column=0,padx=5 , sticky='W')
        self.chk_savecent=tk.Checkbutton(self.start_window, variable=self.savecent_var,padx=10,pady=10)
        self.chk_savecent.grid(row=3,column=1, sticky='W')
        
        #create checbox for csv-concatination
        tk.Label(self.start_window, text="Einzelne csv-Dateien zusätzlich zusammenfassen",wraplength=240,justify='left',pady=10,font='Helvetica 12').grid(row=4,column=0,padx=5, sticky='W')
        self.chk_concatcsv=tk.Checkbutton(self.start_window, variable=self.csv_concat_var,padx=10,pady=10)
        self.chk_concatcsv.grid(row=4,column=1, sticky='W')
        
        #create checkbox for longterm concatination
        tk.Label(self.start_window, text="Aufbereitete Daten zu einer bestehenden Excel-Datei (Langzeitanalyse) hinzufügen",wraplength=240,justify='left',pady=10,font='Helvetica 12').grid(row=5,column=0,padx=5, sticky='W')
        tk.Checkbutton(self.start_window, variable=self.xlsx_concat_var,padx=10,pady=10).grid(row=5,column=1, sticky='W')

        #create Button to browse files
        tk.Button(self.start_window, text="Dateien auswählen", command=self.browse_file,font='Helvetica 12 bold').grid(row=6,columnspan=2,ipady=5,pady=10)

        #create Button to run application
        tk.Button(self.start_window, text="Auswertung starten", command=self.run_application,font='Helvetica 16').grid(row=7,columnspan=2,ipady=10,pady=15)
        
        
        self.start_window.mainloop()

    def resource_path(self,relative_path):    
        try:       
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


        
    def close_program(self):
        self.importtype_var.set('close_program')
        self.start_window.destroy()
    
    #create info menu message
    def action_get_info_dialog(self):
        
            
        infobox = tk.Toplevel()
        infobox.config(bg='white')
        positionRight_info=int(self.start_window.winfo_screenwidth()/2- self.windowWidth/3)
        positionDown_info=int(self.start_window.winfo_screenheight()/3 - self.windowHeight)

        infobox.geometry(f"360x380+{positionRight_info}+{positionDown_info}")
        infobox.title("Über KYSA")

        raw_copycode=Image.open(os.path.join(os.getcwd(),'Base_Functions','Copyrightcode.png')).resize((120,29), Image.ANTIALIAS)
        copycode=ImageTk.PhotoImage(raw_copycode)
        
        banks="\t-------------------------------\n".expandtabs(2)\
        +"\tAktuell unterstützte Banken:\n\n".expandtabs(3)\
        +"\t1) Apobank (Giro)\n".expandtabs(5)\
        +"\t2) comdirect (Giro&Kredit)\n".expandtabs(5)\
        +"\t3) Commerzbank (Giro)\n".expandtabs(5)\
        +"\t4) DKB (Giro&Kredit)\n".expandtabs(5)\
        +"\t5) Deutsche Bank (Giro)\n".expandtabs(5)\
        +"\t6) MLP Bank (Giro)\n".expandtabs(5)\
        +"\t7) Sparkasse (Giro)\n".expandtabs(5)\
        +"\t8) Triodos Bank (Giro)\n".expandtabs(5)\
        +"\t-------------------------------".expandtabs(2)
        
        
        l_title =tk.Label(infobox, text="KYSA\n-\nKnow Your Spendings Application", bg='white',font='Helvetica 15')
        l_version=tk.Label(infobox, text="Version:\tv1.1",bg='white',font='OpenSans  9')
        l_banks=tk.Label(infobox, text=banks,justify='left',bg='white',font='OpenSans 11')
        l_credit=tk.Label(infobox, text="© Daniel Krezdorn 2020",bg='white',font='OpenSans  9')
        l_copyright=tk.Label(infobox, image=copycode)
        l_copyright.image=copycode
        
        l_title.pack(pady=20,fill='x',expand=True)
        l_banks.pack(pady=10,fill='x',expand=True)
        l_version.pack(pady=5,fill='x',expand=True)
        l_credit.pack(pady=5,fill='x',expand=True)


    #create function to adjust values based on importtype decision
    def set_checkboxes(self):
        
        if self.importtype_var.get()=='xls_analyse':
            self.fileextension=5
            self.filetype=("Excel Datei","*.xlsx")
            self.savecent_var.set(0)
            self.csv_concat_var.set(0)            
            self.chk_savecent.config(state='disabled')
            self.chk_concatcsv.config(state='disabled')
            
        else:
            self.fileextension=4
            self.filetype=("CSV Datei","*.csv")
            self.chk_savecent.config(state='normal')
            self.chk_concatcsv.config(state='normal')
            
            
    #create file browsing function
    def browse_file(self):
        if (self.infocounter==0)&(self.importtype_var.get()=='xls_analyse'):
            tk.messagebox.showinfo(message='\nEs können mehrere Dateien auf einmal ausgewählt werden!\n\n\nBitte beachten:\n\nExcel-Dateien, die ausgewertet werden sollen, müssen ein Tabellenblatt "Aufbereitete Daten" in der Formatierung bereits aufbereiteter csv_Dateien haben!\n')
            self.infocounter+=1
        elif (self.infocounter==0):
            tk.messagebox.showinfo(message='\nBitte wählen Sie alle auszuwertenden Dateien auf einmal aus!')
            self.infocounter+=1
            pass
            
        filename_var=tk.StringVar()
        filename_var = tkbrowse.askopenfilenames(initialdir =homefolder, title = "Dateien auswählen", filetypes =(self.filetype,("all files","*.*")))
        #filepathes
        self.filelist=list(filename_var) # use for data import
        if not self.filelist==[]:
            #get directory (double check in windows)
            self.folder_raw=os.path.split(self.filelist[0])[0]

            #extract filenames and create list
            self.filenames=[]
            for path in self.filelist:
                filename=os.path.split(path)[1][:-self.fileextension]
                self.filenames.append((filename,path))
        else:
            pass

    def run_application(self):
        if self.filelist==[]:
            tk.messagebox.showwarning(message='Es wurden keine Dateien ausgewählt!\n\nBitte wählen Sie mindestens eine Datei aus')
        elif (len(self.filelist)==1)&(self.csv_concat_var.get()==1):
        	tk.messagebox.showwarning(message='Es wurde nur eine Datei eingegeben, aber die csv-Zusammenführung gewählt!\n\nBitte wählen Sie mindestens zwei Dateien aus oder wählen die csv-Zusammenführung ab.')
        else:
            #hide main window
            self.start_window.withdraw()
            #start data import via Accounts Data
            #make accountsdata
            self.accounts_data=data_processor.Accounts_Data(self.folder_raw)
    
            successlist=[]
            errorlist=[]
            for item in self.filenames:
                try:
                    self.accounts_data.process_data(item,self.importtype_var.get())
                    successlist.append(item)
            
                except:
                    errorlist.append(item)
    
            if len(errorlist)==len(self.filenames):
                messagetext=f'Es konnte keine der ausgewählten Dateien eingelesen werden!\n\nWählen Sie neue Dateien!'
                tk.messagebox.showerror(message=messagetext)
                self.start_window.deiconify()
       
            else:
                if errorlist==[]:
                    messagetext='Alle Dateien wurden erfolgreich importiert!'
                    tk.messagebox.showinfo(message=messagetext)
                else:
                    successlisttext=('• '+'\n• '.join([successlist[item][0] for item in range(len(successlist))]))
                    errorlisttext=('• '+'\n• '.join([errorlist[item][0] for item in range(len(errorlist))]))
                    messagetext=f'Es wurde:\n\n {successlisttext}\n\nerfolgreich eingelesen.\n\n\nFolgende Dateien konnten nicht eingelesen werden:\n\n{errorlisttext}'
                    tk.messagebox.showinfo(message=messagetext)
                
                self.start_window.destroy()

#--------------info for concat grid



class concat_Window():
    
    def __init__(self,input_list):
        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW",self.skip_concat)
        self.input_list=input_list
        self.root.title("Daten-Zusammenführung")
        #tk.messagebox.showinfo(message='Hier können Sie einzelne csv-Dateien zusammenfügen')
        
        #set variables
        self.cols=4
        self.entrybox=[]
        
        self.chkboxboxes = []
        self.chkboxVars = []

        
        for colid in range(self.cols):
            #initalize checkbox variables
            self.chkboxVars.append([])
            self.chkboxboxes.append([])
            
            #generate entryboxes
            tk.Label(self.root, text= f"Name für Datei {(colid+1)}:",pady=7,font='Helvetica 11').grid(row=len(self.input_list)+2+colid,column=0,padx=5,sticky='w')
            self.entrybox.append(tk.Entry(self.root, state='disabled',font='Helvetica 10',width=50))
            self.entrybox[colid].grid(row=len(self.input_list)+2+colid,column=1,columnspan=4,padx=10,ipady=5,pady=10,sticky='w')
            self.entrybox[0].config(state='normal')
            #generate empty space between blocks
            tk.Label(self.root,pady=8).grid(row=len(self.input_list)+1) 
                
            
            for rowid in range(0,len(self.input_list)):
            

                ##initialize variables checkboxes
                self.chkboxVars[colid].append(tk.IntVar())
                self.chkboxVars[colid][rowid].set(0)


                tk.Label(self.root, text= f"Datei {(colid+1)}",wraplength=80,pady=10,padx=10,font='Helvetica 11').grid(row=0,column=colid+1)
                tk.Label(self.root, text= self.input_list[rowid],pady=10,font='Helvetica 11').grid(row=rowid+1,column=0,padx=5,sticky='w')
                self.chkboxboxes[colid].append(tk.Checkbutton(self.root,variable=self.chkboxVars[colid][rowid],state='disabled'))
                self.chkboxboxes[colid][rowid].grid(row=rowid+1, column=colid+1)
                self.chkboxboxes[colid][rowid].config(command=self.check_columns)
                #enable only first column at beginning
                self.chkboxboxes[0][rowid].config(state='normal')
                
                #generate empty space between blocks
                tk.Label(self.root,pady=8).grid(row=len(self.input_list)+1) 
  
        #create Button to skip or proceed
        tk.Button(self.root, text="Weiter",command=self.proceed_analysis,font='Helvetica 12 bold').grid(row=len(self.input_list)+6,column=2,columnspan=3,ipady=5,pady=10)
        tk.Button(self.root, text="Daten-Zusammenführung abbrechen",command=self.skip_concat,font='Helvetica 12 bold').grid(row=len(self.input_list)+6,columnspan=3,ipady=5,pady=10)
        self.root.mainloop()
    
    def skip_concat(self):
        self.concat_list=[]
        self.root.destroy()
    
    
    def proceed_analysis(self):
        namelist=['na']*self.cols
        self.concat_list=[]
        checklist=[]
        for colid in range(self.cols):
            if not self.entrybox[colid].get()=='':
                if (self.entrybox[colid].get() in namelist) or (self.entrybox[colid].get() in self.input_list):
                    namelist[colid]='errorname'
                else:
                    namelist[colid]=self.entrybox[colid].get()
            #list append checkbox values
            temp=[]
            checklist.append([])
            for rowid in range(0,len(self.input_list)):
                if self.chkboxVars[colid][rowid].get()==1:
                    temp.append(rowid)
            if len(temp)>1:
                  checklist[colid]=temp
        for colid in range(self.cols):
            if not checklist[colid]==[]:
                if namelist[colid]=="na":
                    missingname=1
                else:
                    self.concat_list.append((namelist[colid],checklist[colid]))
                    missingname=0
        #messages before continuation
        if checklist[0]==[]:
            tk.messagebox.showinfo(message='Ihre Auswahl ist unvollständig. Bitte wählen Sie mindestens 2 Dateien aus oder brechen diesen Schritt ab!!')
        
        elif missingname==1:
            tk.messagebox.showinfo(message='Sie haben für Ihre Auswahl keinen Namen eingegeben!')
            
        elif 'errorname' in namelist:
            tk.messagebox.showinfo(message='Sie haben einen Namen eingegeben, der bereits vergeben ist!')
        else:
            if not self.concat_list==[]:
                tk.messagebox.showinfo(message='Die Daten wurden zusammengefügt!')
                self.root.destroy()
        
       
    def check_columns(self):
        selected=[]
        for colid in range(self.cols):
            selected.append([])
            for rowid in range(0,len(self.input_list)):
                if self.chkboxVars[colid][rowid].get()==1:
                    selected[colid].append(rowid)
        
        #turn checkbox on and off depending on previous column
        #turn entrybox on depending on selecion
        
        for colid in range(1,self.cols):
            
            
            if len(selected[colid])>1:
                self.entrybox[colid].config(state='normal')
            else:
                pass
            
            if len(selected[colid-1])>1:
                for rowid in range(0,len(self.input_list)):
                    self.chkboxboxes[colid][rowid].config(state='normal')
            
            else:
                self.entrybox[colid].config(state='disabled')
                for rowid in range(0,len(self.input_list)):
                    self.chkboxVars[colid][rowid].set(0)
                    self.chkboxboxes[colid][rowid].config(state='disabled')
            
            for separ in range(1,self.cols):
                if ((len(selected[colid-(1+separ)])==1) and colid>separ):
                    self.entrybox[colid].config(state='disabled')
                    for rowid in range(0,len(self.input_list)):
                        self.chkboxVars[colid][rowid].set(0)
                        self.chkboxboxes[colid][rowid].config(state='disabled')


#read in excels to concat to other files

import tkinter as tk
from tkinter import messagebox
import os
import tkfilebrowser as tkbrowse

class Longtermimport_Window():
    
    def __init__(self,accounts_data):
        
        self.root = tk.Tk()
        self.accounts_data=accounts_data
        self.folder_raw=accounts_data.folder_raw
        self.root.title('Datei-Import')
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW",self.root.destroy)
        self.filenames=[]
        self.successlist=[]

        
        
        userchoice=tk.messagebox.askokcancel ("Langzeitanalyse", "Bitte wählen Sie im folgenden Schritt die Excel-Dateien für die Langzeitanalyse aus. Die Dateien müssen ein Tabellenblatt 'Aufbereitete Daten' mit einer Formatierung bereits aufbereiteter csv_Dateien haben ")
        
        
        while userchoice:
            self.browse_file()
            if self.filenames==[]:
                if tk.messagebox.askokcancel(message='Wenn Sie abbrechen, wird der Schritt der Datei-Zusammenführung für Langzeitanalysen übersprungen. Möchten Sie dennoch fortfahren?'):
                    break
                else:
                    continue
            else:
                
                errorlist=[]
                for item in self.filenames:
                    try:
                        self.accounts_data.process_data(item,'excel_concat')
                        self.successlist.append(item)
                    except:
                        errorlist.append(item)

                if len(errorlist)==len(self.filenames):
                    messagetext=f'Es konnte keine der ausgewählten Dateien eingelesen werden!\n\nWählen Sie neue Dateien!'
                    tk.messagebox.showerror(message=messagetext)

                    continue

                else:
                    if errorlist==[]:
                        messagetext='Alle Dateien wurden erfolgreich importiert!'
                        tk.messagebox.showinfo(message=messagetext)
                    else:
                        successlisttext=('• '+'\n• '.join([self.successlist[item][0] for item in range(len(self.successlist))]))
                        errorlisttext=('• '+'\n• '.join([errorlist[item][0] for item in range(len(errorlist))]))
                        messagetext=f'Es wurde:\n\n {successlisttext}\n\nerfolgreich eingelesen.\n\n\nFolgende Dateien konnten nicht eingelesen werden:\n\n{errorlisttext}'
                        tk.messagebox.showinfo(message=messagetext)
                    break                         
        
        
        self.root.destroy()
        
    def browse_file(self):

        filename_var=tk.StringVar()
        filename_var=tkbrowse.askopenfilenames(initialdir=self.folder_raw,title="Excel-Dateien für Langzeitanalyse auswählen",filetypes=(("Excel Datei","*.xlsx"),("all files","*.*")))
        
        #filepathes
        
        filelist=list(filename_var) # use for data import
        
        if not filelist==[]:
            #extract filenames and create list
            self.filenames=[]
            for path in filelist:
                filename=os.path.split(path)[1][:-5]
                self.filenames.append((filename,path))
        else:
            pass


#show info about import success
def process_info(messagetext):
    info_window=tk.Tk()
    info_window.withdraw()

    tk.messagebox.showinfo(message=messagetext)
    info_window.destroy
