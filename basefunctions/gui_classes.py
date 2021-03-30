'''Main File holding classes and functions necessary for building GTK3-based GUI
This file really just builds the GUI with its subwindows. Main calculations are stored in user_process.py. The GUI reverts to those functions whenever necessary '''

import time
import os
import platform
import random
import sys
import webbrowser
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, Gio, GLib, Pango

from basefunctions import gui_vars as guivar
from basefunctions import user_process as userproc


#--------------------------------------Import style adaptions-----------------------------------

#style is defined in GUIVers file


style_provider = Gtk.CssProvider()
style_provider.load_from_data(bytes(guivar.KYSA_css.encode()))
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )


#--------------------------------------Platform specific constructions-------------------------


#import supplementary data (icons and readmes)

if not getattr(sys, "frozen", False): #get local folder path for subfolder 'suppldata' when not frozen

    PATH_SUPPLDATA = os.path.join(os.getcwd(), "suppldata")

else:
    PATH_SUPPLDATA = os.path.join(sys.prefix, "suppldata")


PATH_ICON = os.path.join(PATH_SUPPLDATA, 'KYSA-Icon_64.icns')
PATH_README = os.path.join(PATH_SUPPLDATA, 'KYSA_Readme_'+userproc.LANG_CHOICE+'.html')
PATH_LICENSE = os.path.join(PATH_SUPPLDATA, 'KYSA_License_'+userproc.LANG_CHOICE+'.html')
PATH_PROGRESS_PIC = os.path.join(PATH_SUPPLDATA, 'KYSA-Progress_pic.png')
PATH_COPYCODE = os.path.join(PATH_SUPPLDATA, 'CRcode.png')#load to make sure png is present

#get language setting and import language dictionary
open(PATH_COPYCODE) #load to make sure png is present
LANGDICT_USED = userproc.LANGDICT_USED #necessary extra variable definition for KYSA.py to get language information
LANGDICT_GUI = LANGDICT_USED['GUI_Final_vars']



#---------------------------------------Main Window class--------------------------------------------


class MainWindow(Gtk.ApplicationWindow):

#_____________________________________________ subsection window design_______________________________
    def __init__(self, progressqueue):


        #Window properties
        Gtk.Window.__init__(self, title="KYSA - Know Your Spendings")
        self.set_default_size(200, 100)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)
        self.connect("delete_event", self.close_window)
        self.set_resizable(False)


        self.set_default_icon_from_file(PATH_ICON)#

        self.selection_counter = 0#necessary for popup notices

        copycode = Gtk.Image()
        copycode.set_from_file(PATH_COPYCODE)

        #create progressbar window and hide it
        self.progresswin = ProgressBarWindow(self, progressqueue) #create window for progressbar
        self.progresswin.hide() #hide progress bar
######################################################### Menu Part #################################

      	#setup menubar and link to menu functions
      	## menu main structure is defines in xml-part in GuiVars


        menubar = Gtk.HeaderBar()
        menubar.set_show_close_button(True)
        menubar.set_title("KYSA")
        menubar.set_subtitle("Know Your Spendings")
        self.set_titlebar(menubar)

        #load language specific menu
        if userproc.LANG_CHOICE == 'eng':
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

        act_readme = Gio.SimpleAction.new('readme', None)
        act_readme.connect('activate', self.show_readme)
        self.add_action(act_readme)

        act_license = Gio.SimpleAction.new('license', None)
        act_license.connect('activate', self.show_license)
        self.add_action(act_license)

        act_chglog = Gio.SimpleAction.new('changelog', None)
        act_chglog.connect('activate', self.show_chglog)
        self.add_action(act_chglog)

        act_classtbl = Gio.SimpleAction.new('classtbl', None)
        act_classtbl.connect('activate', self.set_folders, 'classdir')
        self.add_action(act_classtbl)

        act_resfolder = Gio.SimpleAction.new('resdir', None)
        act_resfolder.connect('activate', self.set_folders, 'resdir')
        self.add_action(act_resfolder)

        act_uisettings = Gio.SimpleAction.new('uiset', None)
        act_uisettings.connect('activate', self.ui_settings)
        self.add_action(act_uisettings)

        act_accountnames = Gio.SimpleAction.new('accnames', None)
        act_accountnames.connect('activate', self.acc_names_set)
        self.add_action(act_accountnames)

        act_donate = Gio.SimpleAction.new('donate', None)
        act_donate.connect('activate', self.show_donate)
        self.add_action(act_donate)


        act_quit = Gio.SimpleAction.new('quit', None)
        act_quit.connect('activate', self.close_window)
        self.add_action(act_quit)



