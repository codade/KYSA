'''This file has all the relevant information for creating a basic GUI and interact with analyzing scripts'''


from Base_Functions import data_processor as datp

import os
from PIL import ImageTk, Image
import platform
import sys
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import tkfilebrowser as tkbrowse
import webbrowser

#check which os is running and adjust folder structure
if platform.system()=='Windows':
    homefolder=os.path.expanduser(os.getenv('USERPROFILE'))
    padx_os=10
    lmargin2_os=9
else:
    padx_os=7
    homefolder='~/'
    lmargin2_os=14

 # Icon Name   
    



#start Main window to get basic information and do data import
class Main_Window():
    
    def __init__(self):
        
        self.start_window = tk.Tk()

        self.windowWidth = self.start_window.winfo_reqwidth()
        self.windowHeight = self.start_window.winfo_reqheight()
        # self.progres_root=tk.Toplevel()
        # self.progres_root.withdraw()
        
        iconFile_name='KYSA-Icon2.ico'

        if not hasattr(sys, "frozen"):
            iconFile = os.path.join(os.getcwd(),"suppldata", iconFile_name)
        else:
            iconFile = os.path.join(sys.prefix,"suppldata", iconFile_name)
        
        if platform.system()=='Windows':
            self.start_window.iconbitmap(default=self.resource_path(iconFile))
        else:
            linux_img = ImageTk.PhotoImage(Image.open(iconFile))
            self.start_window.iconphoto(True, linux_img)


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
        self.concat_var_single=tk.IntVar()
        self.longterm_select = tk.IntVar()
        
        #start variable
        
        self.importtype_var.set('csv_analyse')
        self.fileextension=4
        self.filetype=("CSV Datei","*.csv")            
        self.infocounter=0
        self.folder_raw=homefolder
            
        # Create Menu
        menu_container = tk.Menu(self.start_window)
        start_menu = tk.Menu(menu_container, tearoff=0)# Start Menu
        # Order menu entries (Info & quit)
        start_menu.add_command(label="Dokumentation", command=self.show_readme)
        start_menu.add_command(label="Über KYSA", command=self.action_get_info_dialog)
        start_menu.add_command(label="Changelog", command=self.show_changelog)
        start_menu.add_separator() # Fügt eine Trennlinie hinzu
        start_menu.add_command(label="Beenden", command=self.close_program)
        # Create Drop-Down Menu
        menu_container.add_cascade(label="Informationen", menu=start_menu)
        # integrate menu with window
        self.start_window.config(menu=menu_container)     
        
        
        #create radiobutton for csv/excel choice
        tk.Label(self.start_window, text="Sollen *.csv oder *.xlsx Daten eingelesen werden",justify='left',wraplength=240,pady=10,font='Helvetica 12').grid(rowspan=2,column=0,padx=5, sticky='W')
        tk.Radiobutton(self.start_window, text='csv',variable=self.importtype_var,value='csv_analyse',command=self.set_checkboxes, font='Helvetica  11',padx=padx_os).grid(row=0,column=1, sticky='W')
        tk.Radiobutton(self.start_window, text='xlsx',variable=self.importtype_var,value='xls_analyse',command=self.set_checkboxes,font='Helvetica  11',padx=padx_os).grid(row=1,column=1, sticky='W')

        #create checkbox for holiday extraction
        tk.Label(self.start_window, text="Urlaube separat auswerten",wraplength=240,pady=10,font='Helvetica 12').grid(row=2,column=0,padx=5, sticky='W')
        tk.Checkbutton(self.start_window, variable=self.holiday_var,padx=10,pady=10).grid(row=2,column=1, sticky='W')
        
        #create checkbox for savecent calculation
        tk.Label(self.start_window, text="Sparcents ausgeben",wraplength=240,pady=10,font='Helvetica 12').grid(row=3,column=0,padx=5 , sticky='W')
        tk.Checkbutton(self.start_window, variable=self.savecent_var,padx=10,pady=10).grid(row=3,column=1, sticky='W')
        
        #create checbox for csv-concatination
        tk.Label(self.start_window, text="Einzelne Dateien zusammenfassen",wraplength=240,pady=5,justify='left',font='Helvetica 12').grid(row=4,column=0,padx=5, sticky='W')
        tk.Checkbutton(self.start_window, variable=self.concat_var_single,padx=10,pady=10).grid(row=4,column=1, sticky='W')
        
        #create checkbox for longterm concatination
        tk.Label(self.start_window, text="Csv-Daten zusätzlich zu bestehenden Excel-Dateien hinzufügen (Langzeitanalyse)",wraplength=240,justify='left',font='Helvetica 12').grid(row=5,column=0,padx=5, sticky='W')
        self.chk_longterm=tk.Checkbutton(self.start_window, variable=self.longterm_select,padx=10,pady=10)
        self.chk_longterm.grid(row=5,column=1, sticky='W')

        tk.Label(self.start_window,pady=5).grid(columnspan=2,row=6)#Placeholder
        #create Button to browse files
        tk.Button(self.start_window, text="Rohdateien auswählen", command=self.file_button,font='Helvetica 12 bold').grid(row=7,columnspan=2,ipady=5,pady=10)

        #create Button to run application
        tk.Button(self.start_window, text="Auswertung starten", command=self.run_application,font='Helvetica 16').grid(row=8,columnspan=2,ipady=10,pady=15)
        
        #check for classification table
        self.import_classtable()
        
        self.start_window.mainloop()

    #necessary for icon integration in windows systems
    def resource_path(self,relative_path):    
        try:       
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def import_classtable(self):
        #import classifier table. if impossible quit
        try:
            self.import_classtable=datp.Classifier()
        except:
            tk.messagebox.showerror(message='Die Zuordnungstabelle befindet sich nicht im Programmordner. Das Programm wird geschlossen!')
            self.close_program()

    #stop gui and scripzt if window is closed by user
    def close_program(self):
        self.importtype_var.set('close_program')
        self.start_window.destroy()
    
    #open readmefile
    def show_readme(self):

        readme_name='KYSA_Readme.html'
        
        if not hasattr(sys, "frozen"):
            readme_path = os.path.join(os.getcwd(),"suppldata", readme_name)
        else:
            readme_path = os.path.join(sys.prefix,"suppldata", readme_name)

        webbrowser.open('file://'+readme_path,new=1)

    #open changelog
    def show_changelog(self):

        #base information
        changelogbox = tk.Toplevel()
        changelogbox.config(bg='white')

        positionRight_info=int(self.start_window.winfo_screenwidth()/2- self.windowWidth/3)
        positionDown_info=int(self.start_window.winfo_screenheight()/3 - self.windowHeight)

        changelogbox.geometry(f"300x400+{positionRight_info}+{positionDown_info}")
        changelogbox.minsize(150,200)
        changelogbox.title("Changelog")

        frame = tk.Frame(master=changelogbox)
        frame.pack(expand=True, fill="both")

        vbar = tk.Scrollbar(frame, orient='v')
        vbar.pack(side="right", fill="y")
        changelogbox.update()

        change201list=['Introduction of error codes','Integration of progressbar','Completely revised process structure','Faster program startup on Windows']
        change201_text=('• '+'\n• '.join([change201list[item] for item in range(len(change201list))]))

        change103list=['Integration of changelog-menu entry','Establish workaround for current comdirect csv-export problem','Rescripting plot generation for account types','Various account import bugfixes']
        change103_text=('• '+'\n• '.join([change103list[item] for item in range(len(change103list))]))

        change102list=['Integration of Readme html-file and copycode','New icon creation','Anchor icon in all running windows','Fix plotting of "rent"&"income"-categories','Change plot output format into *.png','Change excel output engine']
        change102_text=('• '+'\n• '.join([change102list[item] for item in range(len(change102list))]))

        change101list=['Integration of "Über KYSA"-menu entry','Anchor icon in main window and make it work in Windows.exe','Change import process of assignment table']
        change101_text=('• '+'\n• '.join([change101list[item] for item in range(len(change101list))]))

        text_widget = tk.Text(frame, undo=True, yscrollcommand=vbar.set,pady=15,padx=5)
        text_widget.tag_configure('title',font='Helvetica 16 bold',justify='center',spacing3=10,wrap='none')
        text_widget.tag_configure('version',font='OpenSans  13',justify='left',spacing1=20,spacing3=15,wrap='none')
        text_widget.tag_configure('changes',font='OpenSans  11',justify='left',spacing3=3,lmargin2=lmargin2_os,wrap='word')
                
        text_widget.insert('end', "Changelog\n",'title')
        text_widget.insert('end', "Version 2.01:\n",'version')
        text_widget.insert('end', change201_text+'\n','changes')
        text_widget.insert('end', "Version 1.03:\n",'version')
        text_widget.insert('end', change103_text+'\n','changes')
        text_widget.insert('end', "Version 1.02:\n",'version')
        text_widget.insert('end', change102_text+'\n','changes')
        text_widget.insert('end', "Version 1.01:\n",'version')
        text_widget.insert('end', change101_text+'\n','changes')
        text_widget.pack(fill='both',expand=True)
        text_widget.config(state='disabled')

        vbar.config(command=text_widget.yview)




    #create info menu message
    def action_get_info_dialog(self):
        
            
        infobox = tk.Toplevel()
        infobox.config(bg='white')
        infobox.resizable(False, False)
        positionRight_info=int(self.start_window.winfo_screenwidth()/2- self.windowWidth/3)
        positionDown_info=int(self.start_window.winfo_screenheight()/3 - self.windowHeight)

        infobox.geometry(f"360x500+{positionRight_info}+{positionDown_info}")
        infobox.title("Über KYSA")

        copycode='Copyrightcode.png'
        
        if not hasattr(sys, "frozen"):
            path_copycode = os.path.join(os.getcwd(),"suppldata",copycode)
        else:
            path_copycode = os.path.join(sys.prefix,"suppldata",copycode) 

        raw_copycode=Image.open(path_copycode).resize((120,29), Image.ANTIALIAS)
        copycode=ImageTk.PhotoImage(raw_copycode)

        
        banks="\t-------------------------------------\n".expandtabs(2)\
        +"\tAktuell unterstützte Banken:\n\n".expandtabs(3)\
        +"\t1) Apobank (Giro) (beta/nicht validiert)\n".expandtabs(5)\
        +"\t2) comdirect (Giro&Kredit)\n".expandtabs(5)\
        +"\t3) Commerzbank (Giro)\n".expandtabs(5)\
        +"\t4) DKB (Giro&Kredit)\n".expandtabs(5)\
        +"\t5) Deutsche Bank (Giro)\n".expandtabs(5)\
        +"\t6) MLP Bank (Giro) (beta/nicht validiert)\n".expandtabs(5)\
        +"\t7) Sparkasse (Giro)\n".expandtabs(5)\
        +"\t8) Triodos Bank (Giro)\n".expandtabs(5)\
        +"\t-------------------------------------".expandtabs(2)
        
        
        l_title =tk.Label(infobox, text="KYSA\n-\nKnow Your Spendings Application", bg='white',font='Helvetica 15')
        l_version=tk.Label(infobox, text="Version:\tv2.01",bg='white',font='OpenSans  9')
        l_banks=tk.Label(infobox, text=banks,justify='left',bg='white',font='OpenSans 11')
        l_credit=tk.Label(infobox, text="Daniel Krezdorn 2020",bg='white',font='OpenSans  9')
        l_copyright=tk.Label(infobox, image=copycode)
        l_copyright.image=copycode
        
        l_title.pack(pady=20,fill='x',expand=True)
        l_banks.pack(pady=10,fill='x',expand=True)
        l_version.pack(pady=5,fill='x',expand=True)
        l_credit.pack(pady=5,fill='x',expand=True)
        l_copyright.pack(pady=3,expand=True)


    #create function to adjust values based on importtype decision
    def set_checkboxes(self):
        
        if self.importtype_var.get()=='xls_analyse':
            self.fileextension=5
            self.filetype=("Excel Datei","*.xlsx")
            self.longterm_select.set(0)            
            self.chk_longterm.config(state='disabled')
        else:
            self.fileextension=4
            self.filetype=("CSV Datei","*.csv")
            self.chk_longterm.config(state='normal')
    
    def file_button(self):
        self.browse_file('raw_data')

    #create file browsing function
    def browse_file(self,purpose):

        filename_var=tk.StringVar()
        self.filenames=[]
        if purpose=='raw_data':
            if (self.infocounter==0)&(self.importtype_var.get()=='xls_analyse'):
                tk.messagebox.showinfo(message='\nEs können mehrere Dateien auf einmal ausgewählt werden!\n\n\nBitte beachten:\n\nExcel-Dateien, die ausgewertet werden sollen, müssen ein Tabellenblatt "Aufbereitete Daten" in der Formatierung bereits aufbereiteter csv-Dateien haben!\n')
                self.infocounter+=1
            elif self.infocounter==0:
                tk.messagebox.showinfo(message='\nBitte wählen Sie alle auszuwertenden Dateien auf einmal aus!')
                self.infocounter+=1
            else:
                pass
            filename_var = tkbrowse.askopenfilenames(initialdir=self.folder_raw, title = "Rohdateien auswählen", filetypes =(self.filetype,("all files","*.*")))
        
        elif purpose=="concat_longterm":
            filename_var = tkbrowse.askopenfilenames(initialdir=self.folder_raw,title=f"Excel-Dateien für die Zusammenführung (Langzeitanalyse) auswählen",filetypes=(("Excel Datei","*.xlsx"),("all files","*.*")))
            self.fileextension=5

        #filepathes
        filelist=list(filename_var) # use for data import
        if not filelist==[]:
            #get directory (double check in windows)
            self.folder_raw=os.path.split(filelist[0])[0]

            #extract filenames and create list
            for path in filelist:
                filename=os.path.split(path)[1][:-self.fileextension]
                self.filenames.append((filename,path))
        else:
            pass

    def import_check(self,purpose):

        if purpose=='raw_data':
            importtype=self.importtype_var.get()

        elif purpose=='concat_longterm':
            importtype='xls_longterm'

        successlist=[]
        errorlist=[]

        for item in self.filenames:
            
            self.accounts_data.process_data(item,importtype)
            
            ## check if import went through
            if item[0] in self.accounts_data.error_codes.keys():
                errorlist.append(item[0]+' ('+self.accounts_data.error_codes[item[0]]+')')
            
            else:
                successlist.append(item[0])
        
        if successlist==[]:

            errorcodes=', '.join([item for item in list(set(self.accounts_data.error_codes.values()))])
            messagetext=f'Es konnte keine der ausgewählten Dateien verarbeitet werden!\n\nWählen Sie neue Dateien!\n\nFehlercode(s):\n({errorcodes})'
            tk.messagebox.showerror(message=messagetext)
   
        elif errorlist==[]:

            messagetext='Alle Dateien wurden erfolgreich importiert!'
            tk.messagebox.showinfo(message=messagetext)
        
        else:
            successlisttext=('• '+'\n• '.join([item for item in successlist]))
            errorlisttext=('• '+'\n• '.join([item for item in errorlist]))
            messagetext=f'Es wurde:\n\n{successlisttext}\n\nerfolgreich eingelesen.\n\n\nFolgende Dateien konnten nicht verarbeitet werden:\n\n{errorlisttext}'
            tk.messagebox.showinfo(message=messagetext)


        return successlist


    def run_application(self):

        if self.filenames==[]:
            tk.messagebox.showwarning(message='Es wurden keine Dateien ausgewählt!\n\nBitte wählen Sie mindestens eine Datei aus')
        elif (len(self.filenames)==1)&(self.concat_var_single.get()==1):
        	tk.messagebox.showwarning(message='Es wurde nur eine Datei eingegeben, aber die Rohdaten-Zusammenführung gewählt!\n\nBitte wählen Sie mindestens zwei Dateien aus oder wählen die Datei-Zusammenführung ab.')
        else:
            #hide main window
            self.start_window.withdraw()
            #start data import via Accounts Data
            #make accountsdata
            self.accounts_data=datp.Accounts_Data(self.folder_raw,self.import_classtable)
    		
            import_list=self.import_check('raw_data')

            if import_list==[]:
                self.start_window.deiconify()
            else:
                self.data_process()
    			

                
    def excel_extraimport(self,purpose):

        if purpose=='concat_longterm':
            nameholder='Langzeitanalyse'
            userchoice=tk.messagebox.askokcancel(f"{nameholder}", f"Bitte wählen Sie im folgenden Schritt die Excel-Dateien für die Zusammenführung zur {nameholder} aus. Die Dateien müssen ein Tabellenblatt 'Aufbereitete Daten' im Format bereits aufbereiteter csv_Dateien haben.")
            
        while userchoice:
            self.browse_file(purpose)
            if self.filenames==[]:
                if tk.messagebox.askyesno(message=f'Wenn Sie abbrechen, wird die Datenzusammenführung "{nameholder}" übersprungen. Möchten Sie dennoch abbrechen?'):
                    import_list=[]
                    break
                else:
                    continue
            else:
                self.accounts_data.error_codes={} ## empty error-dict while loop is active
                
                import_list=self.import_check(purpose)

                if import_list==[]:
                    continue
                else:
                    break

        return import_list


    #run data preprocessing           
    def data_process(self):

        # #concat holiday data
        if self.holiday_var.get()==1:
            self.accounts_data.bundle_holiday()
            #action if savecent_calculation if selected
        if self.savecent_var.get()==1:
            self.accounts_data.savecent_calculation()

        #concat data if selected
        if self.concat_var_single.get()==1 or self.longterm_select.get()==1:
            ##import long term excel if selected
            longterm_import=[]
            if self.longterm_select.get()==1:
                longterm_import=self.excel_extraimport("concat_longterm")

            if "Sparcents" in list(self.accounts_data.folder_res.keys()):
                processed_files=list(self.accounts_data.folder_res.keys())
                processed_files.remove('Sparcents') #get sublist without savecent 
            else:
                processed_files=list(self.accounts_data.folder_res.keys())  

            concat_basislist=processed_files+longterm_import
            concat_choice=concat_Window(self.start_window,concat_basislist)
            self.start_window.wait_window(concat_choice)
            if not concat_choice.concat_list==[]:
                self.accounts_data.concatter(concat_choice.concat_list)
        else:#no action needed
            pass

        self.accounts_data.month_cat_maker()

        self.start_window.destroy()

