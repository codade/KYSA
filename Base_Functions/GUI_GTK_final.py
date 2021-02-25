'''Main File holding classes and functions necessary for building GTK3-based GUI
This file really just builds the GUI with its subwindows. Main calculations are stored in user_process.py. The GUI reverts to those functions whenever necessary '''

import gi
import os
import sys
import webbrowser
import random

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GLib, Pango
from Base_Functions import GUIvars as guivar
from Base_Functions import user_process as userproc



#--------------------------------------Import style adaptions-----------------------------------

#style is defined in GUIVers file


style_provider=Gtk.CssProvider()
style_provider.load_from_data(bytes(guivar.KYSA_css.encode()))
Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


#--------------------------------------Platform specific constructions-------------------------


#import supplementary data (icons and readmes)

icon_name='KYSA-Icon_64.ico'
readme_name='KYSA_Readme_'+userproc.language_choice+'.html'
license_name='KYSA_License_'+userproc.language_choice+'.html'
kysa_image='KYSA-Progress_pic.png'
copyright_pic='CRcode.png'

if not hasattr(sys, "frozen"): #get local folder path for subfolder 'suppldata'
    suppldata_path=os.path.join(os.getcwd(),"suppldata")

else:
    suppldata_path=os.path.join(os.getcwd(),"suppldata")

iconfilepath= os.path.join(suppldata_path, icon_name)
readme_path= os.path.join(suppldata_path, readme_name)
license_path= os.path.join(suppldata_path, license_name)
kysaimagepath= os.path.join(suppldata_path, kysa_image)
crpic_path=os.path.join(suppldata_path, copyright_pic)#load to make sure png is present

#get language setting and import language dictionary
open(crpic_path) #load to make sure png is present
langdict_all=userproc.langdict_used #necessary extra variable definition for KYSA.py to get language information
langdict_gui=langdict_all['GUI_Final_vars']



#---------------------------------------Main Window class--------------------------------------------


class Main_Window(Gtk.ApplicationWindow):

#_____________________________________________ subsection window design_______________________________
    def __init__(self):


        #Window properties
        Gtk.Window.__init__(self, title="KYSA - Know Your Spendings")
        self.set_default_size(200, 100)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)
        self.connect("delete_event", self.close_window)
        self.set_resizable(False)

        
        self.set_default_icon_from_file(iconfilepath)#

        self.proceed=False#necessary variable for window closing
        self.selection_counter=0#necessary for popup notices

        copycode = Gtk.Image()
        copycode.set_from_file(crpic_path)
######################################################### Menu Part #################################

      	#setup menubar and link to menu functions
      	## menu main structure is defines in xml-part in GuiVars


        menubar = Gtk.HeaderBar()
        menubar.set_show_close_button(True)
        menubar.set_title("KYSA")
        menubar.set_subtitle("Know Your Spendings")
        self.set_titlebar(menubar)
        
        #load language specific menu
        if userproc.language_choice=='eng':
            builder = Gtk.Builder.new_from_string(guivar.KYSA_XMLMenu_eng, -1)
        else:
            builder = Gtk.Builder.new_from_string(guivar.KYSA_XMLMenu_deu, -1)

        menu = builder.get_object("KYSA-Menu")

        #menubutton in headerbar
        button = Gtk.MenuButton.new()
        button.set_menu_model(menu)
        button.set_use_popover(False)#downward opening menubox
        button.set_direction(Gtk.ArrowType.DOWN)
        icon = Gio.ThemedIcon.new("open-menu-symbolic") # include menu symbol
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        menubar.pack_start(button)

        

        ##menu entries and actions (every entry in xml is connected to specific function)


        act_about = Gio.SimpleAction.new('about', None)
        act_about.connect('activate', self.show_about)
        self.add_action(act_about)

        act_readme= Gio.SimpleAction.new('readme', None)
        act_readme.connect('activate', self.show_readme)
        self.add_action(act_readme)

        act_license= Gio.SimpleAction.new('license', None)
        act_license.connect('activate', self.show_license)
        self.add_action(act_license)

        act_chglog= Gio.SimpleAction.new('changelog', None)
        act_chglog.connect('activate', self.show_chglog)
        self.add_action(act_chglog)

        act_classtbl= Gio.SimpleAction.new('classtbl', None)
        act_classtbl.connect('activate', self.set_folders,'classdir')
        self.add_action(act_classtbl)

        act_resfolder= Gio.SimpleAction.new('resdir', None)
        act_resfolder.connect('activate', self.set_folders,'resdir')
        self.add_action(act_resfolder)

        act_uisettings= Gio.SimpleAction.new('uiset', None)
        act_uisettings.connect('activate', self.ui_settings)
        self.add_action(act_uisettings)

        act_donate= Gio.SimpleAction.new('donate', None)
        act_donate.connect('activate', self.show_donate)
        self.add_action(act_donate)


        act_quit= Gio.SimpleAction.new('quit', None)
        act_quit.connect('activate', self.close_window)
        self.add_action(act_quit)

        