######################################################### Buttons Design Part #################################

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6) #create vertical oriented gridbox
        self.add(main_box)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT) #Switch between xls and csv
        self.stack.set_vhomogeneous(False)
        self.stack.set_transition_duration(100)

        #gridboxes for user selection (checkboxes).

        # Base_grid Box holds selections that can be chosen for xls and csv analysis
        base_grid = Gtk.Grid()

        #language specific spacing between label and checkbox column
        if userproc.LANG_CHOICE == 'eng':
            if platform.system() == 'Darwin':
                base_grid.set_column_spacing(32)
                csv_adjustvar = -21.5
            else:
                base_grid.set_column_spacing(30)
                csv_adjustvar = -30.5
        else:
            if platform.system() == 'Darwin':
                base_grid.set_column_spacing(45)
                csv_adjustvar = -7
            else:
                base_grid.set_column_spacing(40)
                csv_adjustvar = -13.5

        base_grid.set_row_spacing(15)

        #csv grid holds those user elective checkboxes that can only be run on csv-data
        csv_grid = Gtk.Grid()
        csv_grid.set_column_spacing(base_grid.get_column_spacing()-csv_adjustvar)
        csv_grid.set_row_spacing(15)

        #labels in grids
        grid_l_lst = [LANGDICT_GUI['mainwin_choice3'][0], LANGDICT_GUI['mainwin_choice4'][0], LANGDICT_GUI['mainwin_choice5'][0],
                      LANGDICT_GUI['mainwin_choice6'][0], LANGDICT_GUI['mainwin_choice7'][0], LANGDICT_GUI['mainwin_choice8'][0]]



        #checkboxes in grids
        self.grid_chk_lst = [Gtk.CheckButton(), Gtk.CheckButton(), Gtk.CheckButton(), Gtk.CheckButton(), Gtk.CheckButton(), Gtk.CheckButton()]

        grids = [(base_grid, 0, 5), (csv_grid, 5, len(grid_l_lst))] #tuple containing lower and upper limits



        #create booth grids with label and checkbox
        for item in grids:
            #adjust index depending on grid


            for num in range(item[1], item[2]): #range from lower to upper limit in respective grid
            #label
                label = Gtk.Label().new(grid_l_lst[num])
                label.set_max_width_chars(40)
                label.set_line_wrap(True)
                label.set_xalign(0)

                item[0].attach(label, 0, num-item[1], 1, 1) #adjust num with lower limit
                #checkbox
                self.grid_chk_lst[num].set_halign(Gtk.Align.END)
                item[0].attach(self.grid_chk_lst[num], 1, num-item[1], 1, 1)


        self.stack.add_titled(csv_grid, "csv_analyse", LANGDICT_GUI['mainwin_choice1'][0])

        xls_box = Gtk.Box()
        self.stack.add_titled(xls_box, "xls_analyse", LANGDICT_GUI['mainwin_choice2'][0])

        #separation between switch and base grid
        separator_label = Gtk.Label()
        separator_label.set_markup(LANGDICT_GUI['mainwin_separator_text'][0])
        separator_label.set_name("separator_label")

        #create main window
        stack_switcher = Gtk.StackSwitcher() #Establish xls-csv-switch
        stack_switcher.set_stack(self.stack)
        stack_switcher.set_halign(Gtk.Align.CENTER)

        #pack switch and selection boces
        main_box.pack_start(stack_switcher, False, True, 5)
        main_box.pack_start(separator_label, False, True, 15)
        main_box.pack_start(base_grid, False, True, 0)
        main_box.pack_start(self.stack, True, False, 5)

        #browse files button
        bws_btn = Gtk.Button.new_with_label(LANGDICT_GUI['mainwin_btn1'][0])
        bws_btn.connect("clicked", self.browse_files)
        bws_btn.set_name("bws_btn")
        bws_btn.set_size_request(0, 45)
        main_box.pack_start(bws_btn, False, False, 15)

        #start calculation button
        run_btn = Gtk.Button.new_with_label(LANGDICT_GUI['mainwin_btn2'][0])
        run_btn.connect("clicked", self.run_program)
        run_btn.set_name("run_btn")
        run_btn.set_size_request(0, 55)
        main_box.pack_start(run_btn, False, False, 5)

        #set timer for readjusting window size depending on csv/xls-selection
        GLib.timeout_add(100, self.window_resize, None)

        #set timer for checking class table
        GLib.timeout_add(500, self.check_classtable, None)


        self.mfunc = userproc.MainFunctions(self)#start main function with this window as master

        #deactivate longterm-data evaluation check box if no longterm-data is stored
        if self.mfunc.saved_dataframe == {}:
            self.grid_chk_lst[4].set_sensitive(False)

        else:
            pass #nothing to do

        self.show_all()

        if userproc.STARTCOUNT == 0:
            uisettings_win = UISettingsWindow(self) #start Language selection with first program start


#_____________________________________________ subsection window/button functions_______________________________

    def window_resize(self, user_data):

        self.resize(100, 50)
        return True

    def check_classtable(self, user_data):
        self.mfunc.set_classtable('import')
        return False

    def selection_adapt(self): #check for current choice and adjust to xls/csv-selection
        #selected choices variables


        self.choice_dtype = self.stack.get_visible_child_name()

        if self.selection_counter == 0:#adjust popup counters
            if userproc.STARTCOUNT < 2:
                userproc.STARTCOUNT += 1
                if self.choice_dtype == 'xls_analyse':
                    userproc.message.info(self, LANGDICT_GUI['mainwin_xlsxinfo'][0], LANGDICT_GUI['mainwin_xlsxinfo'][1])
                else:
                    pass
            else:
                userproc.STARTCOUNT = random.randint(2, 1000)

        #deactivate csv-specific choice if xls is selected
        if self.choice_dtype == 'xls_analyse':
            self.grid_chk_lst[5].set_active(False)
            self.choice_conc_xls = False

        else:
            self.choice_conc_xls = self.grid_chk_lst[5].get_active()



        self.selection_counter += 1

    def browse_files(self, widget):

    	#function belonging to browse button

        self.selection_adapt()#check user selection

        if self.choice_dtype == 'xls_analyse':
            purpose = 'raw_data_excel'
        else:
            purpose = 'raw_data_csv'

        self.mfunc.filebrowser(purpose) #open filebrowser fundtion in MainFunc Class


        #remind user to donate
        if (userproc.STARTCOUNT%7 == 0 or userproc.STARTCOUNT%5 == 0) and userproc.STARTCOUNT != 0:
            self.donate_popup()
        else:
            pass

    def run_program(self, widget):
        #function belonging to start calculation button
        #hide main window and show progressbar
        proceed = False

        self.unrealize()
        self.hide() #hide main window
        self.selection_adapt()#get selection type and specific csv selections
        #get selected variables
        choice_hol = self.grid_chk_lst[0].get_active()
        choice_sav = self.grid_chk_lst[1].get_active()
        choice_conc = self.grid_chk_lst[2].get_active()
        choice_cash = self.grid_chk_lst[3].get_active()
        choice_longterm = self.grid_chk_lst[4].get_active()

        user_choice = (self.choice_dtype, choice_hol, choice_sav, choice_conc, choice_cash, choice_longterm, self.choice_conc_xls)

        proceed = self.mfunc.start_analysis(user_choice)# start analysis. Proceed stays false if no files are selected

        if proceed: #if import starts show progresswin
            self.progresswin.activity_mode = True #start pulsation
            self.progresswin.show_all()
            
        else:
            self.show_all()


    def open_concatwindow(self, input_list):
        #if concat choice is correctly chosen, this function calls for the Concat Window and keeps it open
        concat_list = ConcatWindow(input_list)
        Gtk.main()
        
        return concat_list


    def donate_popup(self):
        if userproc.STARTCOUNT%7 == 0 or userproc.STARTCOUNT%5 == 0:
            userchoice = userproc.message.question(self, LANGDICT_GUI['mainwin_donatinfo'][0], LANGDICT_GUI['mainwin_donatinfo'][1])
            if userchoice:
                donate_win = DonateWindow(self)
        else:
            pass