#--------------info for concat grid



class concat_Window(tk.Toplevel):
    
    def __init__(self,parent,input_list):

        tk.Toplevel.__init__(self,parent)
        self.protocol("WM_DELETE_WINDOW",self.skip_concat)
        self.input_list=input_list
        self.title("Daten-Zusammenführung")
        #tk.messagebox.showinfo(message='Hier können Sie einzelne csv-Dateien zusammenfügen')
        
        #set variables
        if len(input_list)==2:
            self.cols=1
        elif len(input_list)==3:
            self.cols=3
        else:
            self.cols=6

        self.entrybox=[]
        
        self.chkboxboxes = []
        self.chkboxVars = []

        
        for colid in range(self.cols):
            #initalize checkbox variables
            self.chkboxVars.append([])
            self.chkboxboxes.append([])
            
            #generate entryboxes
            tk.Label(self, text= f"Name für Datei {(colid+1)}:",pady=7,font='Helvetica 11').grid(row=len(self.input_list)+2+colid,column=0,padx=5,sticky='w')
            self.entrybox.append(tk.Entry(self, state='disabled',font='Helvetica 10',width=50))
            self.entrybox[colid].grid(row=len(self.input_list)+2+colid,column=1,columnspan=4,padx=10,ipady=5,pady=10,sticky='w')
            self.entrybox[0].config(state='normal')
            #generate empty space between blocks
            self.empty_label=tk.Label(self,pady=8).grid(row=len(self.input_list)+1) 
                
            
            for rowid in range(0,len(self.input_list)):
            

                ##initialize variables checkboxes
                self.chkboxVars[colid].append(tk.IntVar())
                self.chkboxVars[colid][rowid].set(0)


                tk.Label(self, text= f"Datei {(colid+1)}",wraplength=80,pady=10,padx=10,font='Helvetica 11').grid(row=0,column=colid+1)
                tk.Label(self, text= self.input_list[rowid],pady=10,font='Helvetica 11').grid(row=rowid+1,column=0,padx=5,sticky='w')
                self.chkboxboxes[colid].append(tk.Checkbutton(self,variable=self.chkboxVars[colid][rowid],state='disabled'))
                self.chkboxboxes[colid][rowid].grid(row=rowid+1, column=colid+1)
                self.chkboxboxes[colid][rowid].config(command=self.check_columns)
                #enable only first column at beginning
                self.chkboxboxes[0][rowid].config(state='normal')
                
                #generate empty space between blocks
                tk.Label(self,pady=8).grid(row=len(self.input_list)+1) 
  
        #create Button to skip or proceed
        tk.Button(self, text="Weiter",command=self.proceed_analysis,font='Helvetica 12 bold').grid(row=len(self.input_list)+2+self.cols,column=2,columnspan=3,ipady=5,pady=10)
        tk.Button(self, text="Daten-Zusammenführung abbrechen",command=self.skip_concat,font='Helvetica 12 bold').grid(row=len(self.input_list)+2+self.cols,columnspan=3,ipady=5,pady=10)

        #self.root.mainloop()
    
    def skip_concat(self):
        self.concat_list=[]
        self.destroy()
    
    
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
                    temp.append(self.input_list[rowid])
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
                self.destroy()

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