######################################################### Buttons Design Part #################################

        main_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6) #create vertical oriented gridbox
        self.add(main_box)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT) #Switch between xls and csv
        self.stack.set_vhomogeneous(False)
        self.stack.set_transition_duration(100)
        
        #gridboxes for user selection (checkboxes). 

        # Base_grid Box holds selections that can be chosen for xls and csv analysis
        base_grid = Gtk.Grid()

        #language specific spacing between label and checkbox column
        if userproc.language_choice=='eng':
            base_grid.set_column_spacing(30)
            csv_adjustvar=-26.5
        else:
            base_grid.set_column_spacing(40)
            csv_adjustvar=-9.5

        base_grid.set_row_spacing(15)
        base_grid_cols=3

        #csv grid holds those user elective checkboxes that can only be run on csv-data
        csv_grid = Gtk.Grid()
        csv_grid.set_column_spacing(base_grid.get_column_spacing()-csv_adjustvar)
        csv_grid.set_row_spacing(15)

        #labels in grids
        grid_l_lst=[langdict_gui['mainwin_choice3'][0],langdict_gui['mainwin_choice4'][0],langdict_gui['mainwin_choice5'][0],
                            langdict_gui['mainwin_choice6'][0],langdict_gui['mainwin_choice7'][0],langdict_gui['mainwin_choice8'][0]]
        
        #checkboxes in grids
        self.grid_chk_lst=[Gtk.CheckButton(),Gtk.CheckButton(),Gtk.CheckButton(),Gtk.CheckButton(),Gtk.CheckButton(),Gtk.CheckButton()]

        grids=[(base_grid,0,5),(csv_grid,5,len(grid_l_lst))] #tuple containing lower and upper limits

        #create booth grids with label and checkbox
        for item in grids:
            #adjust index depending on grid


            for num in range(item[1],item[2]): #range from lower to upper limit in respective grid
            #label
                label=Gtk.Label.new(grid_l_lst[num])
                label.set_max_width_chars(40)
                label.set_line_wrap(True)
                label.set_xalign(0)
                 
                item[0].attach(label,0,num-item[1],1,1) #adjust num with lower limit
                #checkbox
                self.grid_chk_lst[num].set_halign(Gtk.Align.END)
                item[0].attach(self.grid_chk_lst[num], 1, num-item[1], 1, 1)


        self.stack.add_titled(csv_grid, "csv_analyse", langdict_gui['mainwin_choice1'][0])
        
        xls_box = Gtk.Box()
        self.stack.add_titled(xls_box, "xls_analyse", langdict_gui['mainwin_choice2'][0])
        
        #separation between switch and base grid
        separator_label = Gtk.Label() 
        separator_label.set_markup(langdict_gui['mainwin_separator_text'][0])
        separator_label.set_name("separator_label")
        
        #create main window
        stack_switcher = Gtk.StackSwitcher() #Establish xls-csv-switch
        stack_switcher.set_stack(self.stack)
        stack_switcher.set_halign(Gtk.Align.CENTER)

        #pack switch and selection boces
        main_box.pack_start(stack_switcher, False, True, 5) 
        main_box.pack_start(separator_label,False,True,15)
        main_box.pack_start(base_grid,False,True,0)
        main_box.pack_start(self.stack, True, False, 5)
        
        #browse files button
        bws_btn = Gtk.Button.new_with_label(langdict_gui['mainwin_btn1'][0])
        bws_btn.connect("clicked", self.browse_files)
        bws_btn.set_name("bws_btn")
        bws_btn.set_size_request(0, 45)
        main_box.pack_start(bws_btn, False, False, 15)
        
        #start calculation button
        run_btn = Gtk.Button.new_with_label(langdict_gui['mainwin_btn2'][0])
        run_btn.connect("clicked", self.run_program)
        run_btn.set_name("run_btn")
        run_btn.set_size_request(0, 55)
        main_box.pack_start(run_btn, False, False, 5)
        
        #set timer for readjusting window size depending on csv/xls-selection
        GLib.timeout_add(100, self.window_resize, None)

        self.show_all()

        self.mfunc=userproc.Main_Functions(self)#start main function with this window as master

        if userproc.startcount==0:
            uisettings_win=UISettings_Window(self) #start Language selection with first program start