###################################### Menu Fundtions Part #################################

# these funcions belong to the menu build part and connect to the menu structure given in XML file of GuiVars


    def show_readme(self, action, value):
        webbrowser.open('file://'+PATH_README, new=1)

    def show_license(self, action, value):
        webbrowser.open('file://'+PATH_LICENSE, new=1)

    def show_about(self, action, value):
        aboutdialog = Gtk.AboutDialog()
        authors = ["Daniel Krezdorn"]
        aboutdialog.set_program_name("KYSA\nKnow Your Spendings Application")
        aboutdialog.set_copyright("\xa9 2021 Daniel Krezdorn")
        aboutdialog.set_authors(authors)
        aboutdialog.set_version(guivar.versions[0])
        aboutdialog.set_license_type(Gtk.License.BSD_3) #Changed to BSD 3 from BSD 2 (currently not suported by PyGobject version)
        aboutdialog.set_website(LANGDICT_GUI['aboutwin_link'][0]) #link
        aboutdialog.set_website_label(LANGDICT_GUI['aboutwin_link'][1])# displayed text for link

        aboutdialog.set_title(LANGDICT_GUI['aboutwin_title'][0])
        aboutdialog.show()

    def show_chglog(self, action, value):

        chglog_win = ChglogWindow(self)

    def show_donate(self, action, value):

        donate_win = DonateWindow(self)

    def ui_settings(self, action, value):

        uisettings_win = UISettingsWindow(self)

    def acc_names_set(self, action, value):
        accsettings_win = AccSettingsWindow(self)
        #passuisettings_win=UISettingsWindow(self)


    def set_folders(self, action, value, purpose):
        if purpose == 'classdir':
            classtbl_success = self.mfunc.set_classtable('change') #link to classtable check function; variable classtable_success necessary as functions returns value for user_process script

        elif purpose == 'resdir':
            self.mfunc.filebrowser('resdir')

    def close_window(self, widget, origin):#used by menu entry quit and close event

        self.mfunc.save_prefs()#save preferences
        self.mfunc.encrypt_datasets()

        self.choice_dtype = 'stop_analysis'
        Gtk.main_quit()



#---------------------------------------Changelog Window class--------------------------------------------

#start extra window for changelog. Changlog entries are created in GUIVars file as loopable list

class ChglogWindow(Gtk.Window):
    def __init__(self, master):

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
        self.main_box.pack_start(scrolledwindow, True, True, 0)

        # main text box
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        #connect text box to scrollable window
        text_view = Gtk.Viewport()
        text_view.add(text_box)
        scrolledwindow.add(text_view)

        # main label header
        label_header = Gtk.Label()
        label_header.set_markup("<big>Changelog\n</big>")
        label_header.set_name("separator_label")
        text_box.pack_start(label_header, True, True, 0)

        version_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        #loop through changeloglist created in GUIVars. Every list entry holds a tuple. First position in tuple holds version number, the second the changes being applied
        for i in range(len(guivar.chglog_list)):
            label_ver = Gtk.Label()
            label_ver.set_markup(f"<b>{guivar.chglog_list[i][0]}</b>")
            label_ver.set_xalign(0)

            label_chg = Gtk.Label.new(guivar.chglog_list[i][1])
            label_chg.set_line_wrap_mode(Pango.WrapMode.WORD)
            label_chg.set_line_wrap(True)
            label_chg.set_xalign(0)

            #pack labels within version_textbox
            version_box.pack_start(label_ver, True, True, 2)
            version_box.pack_start(label_chg, True, True, 0)

        text_box.pack_start(version_box, True, True, 0)

        self.show_all()


#---------------------------------------Donation Window class--------------------------------------------

#start extra window for donation info.

class DonateWindow(Gtk.Window):
    def __init__(self, master):

        Gtk.Window.__init__(self, title=LANGDICT_GUI['donatewin_header'][0])

        self.set_default_size(300, 50)
        self.set_resizable(False)
        self.set_size_request(300, 50)
        self.set_position(Gtk.WindowPosition.CENTER)
        #self.set_transient_for(master)
        #self.set_modal(True)
        #self.set_keep_above(True)

        #design part
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.add(main_box)

        # main label header
        label_header = Gtk.Label()
        label_header.set_markup(LANGDICT_GUI['donatewin_title'][0])
        label_header.set_name("separator_label")
        main_box.pack_start(label_header, True, True, 15)





        label_content = Gtk.Label(label=LANGDICT_GUI['donatewin_text'][0])


        label_content.set_line_wrap_mode(Pango.WrapMode.WORD)
        label_content.set_line_wrap(True)
        label_content.set_max_width_chars(60) #necessary for windows compatibility
        #label_content.set_xalign(0)
        main_box.pack_start(label_content, True, True, 10)


        label_link = Gtk.LinkButton.new_with_label(LANGDICT_GUI['donatewin_link'][0], LANGDICT_GUI['donatewin_link'][1])
        main_box.pack_start(label_link, True, True, 10)

        self.show_all()


#start extra window for language settings