#-------------progressbar

class Progressbar():
    
    def __init__(self,master):
        
        self.process_info = master
        self.process_info.title('Datenverarbeitung')
        self.process_info.protocol("WM_DELETE_WINDOW",self.keep_alive)
        self.process_info.resizable(False, False)
        self.process_info.config(bg='black')
        
        # Gets both half the screen width/height
        positionRight_main = int(self.process_info.winfo_screenwidth()/2 - 110)
        positionDown_main = int(self.process_info.winfo_screenheight()/2 - 110)
 
        #Positions the window in the center of the page.
        self.process_info.geometry(f"+{positionRight_main}+{positionDown_main}")
        
        #icon
        iconFile_name='KYSA-Icon2.ico'
        
        if not hasattr(sys, "frozen"):
            iconFile = os.path.join(os.getcwd(),"suppldata", iconFile_name)
        else:
            iconFile = os.path.join(sys.prefix,"suppldata", iconFile_name)

        s=ttk.Style()
        #platform adaptions icons and progressbar style
        if platform.system()=='Windows':
            #icon
            self.process_info.tk.call('wm', 'iconphoto', self.process_info._w,ImageTk.PhotoImage(file=iconFile)) 
            #progressbar style
            s.theme_use('default')
            s.configure("KYSA.Horizontal.TProgressbar",foreground='white',background='black') 
        
        else:
            #icon
            linux_icon=Image.open(iconFile)
            linux_img = ImageTk.PhotoImage(linux_icon)
            self.process_info.iconphoto(True, linux_img)
            #progressbar style
            TROUGH_COLOR='white'
            BAR_COLOR='black'
            s.configure("KYSA.Horizontal.TProgressbar",thickness=18,troughcolor=TROUGH_COLOR,bordercolor=TROUGH_COLOR, background=BAR_COLOR, lightcolor=BAR_COLOR, darkcolor=BAR_COLOR)
        


        #integrate picture
        progress_icon='KYSA-Progress_Icon.png'
        
        if not hasattr(sys, "frozen"):
            path_progress_icon = os.path.join(os.getcwd(),"suppldata",progress_icon)
        else:
            path_progress_icon = os.path.join(sys.prefix,"suppldata",progress_icon) 

        process_info_pic=ImageTk.PhotoImage(Image.open(path_progress_icon))
        
               
        process_pic=tk.Label(self.process_info, image=process_info_pic)
        process_pic.image=process_info_pic
        
        #progressbar widget
        self.pgsb=ttk.Progressbar(self.process_info,style="KYSA.Horizontal.TProgressbar",takefocus=True,orient="horizontal",length=220,mode="indeterminate")
        
        process_pic.pack(expand=True)
        self.pgsb.pack(pady=1,side='bottom',fill='x')
        
        #self.pgsb.config()
        self.pgsb.start(20)
        
    def close_proc(self):
        self.process_info.quit()

    def keep_alive(self):
        pass



#show info about import success
def process_info(messagetext,messagetyp):
    info_window=tk.Tk()
    info_window.withdraw()

    if messagetyp=='errormessage':
        tk.messagebox.showerror(message=messagetext)
    else:
        tk.messagebox.showinfo(message=messagetext)
    info_window.destroy