#_____________________________________________ subsection window/button functions_______________________________

    def window_resize(self,user_data):

        self.resize(100,50)
        return True
        
    def selection_adapt(self): #check for current choice and adjust to xls/csv-selection
        #selected choices variables
        

        self.choice_dtype=self.stack.get_visible_child_name()
        
        if self.selection_counter==0:#adjust popup counters
            if userproc.startcount<2:
                userproc.startcount+=1
                if self.choice_dtype=='xls_analyse':
                    userproc.message.info(self,langdict_gui['mainwin_xlsxinfo'][0],langdict_gui['mainwin_xlsxinfo'][1])
                else:
                    pass
            else:
                userproc.startcount=random.randint(2,1000)

        #deactivate csv-specific choice if xls is selected
        if self.choice_dtype=='xls_analyse':
            self.grid_chk_lst[5].set_active(False)
            self.choice_conc_xls=False

        else:
            self.choice_conc_xls=self.grid_chk_lst[5].get_active()
            


        self.selection_counter+=1

    def browse_files(self,widget):

    	#function belonging to browse button

        self.selection_adapt()#check user selection

        if self.choice_dtype=='xls_analyse':
            purpose='raw_data_excel'
        else:
            purpose='raw_data_csv'
        
        self.mfunc.filebrowser(purpose) #open filebrowser fundtion in MainFunc Class
        
        if (userproc.startcount%7==0 or userproc.startcount%5==0) and userproc.startcount!=0:
            self.donate_popup()
        else:
            pass

    def run_program(self,widget):
        #function belonging to start calculation button

        self.selection_adapt()#get selection type and specific csv selections
        #get selected variables
        choice_hol=self.grid_chk_lst[0].get_active()
        choice_sav=self.grid_chk_lst[1].get_active()
        choice_conc=self.grid_chk_lst[2].get_active()
        choice_cash=self.grid_chk_lst[3].get_active()
        choice_longterm=self.grid_chk_lst[4].get_active()

        user_choice=(self.choice_dtype,choice_hol,choice_sav,choice_conc,choice_cash,choice_longterm,self.choice_conc_xls)

        self.proceed=self.mfunc.start_analysis(user_choice)#get information about import success
        
        if self.proceed:
            #do data preparation and show progress (in data prep function)
            self.hide()
            self.mfunc.data_preparation()
            self.close_window('test','run_prog')#close window and open progress bar

    def donate_popup(self):
        if userproc.startcount%7==0 or userproc.startcount%5==0:
            userchoice=userproc.message.question(self,langdict_gui['mainwin_donatinfo'][0],langdict_gui['mainwin_donatinfo'][1])
            if userchoice:
                donate_win=Donate_Window(self)
        else:
            pass




###################################### Menu Fundtions Part #################################