class UISettingsWindow(Gtk.Window):
    def __init__(self, master):

        Gtk.Window.__init__(self, title=LANGDICT_GUI['setuiwin_header'][0])

        self.set_default_size(300, 50)
        self.set_resizable(False)
        self.set_size_request(300, 50)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_transient_for(master)
        self.set_modal(True)
        self.master = master

        self.counter = 0
        self.language = userproc.LANG_CHOICE
        self.currency = userproc.CURRENCY_CHOICE

        #design part
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.add(main_box)

        # main label title
        label_header = Gtk.Label()
        label_header.set_markup(LANGDICT_GUI['setuiwin_title'][0])
        label_header.set_name("separator_label")
        label_header.set_padding(10, 15)
        main_box.pack_start(label_header, True, True, 0)


        hbox_grid = Gtk.Grid()
        hbox_grid.set_row_spacing(20)
        hbox_grid.set_column_spacing(50)
        hbox_grid.set_row_homogeneous(False)
        hbox_grid.set_column_homogeneous(False)
        hbox_grid.set_halign(Gtk.Align.CENTER)

        label_lang = Gtk.Label()
        label_lang.set_markup(LANGDICT_GUI['setuiwin_choicelabel'][0])
        label_lang.set_halign(Gtk.Align.CENTER)
        hbox_grid.attach(label_lang, 0, 0, 1, 1)

        label_curr = Gtk.Label()
        label_curr.set_markup(LANGDICT_GUI['setuiwin_choicelabel'][1])
        label_curr.set_halign(Gtk.Align.CENTER)
        hbox_grid.attach(label_curr, 1, 0, 1, 1)


        vbox_lang = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox_curr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

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
        button_euro = Gtk.RadioButton.new_with_label_from_widget(None, LANGDICT_GUI['setuiwin_currencies1'][0])
        button_euro.connect("toggled", self.curr_button_toggled, "€")
        vbox_curr.pack_start(button_euro, True, True, 0)

        #Dollar
        self.button_dollar = Gtk.RadioButton.new_from_widget(button_euro)
        self.button_dollar.set_label(LANGDICT_GUI['setuiwin_currencies1'][1])
        self.button_dollar.connect("toggled", self.curr_button_toggled, "$")
        vbox_curr.pack_start(self.button_dollar, True, True, 0)

        #Pound
        self.button_pound = Gtk.RadioButton.new_from_widget(button_euro)
        self.button_pound.set_label(LANGDICT_GUI['setuiwin_currencies2'][0])
        self.button_pound.connect("toggled", self.curr_button_toggled, "£")
        vbox_curr.pack_start(self.button_pound, True, True, 0)

        #Krone
        self.button_krone = Gtk.RadioButton.new_from_widget(button_euro)
        self.button_krone.set_label(LANGDICT_GUI['setuiwin_currencies2'][1])
        self.button_krone.connect("toggled", self.curr_button_toggled, "Kr")
        vbox_curr.pack_start(self.button_krone, True, True, 0)

        vbox_curr.set_halign(Gtk.Align.CENTER)

        hbox_grid.attach(vbox_lang, 0, 1, 1, 1)

        hbox_grid.attach(vbox_curr, 1, 1, 1, 1)


        ################# Save Preferences Button#####

        save_btn = Gtk.Button.new_with_label(LANGDICT_GUI['setuiwin_btn'][0])
        save_btn.connect("clicked", self.save_prefs)
        save_btn.set_size_request(0, 40)
        hbox_grid.attach(save_btn, 0, 2, 2, 1)


        main_box.pack_start(hbox_grid, True, True, 10)

        if self.counter == 0:
            self.get_saved_prefs()

        self.show_all()

    def save_prefs(self, widget):

        closeproc_choice = False #necessary for automated program closure


        if self.counter > 2:
            #user changed selection
            closeproc_choice = userproc.message.question(self, LANGDICT_GUI['setuiwin_newchoice'][0], LANGDICT_GUI['setuiwin_newchoice'][1])

            #save preferences whenever a new choice was selected
            userproc.LANG_CHOICE = self.language
            userproc.CURRENCY_CHOICE = self.currency

        else:
            #no user selection
            userproc.message.info(self, LANGDICT_GUI['setuiwin_nochoice'][0], LANGDICT_GUI['setuiwin_nochoice'][1])

        #adjust STARTCOUNT necessary for UI window popup with very first program start
        userproc.STARTCOUNT += 1

        #close program if user pressed ok
        if closeproc_choice:
            self.close()
            self.master.close()
        else:
            self.close()

    def get_saved_prefs(self):
        #turn buttons on based on saved value in prefs file

        #language preset
        if self.language == 'eng':
            self.button_eng.set_active(True)
        else:
            #pass
            self.counter += 1 #set self.counter according to preeselection of language to display language switch notification correctly


        #currency preset
        if self.currency == '$':
            self.button_dollar.set_active(True)

        elif self.currency == '£':
            self.button_pound.set_active(True)

        elif self.currency == 'Kr':
            self.button_krone.set_active(True)

        else:
            #pass
            self.counter += 1 #set self.counter according to preeselection of language to display language switch notification correctly
        #self.counter=1


    def curr_button_toggled(self, button, curr):

        if button.get_active():
            self.currency = curr
            self.counter += 1
        else:
            pass #buttons turned off



    def lang_button_toggled(self, button, lang):
        #get the language changes
        if button.get_active():
            self.language = lang #button turned on save language choice to pref variable
            self.counter += 1
        else:
            pass #button turned off


#---------------------------------------Account Settings and Account Names Window class--------------------------------------------

class AccSettingsWindow(Gtk.Window):
#_____________________________________________ subsection window design accsettings_______________________________
    def __init__(self, master):

        self.accsetting_master = master
        Gtk.Window.__init__(self, title=LANGDICT_GUI['accsettingswin_header'][0])

        self.set_position(Gtk.WindowPosition.CENTER)

        self.set_transient_for(self.accsetting_master)
        self.set_modal(True)
        self.set_border_width(15)

        self.saved_dataframe = master.mfunc.saved_dataframe

        if userproc.ACCOUNT_NAMES != []: #if account names were set use them
            self.acc_names_show = userproc.ACCOUNT_NAMES
        else:# if menu is entered after accounts were already analysed use those keys
            self.acc_names_show = list(self.saved_dataframe.keys())

        self.update_window()#draw inner entries

