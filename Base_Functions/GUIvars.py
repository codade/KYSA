'''File is only used to store variables necessary for building and showing GUI'''


#--------------------css adoptions used in Main GUI--------------------
## simple adaptions to standard style, mainly progressbar (black bar) and button text size

KYSA_css='''progress {min-height: 24px;background-color:#000;border:#000;}
trough {min-height: 24px;}
label {font-size:19px;}
textview{font-size:22px;}
menu {color:#fff;background-color:#4b4848;}
menuitem:hover {color:#fff;background-color:rgba(255, 255, 255, .1);}
#separator_label {font-size:20px;font-weight: bold;}
#bws_btn {font-size:24px; font-weight:bold;}
#run_btn {font-size:25px; font-weight:bold;}
'''


#-----------------------------------------XML Menu Info-----------------------

#XML data for building main menu
KYSA_XMLMenu = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="KYSA-Menu">
    
    <submenu>
        <attribute name='label'>Informationen</attribute>
        <item>
        <attribute name='label'>Changelog</attribute>
        <attribute name='action'>win.changelog</attribute>
        </item>
        <item>
        <attribute name='label'>Dokumentation</attribute>
        <attribute name='action'>win.readme</attribute>
        </item>
        <item>
        <attribute name='label'>Lizenzhinweis</attribute>
        <attribute name='action'>win.license</attribute>
        </item>
        <item>
        <attribute name='label'>Über KYSA</attribute>
        <attribute name='action'>win.about</attribute>
        </item>
    </submenu>
    <submenu>
        <attribute name='label'>Einstellungen</attribute>
        <item>
        <attribute name='label'>Ordner mit\nZuordnungstabelle</attribute>
        <attribute name='action'>win.classtbl</attribute>
        </item>
        <item>
        <attribute name='label'>Ordner für\nErgebnisse</attribute>
        <attribute name='action'>win.resdir</attribute>
        </item>
    </submenu>
    <section>
        <item>
            <attribute name="label">Unterstützen</attribute>
            <attribute name="action">win.donate</attribute>
        </item>
    </section>
    <section>
        <item>
            <attribute name="label">Beenden</attribute>
            <attribute name="action">win.quit</attribute>
        </item>
    </section>
  </menu>
</interface>
"""

#_-----------------------------Changelog Info----------------------------------


versions=['2.04','2.03','2.02','2.01','1.03','1.02','1.01']
changes={'2.04':['Popup notices','Revision of account identifier','Bugfix in splitted plots'],
             '2.03':['Completly refurbished GUI','Minor bugfixes','Storable directories for assignment table and results','Adaptions to manual','Integration of license file'],
             '2.02':['Integration of budget book evaluation','Improved plotting (sliced plots) for huge dataframes','New data processing structure','Introduction of prefs file','No double entries when concatting'],
             '2.01':['Introduction of error codes','Integration of progressbar','Completely revised process structure','Faster program startup on windows'],
             '1.03':['Integration of changelog-menu entry','Establish workaround for current comdirect csv-export problem','Rescripting plot generation for account types','Various account import bugfixes'],
             '1.02':['Integration of Readme html-file and copycode','New icon creation','Anchor icon in all running windows','Fix plotting of "rent"&"income"-categories','Change plot output format into *.png','Change excel output engine'],
             '1.01':['Integration of "Über KYSA"-menu entry','Anchor icon in main window and make it work in Windows.exe','Change import process of assignment table']}

chglog_list=[]

#for loop for changelog generation. Prints version number followed by 'changes' for every version
for vernum in versions:
    versiontext=f"\nVersion {vernum}:"
    changetext=('• '+'\n• '.join([changes[vernum][item] for item in range(len(changes[vernum]))]))
    chglog_list.append((versiontext,changetext))