# these funcions belong to the menu build part and connect to the menu structure given in XML file of GuiVars


    def show_readme(self,action, value):
        webbrowser.open('file://'+readme_path,new=1)

    def show_license(self,action, value):
        webbrowser.open('file://'+license_path,new=1)

    def show_about(self,action, value):
        aboutdialog = Gtk.AboutDialog()
        authors = ["Daniel Krezdorn"]
        aboutdialog.set_program_name("KYSA\nKnow Your Spendings Application")
        aboutdialog.set_copyright("\xa9 2020 Daniel Krezdorn")
        aboutdialog.set_authors(authors)
        aboutdialog.set_version(guivar.versions[0])
        aboutdialog.set_license_type(Gtk.License.BSD_3) #Changed to BSD 3 from BSD 2 (currently not suported by PyGobject version)
        aboutdialog.set_website("http://www.digital-souveraenitaet.de/kysa-")
        aboutdialog.set_website_label(langdict_gui['aboutwin_linktext'][0])

        aboutdialog.set_title(langdict_gui['aboutwin_title'][0])
        aboutdialog.show()

    def show_chglog(self,action, value):
        
        chglog_win=Chglog_Window(self)

    def show_donate(self,action, value):
        
        donate_win=Donate_Window(self)

    def ui_settings(self,action, value):
        
        uisettings_win=UISettings_Window(self)

        
    def set_folders(self,action,value,purpose):
        if purpose=='classdir':
            classtbl_success=self.mfunc.set_classtable('change') #link to classtable check function; variable classtable_success necessary as functions returns value for user_process script

        elif purpose=='resdir':
            self.mfunc.filebrowser('resdir')

    def close_window(self,widget,origin):#used by menu entry quit and close event
        
        self.mfunc.save_prefs()#save preferences
        #save changes to history train data to csv and encrypt it
        self.mfunc.encrypt_datasets()

        if origin=='run_prog':
            self.close()#send close signal
        else:#close window
            if not self.proceed:
                self.choice_dtype='stop_analysis'
            else: 
                pass

            Gtk.main_quit()



#---------------------------------------Changelog Window class--------------------------------------------

#start extra window for changelog. Changlog entries are created in GUIVars file as loopable list

class Chglog_Window(Gtk.Window):
    def __init__(self,master):

        Gtk.Window.__init__(self, title="Changelog")

        self.set_default_size(400, 300)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_transient_for(master)

        #design part
        self.main_box = Gtk.Box()
        self.add(self.main_box)

        #establish scrollbar

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_hexpand(True)
        self.main_box.pack_start(scrolledwindow, True,True,0)

        # main text box
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3)
        
        #connect text box to scrollable window
        text_view=Gtk.Viewport()
        text_view.add(text_box)
        scrolledwindow.add(text_view)

        # main label header
        label_header= Gtk.Label() 
        label_header.set_markup("<big>Changelog\n</big>")
        label_header.set_name("separator_label")
        text_box.pack_start(label_header,True,True,0)

        version_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        #loop through changeloglist created in GUIVars. Every list entry holds a tuple. First position in tuple holds version number, the second the changes being applied
        for i in range(len(guivar.chglog_list)):
            label_ver=Gtk.Label()            
            label_ver.set_markup(f"<b>{guivar.chglog_list[i][0]}</b>")
            label_ver.set_xalign(0)

            label_chg=Gtk.Label.new(guivar.chglog_list[i][1])
            label_chg.set_line_wrap_mode(Pango.WrapMode.WORD)
            label_chg.set_line_wrap(True)
            label_chg.set_xalign(0)

            #pack labels within version_textbox
            version_box.pack_start(label_ver,True,True,2)
            version_box.pack_start(label_chg,True,True,0)

        text_box.pack_start(version_box,True,True,0)

       	self.show_all()


#---------------------------------------Donation Window class--------------------------------------------

#start extra window for donation info.