######################################################### Account Names Altering Design Part #################################

    def update_window(self): #draws the window and updates the entries


        try:
            self.settings_grid.destroy() #destroy outer box and create new one
        except:
            pass
        self.settings_grid = Gtk.Grid() #main box with label
                #create grid to arrange labels and buttons
        self.settings_grid.set_column_spacing(20)
        self.settings_grid.set_row_spacing(18)
        self.settings_grid.set_row_homogeneous(False)

        self.settings_grid.set_halign(Gtk.Align.CENTER)

        self.add(self.settings_grid)

        self.acc_names_show = sorted(self.acc_names_show) #sort lsit after every change
        #set title in window
        label_title = Gtk.Label()
        label_title.set_markup('<big>'+LANGDICT_GUI['accsettingswin_header'][1]+'</big>')
        label_title.set_name("separator_label")
        label_title.set_padding(10, 15)
        self.settings_grid.attach(label_title, 0, 0, 3, 1)

        #import icons for buttons
        icon_delete = Gio.ThemedIcon.new("edit-delete-symbolic") # include menu symbol
        image_delete = Gtk.Image.new_from_gicon(icon_delete, Gtk.IconSize.BUTTON)

        icon_edit = Gio.ThemedIcon.new("document-edit-symbolic") # include menu symbol
        image_edit = Gtk.Image.new_from_gicon(icon_edit, Gtk.IconSize.BUTTON)

        icon_addfile = Gio.ThemedIcon.new("list-add-symbolic") # include menu symbol
        image_addfile = Gtk.Image.new_from_gicon(icon_addfile, Gtk.IconSize.BUTTON)

        #define lists to be able to set buttons
        delete_imagelist = []
        edit_imagelist = []
        delete_buttons_list = []
        edit_buttons_list = []

        #set row length
        row_length = len(self.acc_names_show)

        #set describing label for accounts
        desc_label = Gtk.Label()
        desc_label.set_markup('<b>'+LANGDICT_GUI['accsettingswin_descrlabel'][0]+'</b>')
        desc_label.set_xalign(0)
        self.settings_grid.attach(desc_label, 0, 1, 1, 1)


        if row_length != 0:

            for rowid in range(0, row_length):

                #set label for this (rowid) account name
                label_file = Gtk.Label()
                label_file.set_markup('<b>'+self.acc_names_show[rowid]+':</b>')
                label_file.set_max_width_chars(16)
                label_file.set_line_wrap_mode(Pango.WrapMode.WORD)
                label_file.set_line_wrap(True)
                label_file.set_xalign(0)
                self.settings_grid.attach(label_file, 0, rowid+2, 1, 1)

                #create delete button for this account name
                delete_imagelist.append(Gtk.Image.new_from_gicon(icon_delete, Gtk.IconSize.BUTTON))
                delete_buttons_list.append(Gtk.Button())
                delete_buttons_list[rowid].add(delete_imagelist[rowid])
                delete_buttons_list[rowid].connect("clicked", self.del_accname, rowid)
                self.settings_grid.attach(delete_buttons_list[rowid], 2, rowid+2, 1, 1)

                #create edit button for this account name
                edit_imagelist.append(Gtk.Image.new_from_gicon(icon_edit, Gtk.IconSize.BUTTON))
                edit_buttons_list.append(Gtk.Button())
                edit_buttons_list[rowid].add(edit_imagelist[rowid])
                edit_buttons_list[rowid].connect("clicked", self.edit_accname, rowid)
                self.settings_grid.attach(edit_buttons_list[rowid], 1, rowid+2, 1, 1)

        #add add button at end
        add_button = Gtk.Button()
        add_button.add(image_addfile)
        add_button.connect("clicked", self.add_accname, None)
        self.settings_grid.attach(add_button, 0, row_length+2, 1, 1)

        close_button = Gtk.Button.new_with_label(LANGDICT_GUI['accsettingswin_closebtn'][0])
        close_button.connect("clicked", self.close_window)
        self.settings_grid.attach(close_button, 0, row_length+3, 3, 1)


        self.show_all()


######################################################### Account Names Altering Function Part #################################


    def del_accname(self, widget, rowid):

        try:
            del self.saved_dataframe[self.acc_names_show[rowid]] #delete dataframe in saved files if existing
        except:
            pass #nothing to do if name not in saved dataframe
        del self.acc_names_show[rowid] #remove the respective account name
        self.update_window()


    def edit_accname(self, widget, rowid): #change the respective account name

        entry = SetAccNameWindow(self, 'change', rowid)

    def add_accname(self, widget, rowid): #add a new account name

        entry = SetAccNameWindow(self, 'add', rowid)

    def close_window(self, widget):
        userproc.ACCOUNT_NAMES = self.acc_names_show# save altered account names to prefs file
        self.close()


class SetAccNameWindow(Gtk.Window):
    #_____________________________________________ subsection window design accnames_______________________________
    def __init__(self, master, purpose, rowid):

        Gtk.Window.__init__(self, title=LANGDICT_GUI['setaccnamewin_header'][0])

        self.master_accnames = master
        self.purpose = purpose
        self.rowid = rowid

        self.set_border_width(7)

        self.set_transient_for(master)
        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.MOUSE)

        entry_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(entry_box)

        #load icons for accept and cancel button
        icon_accept = Gio.ThemedIcon.new("object-select-symbolic") # include menu symbol
        image_accept = Gtk.Image.new_from_gicon(icon_accept, Gtk.IconSize.BUTTON)

        icon_cancel = Gio.ThemedIcon.new("window-close-symbolic") # include menu symbol
        image_cancel = Gtk.Image.new_from_gicon(icon_cancel, Gtk.IconSize.BUTTON)

        #set entrybox and label

        entry_label = Gtk.Label()
        if purpose == 'add':
            entry_label.set_markup(LANGDICT_GUI['setaccnamewin_entrylabel'][0])
        else:
            entry_label.set_markup(LANGDICT_GUI['setaccnamewin_entrylabel'][1])
        entry_label.set_max_width_chars(25)
        entry_label.set_line_wrap_mode(Pango.WrapMode.WORD)
        entry_label.set_line_wrap(True)
        entry_label.set_xalign(0)
        entry_box.pack_start(entry_label, True, True, 2)

        #set entry field
        self.entry_box = Gtk.Entry()
        self.entry_box.set_max_length(20) #maximum characters per account
        entry_box.pack_start(self.entry_box, True, True, 2)

        #set button grid
        buttons_box = Gtk.Box(spacing=5)
        entry_box.pack_start(buttons_box, True, True, 2)

        #define accept and cancel buttons
        cancel_button = Gtk.Button()
        cancel_button.add(image_cancel)
        cancel_button.connect("clicked", self.close_window)
        buttons_box.pack_start(cancel_button, True, True, 2)

        accept_button = Gtk.Button()
        accept_button.add(image_accept)
        accept_button.connect("clicked", self.check_name)
        buttons_box.pack_start(accept_button, True, True, 2)

        self.show_all()#