class Donate_Window(Gtk.Window):
    def __init__(self,master):

        Gtk.Window.__init__(self, title=langdict_gui['donatewin_header'][0])

        self.set_default_size(300, 50)
        self.set_resizable(False)
        self.set_size_request(300,50)
        self.set_position(Gtk.WindowPosition.CENTER)
        #self.set_transient_for(master)
        #self.set_modal(True)
        #self.set_keep_above(True)

        #design part
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        
        self.add(main_box)

        # main label header
        label_header= Gtk.Label() 
        label_header.set_markup(langdict_gui['donatewin_title'][0])
        label_header.set_name("separator_label")
        main_box.pack_start(label_header,True,True,15)



        
        
        label_content=Gtk.Label(label=langdict_gui['donatewin_text'][0])

        
        label_content.set_line_wrap_mode(Pango.WrapMode.WORD)
        label_content.set_line_wrap(True)
        label_content.set_max_width_chars(60) #necessary for windows compatibility
        #label_content.set_xalign(0)
        main_box.pack_start(label_content,True,True,10)  
        

        label_link=Gtk.LinkButton.new_with_label(langdict_gui['donatewin_link'][0],langdict_gui['donatewin_link'][1])
        main_box.pack_start(label_link,True,True,10)

        self.show_all()


#start extra window for language settings

class UISettings_Window(Gtk.Window):
    def __init__(self,master):

        Gtk.Window.__init__(self, title=langdict_gui['setuiwin_header'][0])

        self.set_default_size(300, 50)
        self.set_resizable(False)
        self.set_size_request(300,50)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_transient_for(master)
        self.set_modal(True)
        self.master=master

        self.counter=0
        self.language=userproc.language_choice
        self.currency=userproc.currency_var

        #design part
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        
        self.add(main_box)

        # main label title
        label_header= Gtk.Label() 
        label_header.set_markup(langdict_gui['setuiwin_title'][0])
        label_header.set_name("separator_label")
        label_header.set_padding(10,15)
        main_box.pack_start(label_header,True,True,0)


        hbox_grid = Gtk.Grid()
        hbox_grid.set_row_spacing(20)
        hbox_grid.set_column_spacing(50)
        hbox_grid.set_row_homogeneous(False)
        hbox_grid.set_column_homogeneous(False)
        hbox_grid.set_halign(Gtk.Align.CENTER)

        label_lang=Gtk.Label()
        label_lang.set_markup(langdict_gui['setuiwin_choicelabel'][0])
        label_lang.set_halign(Gtk.Align.CENTER)
        hbox_grid.attach(label_lang, 0, 0, 1, 1)

        label_curr=Gtk.Label()
        label_curr.set_markup(langdict_gui['setuiwin_choicelabel'][1])
        label_curr.set_halign(Gtk.Align.CENTER)
        hbox_grid.attach(label_curr, 1, 0, 1, 1)
        

        vbox_lang = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        vbox_curr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)

###################################### Language Radiobutton Part #################################    

        #radiobuttons for language selection
        button_deu = Gtk.RadioButton.new_with_label_from_widget(None, "Deutsch")
        button_deu.connect("toggled", self.lang_button_toggled, "deu")
        vbox_lang.pack_start(button_deu, True, True, 0)

        self.button_eng = Gtk.RadioButton.new_from_widget(button_deu)
        self.button_eng.set_label("English")
        self.button_eng.connect("toggled", self.lang_button_toggled, "eng")
        vbox_lang.pack_start(self.button_eng, True, True, 0)
        
        vbox_lang.set_halign(Gtk.Align.CENTER)
        vbox_lang.set_valign(Gtk.Align.CENTER)
        
        