######################################################### Enter Account Names Function Part #################################

    def check_name(self, widget):

        #check entered name and keep field open until a unique name is entered or canceled
        self.entry_accname = self.entry_box.get_text()

        if self.entry_accname == '':
            userproc.message.error(self, LANGDICT_GUI['setaccnamewin_errnoname'][0], LANGDICT_GUI['setaccnamewin_errnoname'][1])
            #userproc.message.error(self, 'Kein Name''Es wurde nichts eingegeben')
        elif self.entry_accname in self.master_accnames.acc_names_show:
            userproc.message.error(self, LANGDICT_GUI['setaccnamewin_errname'][0], LANGDICT_GUI['setaccnamewin_errname'][1])
            #userproc.message.error(self, 'Falscher Name''Der Kontoname wird schon verwendet')
        else:
            if self.purpose == 'add':
                self.master_accnames.acc_names_show.append(self.entry_accname)#add new name to files
            elif self.purpose == 'change':
                old_name = self.master_accnames.acc_names_show[self.rowid] #old account name

                if old_name in self.master_accnames.saved_dataframe.keys(): #if the name was already used in the saved data field change it
                    self.master_accnames.saved_dataframe[self.entry_accname] = self.master_accnames.saved_dataframe.pop(old_name)
                else:
                    pass #nothing to do

                self.master_accnames.acc_names_show[self.rowid] = self.entry_accname #change old name to new name

            self.master_accnames.update_window()

            self.close_window('finish')


    def close_window(self, widget):
        self.close() #close set name window



#---------------------------------------Account-Imported Files Allocation Window class--------------------------------------------

class FileAccLinkWindow(Gtk.Window):
#_____________________________________________ subsection window design_______________________________
    def __init__(self, master, imported_files):


        Gtk.Window.__init__(self, title=LANGDICT_GUI['fileacclinkwin_header'][0])

        self.connect("delete_event", self.close_window)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_deletable(False)
        self.set_modal(True)
        self.set_border_width(15)
        self.accounts_data = master.master.mfunc.accounts_data
        self.check_loop = True

        #import lists
        self.acc_names = userproc.ACCOUNT_NAMES
        self.imported_files = imported_files #list of successfully imported files
        self.rows = len(self.imported_files) #length of imported files list defines number of rows
        self.cols = len(self.acc_names) #length of account names defines number of columns

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        self.add(main_box)


        #set title in window
        label_title = Gtk.Label()
        label_title.set_markup('<big>'+LANGDICT_GUI['fileacclinkwin_header'][0]+'</big>') #same as header
        label_title.set_name("separator_label")
        main_box.pack_start(label_title, True, True, 10)


        #create selection grid (checkboxes)
        chk_grid = Gtk.Grid()
        chk_grid.set_column_spacing(20)
        chk_grid.set_row_spacing(15)
        chk_grid.set_row_homogeneous(False)
        main_box.pack_start(chk_grid, True, True, 0)

        #add add button at end
        add_button = Gtk.Button.new_with_label(LANGDICT_GUI['fileacclinkwin_proceed'][0])
        add_button.connect("clicked", self.proceed)
        main_box.pack_start(add_button, True, True, 5)
        ######################################################### Selection Grid Design Part #################################
        accnames_desc = Gtk.Label()
        accnames_desc.set_markup('<b>'+LANGDICT_GUI['fileacclinkwin_collabels'][0]+'</b>')#eval function transforms f-string statements to be interpreted as f-strings
        chk_grid.attach(accnames_desc, 1, 0, self.cols, 1)

        imports_desc = Gtk.Label()
        imports_desc.set_markup('<b>'+LANGDICT_GUI['fileacclinkwin_collabels'][1]+'</b>')#eval function transforms f-string statements to be interpreted as f-strings
        imports_desc.set_max_width_chars(15)
        imports_desc.set_line_wrap_mode(Pango.WrapMode.WORD)
        imports_desc.set_line_wrap(True)
        imports_desc.set_xalign(0)
        chk_grid.attach(imports_desc, 0, 0, 1, 2)

        self.chkboxes = []

        self.selected = []

        #build checkbox grid with for loops
        #first loop through number of columns (depending on grid size given by imported data sets).
        #rows hold number of imported files which are supposed to be linked to one account name)
        for rowid in range(self.rows):


            self.selected.append([])
            #self.
            #display names of datasets to be merged
            label_file = Gtk.Label.new(self.imported_files[rowid]+':') 
            label_file.set_max_width_chars(15)
            label_file.set_line_wrap_mode(Pango.WrapMode.WORD)
            label_file.set_line_wrap(True)
            label_file.set_xalign(0)

            chk_grid.attach(label_file, 0, rowid+2, 1, 1)

            self.chkboxes.append([]) #create enpty


            #loop through columns (account names)
            for colid in range(self.cols):
                ACCOUNT_NAMES = Gtk.Label.new(self.acc_names[colid])#eval function transforms f-string statements to be interpreted as f-strings
                chk_grid.attach(ACCOUNT_NAMES, colid+1, 1, 1, 1)



                self.chkboxes[rowid].append(Gtk.CheckButton())
                self.chkboxes[rowid][colid].set_halign(Gtk.Align.CENTER) #align in center of column
                chk_grid.attach(self.chkboxes[rowid][colid], colid+1, rowid+2, 1, 1)

        GLib.timeout_add(300, self.check_columns)#while-loop for activating/deactivate entry and checkboxes

        self.show_all()

#_____________________________________________ subsection window functions_______________________________


    def check_columns(self):

        for rowid in range(self.rows):
            for colid in range(self.cols):
                #check if for filename (rowid) the box in the account name (colid) was checked and add to selection list if not already existing 
                if self.chkboxes[rowid][colid].get_active() == True and colid not in self.selected[rowid]: 
                    self.selected[rowid].append(colid)
                #check if a previously selected filename (rowid)- account name (colid) connection was revoked. If yes delete entry from selection list
                elif self.chkboxes[rowid][colid].get_active() != True and colid in self.selected[rowid]:
                    self.selected[rowid].remove(colid)

            if len(self.selected[rowid]) > 1:
                self.chkboxes[rowid][self.selected[rowid][0]].set_active(False)
                self.selected[rowid].pop(0)
            else:
                pass
                

        return self.check_loop

    def proceed(self, widget):
        
        self.check_loop = False
        assignedfiles=[]
        for rowid in range(self.rows):

            try:
                account_name = self.acc_names[self.selected[rowid][0]] #save allocated account name to imported file, if user choice was set
            except:
                account_name = LANGDICT_GUI['fileacclinkwin_nochoice'][0] #set account name unknown for imported files without user choice
            
            assignedfiles.append((self.imported_files[rowid], account_name))
        
        #call function in accounts data to link account names to imported data sets
        self.accounts_data.assign_fileaccnames(assignedfiles)
        self.close()

    def close_window(self, widget, origin):
        if origin == 'btn':
            self.close()#send close signal
        else:#close window
            Gtk.main_quit()



#---------------------------------------Concat Window class--------------------------------------------

# Window is only shown if user selects concatenation

class ConcatWindow(Gtk.Window):

#_____________________________________________ subsection window design_______________________________
    def __init__(self, input_list):


        Gtk.Window.__init__(self, title=LANGDICT_GUI['concatwin_header'][0])

        self.set_border_width(15)
        self.connect("delete_event", self.close_window)
        self.set_modal(True)

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        self.proceed = False #variable needed to clear concat_list, if  selection process wasn't successful
        self.window_active = True #necessary for outer loop waiting for window reply

        self.input_list = input_list

        self.concat_list = []

        #Styling
        #vertical main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        self.add(main_box)

        #create selection grid (checkboxes)
        chk_grid = Gtk.Grid()
        chk_grid.set_column_spacing(20)
        chk_grid.set_row_spacing(15)
        chk_grid.set_row_homogeneous(False)
        main_box.pack_start(chk_grid, True, True, 5)

        #button box
        bt_box = Gtk.Box()
        main_box.pack_start(bt_box, True, True, 35)

        #buttons
        #cancel concatenation
        btn_nogo = Gtk.Button.new_with_label(LANGDICT_GUI['concatwin_btn1'][0])
        btn_nogo.connect("clicked", self.close_window, 'btn')
        bt_box.pack_start(btn_nogo, True, True, 20)

        # continue button
        btn_go = Gtk.Button.new_with_label(LANGDICT_GUI['concatwin_btn2'][0])
        btn_go.connect("clicked", self.proceed_analysis)
        bt_box.pack_start(btn_go, True, True, 20)

        #set variables for grid size depending on number of input datasets(input_list)
        self.rows = len(self.input_list)


        if self.rows == 2:
            self.cols = 1
        elif self.rows == 3:
            self.cols = 3
        else:
            self.cols = 6
        #create chk_grid