###################################### Currency Radiobutton Part #################################    

        #radiobuttons for currency selection
        #Euro
        button_euro = Gtk.RadioButton.new_with_label_from_widget(None, langdict_gui['setuiwin_currencies1'][0])
        button_euro.connect("toggled", self.curr_button_toggled, "€")
        vbox_curr.pack_start(button_euro, True, True, 0)

        #Dollar
        self.button_dollar = Gtk.RadioButton.new_from_widget(button_euro)
        self.button_dollar.set_label(langdict_gui['setuiwin_currencies1'][1])
        self.button_dollar.connect("toggled", self.curr_button_toggled, "$")
        vbox_curr.pack_start(self.button_dollar, True, True, 0)

        #Pound
        self.button_pound = Gtk.RadioButton.new_from_widget(button_euro)
        self.button_pound.set_label(langdict_gui['setuiwin_currencies2'][0])
        self.button_pound.connect("toggled", self.curr_button_toggled, "£")
        vbox_curr.pack_start(self.button_pound, True, True, 0)

        #Krone
        self.button_krone = Gtk.RadioButton.new_from_widget(button_euro)
        self.button_krone.set_label(langdict_gui['setuiwin_currencies2'][1])
        self.button_krone.connect("toggled", self.curr_button_toggled, "Kr")
        vbox_curr.pack_start(self.button_krone, True, True, 0)
        
        vbox_curr.set_halign(Gtk.Align.CENTER)

        hbox_grid.attach(vbox_lang, 0, 1, 1, 1)

        hbox_grid.attach(vbox_curr, 1, 1, 1, 1)

        
        ################# Save Preferences Button#####

        save_btn = Gtk.Button.new_with_label(langdict_gui['setuiwin_btn'][0])
        save_btn.connect("clicked", self.save_prefs)
        save_btn.set_size_request(0, 40)
        hbox_grid.attach(save_btn, 0, 2, 2, 1)


        main_box.pack_start(hbox_grid,True,True,10)
        
        if self.counter==0:
            self.get_saved_prefs()

        self.show_all()

    def save_prefs(self, widget):

        closeproc_choice=False #necessary for automated program closure


        if self.counter>2:
            #user changed selection
            closeproc_choice=userproc.message.question(self,langdict_gui['setuiwin_newchoice'][0],langdict_gui['setuiwin_newchoice'][1])

            #save preferences whenever a new choice was selected
            userproc.language_choice=self.language
            userproc.currency_var=self.currency

        else:
            #no user selection
            userproc.message.info(self,langdict_gui['setuiwin_nochoice'][0],langdict_gui['setuiwin_nochoice'][1])

        #adjust startcount necessary for UI window popup with very first program start  
        userproc.startcount+=1 
        
        #close program if user pressed ok
        if closeproc_choice:
            self.close()
            self.master.close()
        else:
            self.close()

    def get_saved_prefs(self):
        #turn buttons on based on saved value in prefs file

        #language preset
        if self.language=='eng':
            self.button_eng.set_active(True)
        else:
            #pass
            self.counter+=1 #set self.counter according to preeselection of language to display language switch notification correctly
            
        
        #currency preset
        if self.currency=='$':
            self.button_dollar.set_active(True)

        elif self.currency=='£':
            self.button_pound.set_active(True)

        elif self.currency=='Kr':
            self.button_krone.set_active(True)

        else:
            #pass
            self.counter+=1 #set self.counter according to preeselection of language to display language switch notification correctly
        #self.counter=1
            

    def curr_button_toggled(self, button, curr):

        if button.get_active():
            self.currency=curr
            self.counter+=1
        else:
            pass #buttons turned off



    def lang_button_toggled(self, button, lang):
        #get the language changes
        if button.get_active():
            self.language=lang #button turned on save language choice to pref variable
            self.counter+=1
        else:
            pass #button turned off
  


        

#---------------------------------------Concat Window class--------------------------------------------

# Window is only shown if user selects concatenation

class Concat_Window(Gtk.Window):

#_____________________________________________ subsection window design_______________________________
    def __init__(self,input_list):
        

        Gtk.Window.__init__(self, title=langdict_gui['concatwin_header'][0])
        
        self.set_border_width(15)
        self.connect("delete_event", self.close_window)
        self.set_modal(True)

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        
        self.proceed=False #variable needed to clear concat_list, if  selection process wasn't successful
        self.window_active=True #necessary for outer loop waiting for window reply

        self.input_list=input_list

        self.concat_list=[]
        
        #Styling
        #vertical main box
        main_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        main_box.set_margin_top(10)
        self.add(main_box)
        
        #create selection grid (checkboxes)
        chk_grid = Gtk.Grid()
        chk_grid.set_column_spacing(20)
        chk_grid.set_row_spacing(15)
        chk_grid.set_row_homogeneous(False)
        main_box.pack_start(chk_grid,True,True,5)
        
        #button box
        bt_box=Gtk.Box()
        main_box.pack_start(bt_box,True,True,35)
        
        #buttons
        #cancel concatenation
        btn_nogo = Gtk.Button.new_with_label(langdict_gui['concatwin_btn1'][0])
        btn_nogo.connect("clicked",self.close_window,'btn')
        bt_box.pack_start(btn_nogo, True, True, 20)
        
        # continue button
        btn_go = Gtk.Button.new_with_label(langdict_gui['concatwin_btn2'][0])
        btn_go.connect("clicked",self.proceed_analysis)
        bt_box.pack_start(btn_go, True, True, 20)
    
        #set variables for grid size depending on number of input datasets(input_list)
        self.rows=len(self.input_list)
        
        
        if self.rows==2:
            self.cols=1
        elif self.rows==3:
            self.cols=3
        else:
            self.cols=6
        #create chk_grid

######################################################### Selection Grid Design Part #################################
        
        self.entrybox=[]        
        self.chkboxes = []
        

        #build checkbox grid with for loops
        #first loop through number of columns (depending on grid size given by imported data sets).
        #columns hold number of new files created (merged files)
        for colid in range(0,self.cols):
            
            self.chkboxes.append([])
            
            #empty label 
            chk_grid.attach(Gtk.Label(), 0, self.rows+1, 1, 1)
           
            #display label for respective entrybox of new file
            label_entry=Gtk.Label()
            label_entry.set_markup(eval(f"f'''{langdict_gui['concatwin_entryname'][0]}'''"))#eval function transforms f-string statements to be interpreted as f-strings
            label_entry.set_xalign(0) #styling
            chk_grid.attach(label_entry, 0, self.rows+colid+2, 1, 1)
            
            #build entrybox for entering name for new file
            self.entrybox.append(Gtk.Entry())
            self.entrybox[colid].set_sensitive(False)
            self.entrybox[colid].set_max_length(15)
            chk_grid.attach(self.entrybox[colid], 1, self.rows+colid+2, self.cols, 1)
            self.entrybox[0].set_sensitive(True) #activate first column
           
            #loop through rows (imported datasets which are supposed to be merged)

            for rowid in range(self.rows):
                
                #label of respective new file (file 1, file 2). The real name has to be set by user via entrybox 
                label_data = Gtk.Label.new(eval(f"f'''{langdict_gui['concatwin_choicename'][0]}'''"))#eval function transforms f-string statements to be interpreted as f-strings
                chk_grid.attach(label_data, colid+1, 0, 1, 1)
                
                #display names of datasets to be merged
                label_file = Gtk.Label.new(self.input_list[rowid])
                label_file.set_max_width_chars(15)
                label_file.set_line_wrap_mode(Pango.WrapMode.CHAR)
                label_file.set_line_wrap(True)
                label_file.set_xalign(0)
                
                chk_grid.attach(label_file, 0, rowid+1, 1, 1)
                
                self.chkboxes[colid].append(Gtk.CheckButton())
                #self.chkboxes[colid][rowid]=Gtk.CheckButton()
                self.chkboxes[colid][rowid].set_sensitive(False)
                self.chkboxes[colid][rowid].set_halign(Gtk.Align.CENTER) #align in center of column
                chk_grid.attach(self.chkboxes[colid][rowid], colid+1, rowid+1, 1, 1)
                self.chkboxes[0][rowid].set_sensitive(True)#activate first column
        
        GLib.timeout_add(200, self.check_columns)#while-loop for activating/deactivate entry and checkboxes
    
        self.show_all()
        