######################################################### Selection Grid Design Part #################################

        self.entrybox = []
        self.chkboxes = []


        #build checkbox grid with for loops
        #first loop through number of columns (depending on grid size given by imported data sets).
        #columns hold number of new files created (merged files)
        for colid in range(0, self.cols):

            self.chkboxes.append([])

            #empty label
            chk_grid.attach(Gtk.Label(), 0, self.rows+1, 1, 1)

            #display label for respective entrybox of new file
            label_entry = Gtk.Label()
            label_entry.set_markup('<b>'+eval(f"f'''{LANGDICT_GUI['concatwin_entryname'][0]}'''")+'</b>')#eval function transforms f-string statements to be interpreted as f-strings
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
                label_data = Gtk.Label.new(eval(f"f'''{LANGDICT_GUI['concatwin_choicename'][0]}'''"))#eval function transforms f-string statements to be interpreted as f-strings
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

    def close_window(self, widget, origin):
        if origin == 'btn':
            self.close()#send close signal
        else:#close window
            if not self.proceed:#clear list if selection process wasn't successful
                self.concat_list = []
            else:
                pass
            Gtk.main_quit()


    def check_columns(self):
        #check for user choice and deactivate entryboxes and checkboxes which are not needed (e.g. first column is selected, third column is deactivated)
        selected = []
        for colid in range(self.cols):
            selected.append([])
            for rowid in range(self.rows):
                if self.chkboxes[colid][rowid].get_active() == True:
                    selected[colid].append(rowid)

        #turn checkbox on and off depending on previous column
        #turn entrybox on depending on selection

        for colid in range(1, self.cols):

            if len(selected[colid]) > 1:
                self.entrybox[colid].set_sensitive(True)
            else:
                self.entrybox[colid].set_sensitive(False)
                self.entrybox[colid].set_text('')

            if len(selected[colid-1]) > 1:
                for rowid in range(self.rows):
                    self.chkboxes[colid][rowid].set_sensitive(True)

            else:
                #self.entrybox[colid].set_sensitive(False)
                for rowid in range(0, len(self.input_list)):
                    self.chkboxes[colid][rowid].set_active(False)
                    self.chkboxes[colid][rowid].set_sensitive(False)

            for separ in range(1, self.cols):
                if ((len(selected[colid-(1+separ)]) == 1) and colid > separ):
                    #self.entrybox[colid].set_sensitive(False)
                    for rowid in range(self.rows):
                        self.chkboxes[colid][rowid].set_active(False)
                        self.chkboxes[colid][rowid].set_sensitive(False)
        return True

    def proceed_analysis(self, widget):
        #do several checks before proceeding. Check for minimum 2 files selected, if name for selection is provided and if it already exists

        namelist = ['na']*self.cols
        checklist = []
        for colid in range(self.cols):
            if not self.entrybox[colid].get_text() == '':
                if (self.entrybox[colid].get_text() in namelist) or (self.entrybox[colid].get_text() in self.input_list):
                    namelist[colid] = 'errorname'
                else:
                    namelist[colid] = self.entrybox[colid].get_text()
            #list append checkbox values
            temp = []
            checklist.append([])
            for rowid in range(self.rows):
                if self.chkboxes[colid][rowid].get_active() == True:
                    temp.append(self.input_list[rowid])
            if len(temp) > 1:
                checklist[colid] = temp

        for colid in range(self.cols):
            if not checklist[colid] == []:

                if namelist[colid] == "na":
                    errormessage = 'errnoname'

                elif namelist[colid] == 'errorname':
                    errormessage = 'errname'

                else:
                    errormessage = 'success'
                    self.concat_list.append((namelist[colid], checklist[colid]))
            else:
                if colid == 0: # if no files where selected from first column (minimum 2)
                    errormessage = 'errselect'
                else:
                    pass

        #messages before continuation

        if errormessage == 'errselect': # no choice
            userproc.message.error(self, LANGDICT_GUI['concatwin_errselect'][0], LANGDICT_GUI['concatwin_errselect'][1])
            self.concat_list = [] #reset concat_list

        elif errormessage == 'errnoname':
            userproc.message.error(self, LANGDICT_GUI['concatwin_errnoname'][0], LANGDICT_GUI['concatwin_errnoname'][1])
            self.concat_list = [] #reset concat_list

        elif errormessage == 'errname':
            userproc.message.error(self, LANGDICT_GUI['concatwin_errname'][0], LANGDICT_GUI['concatwin_errname'][1])
            self.concat_list = [] #reset concat_list

        else:
            if not self.concat_list == []:
                userproc.message.info(self, LANGDICT_GUI['concatwin_succ'][0], LANGDICT_GUI['concatwin_succ'][1])
                self.proceed = True
                self.close()




#---------------------------------------Progressbar Window class--------------------------------------------

# show progressbar while doing the main data processing and plotting

class ProgressBarWindow(Gtk.Window):

    def __init__(self, master, queue):

        Gtk.Window.__init__(self, title=LANGDICT_GUI['prgrsswin_header'][0])
        self.queue = queue
        self.master = master
        self.langdict_main = LANGDICT_USED['Main_File_vars']

        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", self.close_window)        
        #self.set_transient_for(master)
        self.set_resizable(False)
        self.set_deletable(False)
        #self.set_keep_below(True)
        self.set_icon_from_file(PATH_ICON) #needed to be defined separately as progressbar is a spawned process in windows

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_margin_bottom(10)
        self.add(main_box)

        image = Gtk.Image()
        image.set_from_file(PATH_PROGRESS_PIC)

        # add the image to the window
        main_box.pack_start(image, True, True, 0)

        #create progressbar
        self.progressbar = Gtk.ProgressBar()
        self.activity_mode = False#nececessary for controlling progressbar
        main_box.pack_start(self.progressbar, True, True, 0)

        #start timer-loop for contanstly doing progress pulsation and queuecheck
        #timeout_queue = GLib.timeout_add(50, self.queue_check, None)
        GLib.idle_add(self.queue_check)
        timeout_pulsating = GLib.timeout_add(100, self.main_timeout, None)
        self.show_all()

#_____________________________________________ subsection window/button functions_______________________________

    def queue_check(self):
        '''Function for checking information exchange between the two processes'''

        try:
            msg, data = self.queue.get_nowait()

        except Exception:
            return True

        if 'process' in msg:
            self.userinformation(msg, data)
            self.queue.put(('success', ""))
        
        elif 'rawimport_end' in msg:

            self.check_import(data)

        return True

    def main_timeout(self, user_data):
    #Update value on the progress bar
        if self.activity_mode:
        	#make progressbar bumping from one side to another
            self.progressbar.pulse()

        return True

    def check_import(self, data):

        #display import result and link files to account names if necessary
        self.master.mfunc.accounts_data = data #update accounts_data class
        self.activity_mode = False #stop pulsastion for message display
        imported_files = self.master.mfunc.dataimport_check() #check errorcodes in imported files and print user info
        #if at least one dataframe was imported correctly start data preparation
        if imported_files != []:
            
            if userproc.ACCOUNT_NAMES != []: #if account names are used link files to account name
                self.hide()              
                filelink = FileAccLinkWindow(self, imported_files)
                Gtk.main()
                self.show_all()
            else:
                pass
            #start data preparation 
            self.master.mfunc.data_preparation()
        else: #else show main window again
            self.hide()
            self.master.show_all()


    def userinformation(self, msg, data):
    	# this function is only needed for the queue interaction with the main processing running in a separate process
        title1, title2 = self.langdict_main[data][0], self.langdict_main[data][1]
        if msg == 'process_error':
            self.activity_mode = False
            userproc.message.error(self, title1, title2)            
            self.close_window('error','user_info')
        elif msg == 'process_start':
            self.activity_mode = False
            userproc.message.info(self, title1, title2)
            self.set_title(LANGDICT_GUI['prgrsswin_visualinfo'][0])
            self.activity_mode = True
        elif msg == 'process_end':
            self.activity_mode = False
            title2 = eval(f"f'''{title2}'''")
            userproc.message.info(self, title1, title2)
            self.close_window('end','user_info')

    def close_window(self, widget, origin):#used by menu entry quit and close event

        self.master.close_window('plot_end', 'progres') #call close function in main window