#_____________________________________________ subsection window/button functions_______________________________
    
    def close_window(self,widget,origin):
        if origin=='btn':
            self.close()#send close signal
        else:#close window
            if not self.proceed:#clear list if selection process wasn't successful
                self.concat_list=[]
            else: 
                pass
            Gtk.main_quit()


    def check_columns(self):
        #check for user choice and deactivate entryboxes and checkboxes which are not needed (e.g. first column is selected, third column is deactivated)
        selected=[]
        for colid in range(self.cols):
            selected.append([])
            for rowid in range(self.rows):
                if self.chkboxes[colid][rowid].get_active()==True:
                    selected[colid].append(rowid)
        
        #turn checkbox on and off depending on previous column
        #turn entrybox on depending on selection
        
        for colid in range(1,self.cols):
                     
            if len(selected[colid])>1:
                self.entrybox[colid].set_sensitive(True)
            else:
                self.entrybox[colid].set_sensitive(False)
                self.entrybox[colid].set_text('')
            
            if len(selected[colid-1])>1:
                for rowid in range(self.rows):
                    self.chkboxes[colid][rowid].set_sensitive(True)
            
            else:
                #self.entrybox[colid].set_sensitive(False)
                for rowid in range(0,len(self.input_list)):
                    self.chkboxes[colid][rowid].set_active(False)
                    self.chkboxes[colid][rowid].set_sensitive(False)
            
            for separ in range(1,self.cols):
                if ((len(selected[colid-(1+separ)])==1) and colid>separ):
                    #self.entrybox[colid].set_sensitive(False)
                    for rowid in range(self.rows):
                        self.chkboxes[colid][rowid].set_active(False)
                        self.chkboxes[colid][rowid].set_sensitive(False)
        return True
                
    def proceed_analysis(self,widget):
        #do several checks before proceeding. Check for minimum 2 files selected, if name for selection is provided and if it already exists

        namelist=['na']*self.cols
        
        checklist=[]
        for colid in range(self.cols):
            if not self.entrybox[colid].get_text()=='':
                if (self.entrybox[colid].get_text() in namelist) or (self.entrybox[colid].get_text() in self.input_list):
                    namelist[colid]='errorname'
                else:
                    namelist[colid]=self.entrybox[colid].get_text()
            #list append checkbox values
            temp=[]
            checklist.append([])
            for rowid in range(self.rows):
                if self.chkboxes[colid][rowid].get_active()==True:
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
            userproc.message.error(self,langdict_gui['concatwin_errselect'][0],langdict_gui['concatwin_errselect'][1])

        elif missingname==1:
            userproc.message.error(self,langdict_gui['concatwin_errnoname'][0],langdict_gui['concatwin_errnoname'][1])
            
        elif 'errorname' in namelist:
            userproc.message.error(self,langdict_gui['concatwin_errname'][0],langdict_gui['concatwin_errname'][1])
        else:
            if not self.concat_list==[]:
                userproc.message.info(self,langdict_gui['concatwin_succ'][0],langdict_gui['concatwin_succ'][1])
                self.proceed=True
                self.close()



#---------------------------------------Progressbar Window class--------------------------------------------

# show progressbar while doing the main data processing and plotting

class ProgressBarWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=langdict_gui['prgrsswin_header'][0])

        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)
        self.set_resizable(False)
        self.set_deletable(False)
        self.set_icon_from_file(iconfilepath) #needed to be defined separately as progressbar is a spawned process in windows
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_margin_bottom(10)
        self.add(main_box)
        
        image = Gtk.Image()
        image.set_from_file(kysaimagepath)

        # add the image to the window
        main_box.pack_start(image, True, True,0)

        #create progressbar
        self.progressbar = Gtk.ProgressBar()
        self.activity_mode = True#nececessary for controlling progressbar
        main_box.pack_start(self.progressbar, True, True, 0)

        #start timer-loop for contanstly doing progress pulsation and queuecheck
        timeout_queue=GLib.timeout_add(100, self.main_timeout, None)
        self.show_all()

#_____________________________________________ subsection window/button functions_______________________________

    def main_timeout(self, user_data):
    #Update value on the progress bar
        if self.activity_mode:
        	#make progressbar bumping from one side to another
            self.progressbar.pulse()

       

        return True

    

    def userinformation(self,msg,data):
    	# this function is only needed for the queue interaction with the main processing running in a separate process
        title1,title2=data

        if msg=='process_error':
            self.activity_mode=False
            userproc.message.error(self,title1,title2)
            self.close()
        elif msg=='process_start':
            self.activity_mode=False
            userproc.message.info(self,title1,title2)
            self.set_title(langdict_gui['prgrsswin_visualinfo'][0])
            self.activity_mode=True
        elif msg=='process_end':
            self.activity_mode=False
            userproc.message.info(self,title1,title2)
            self.close()
        
