'''This script helps to identify the acc type which is used in the data processing script. For further development
purposes a little test function is implemented to directly test acc type recognition and print infos provided by separately maintained excel'''



import os
import sys
import pandas as pd

if not hasattr(sys, 'frozen'): #get local folder path for subfolder 'suppldata' if window is not frozen
    ACCINFO_FILE = os.path.join(os.getcwd(), 'suppldata', 'acc_infofile.txt')
else:
    ACCINFO_FILE = os.path.join(sys.prefix, 'suppldata', 'acc_infofile.txt')

#necessary function to define how date can be read-in correctly
def dateadjuster(val, timevar):
    '''format transformation for parsing dates from csv'''
    #new format because of deprecitation warning; error values are handeld as 'NaT' automatically
    if timevar == 'capy':
        return pd.to_datetime(val, format='%d.%m.%Y', errors='coerce')
    else:
        return pd.to_datetime(val, format='%d.%m.%y', errors='coerce')

DATEPARSER_CAPY = lambda x: dateadjuster(x, 'capy')
DATEPARSER_LOWY = lambda x: dateadjuster(x, 'lowy')


# #Import txt-file with accountinfo
# ACCINFOS = open(ACCINFO_FILE, 'r')
# ACCINFO_LINES = ACCINFOS.readlines()
# ACCINFO_SCRIPT = ''
# #read ACCINFO_LINES and concat them to str
# for line in ACCINFO_LINES:
#     ACCINFO_SCRIPT += line
# #execute string and close file

# exec(ACCINFO_SCRIPT)
# ACCINFOS.close()


##create ACCOUNT INFOS

INFO_COMDI_GIRO = (['Buchungstag', 'Wertstellung (Valuta)', 'Vorgang', 'Buchungstext', 'Umsatz in EUR'], ('no', []), ('no', [], []), 'giro', 'complete')

INFO_COMDI_CREDIT = (['Buchungstag', 'Umsatztag', 'Vorgang', 'Referenz', 'Buchungstext', 'Umsatz in EUR'], ('yes', [3, 4]), ('yes', 3, [0, 1, 2, 3, 4]), 'credit', 'normal')

INFO_DKB_GIRO = (['Buchungstag', 'Wertstellung', 'Buchungstext', 'Auftraggeber / Begünstigter', 'Verwendungszweck', 'Kontonummer', 'BLZ', 'Betrag (EUR)', 'Gläubiger-ID', 'Mandatsreferenz', 'Kundenreferenz', 'Unnamed: 11'], ('yes', [3, 4, 5]), ('yes', [3, 4, 5, 6, 8, 9, 10, 11], [0, 1, 2, 4, 3]), 'giro', 'complete')

INFO_DKB_CREDIT = (['Umsatz abgerechnet und nicht im Saldo enthalten', 'Wertstellung', 'Belegdatum', 'Beschreibung', 'Betrag (EUR)', 'Ursprünglicher Betrag'], ('no', []), ('yes', [0, 5], [0, 1, 2, 3]), 'credit', 'normal')

INFO_STANDFORM1_GIRO = (['Buchungstag', 'Valuta', 'Auftraggeber/Zahlungsempfänger', 'Empfänger/Zahlungspflichtiger', 'Konto-Nr.', 'IBAN', 'BLZ', 'BIC', 'Vorgang/Verwendungszweck', 'Kundenreferenz', 'Währung', 'Umsatz', 'Soll/Haben', 'Vorgang'], ('yes', [3, 8, 9]), ('yes', [2, 3, 4, 5, 6, 7, 8, 9, 10, 12], [0, 1, 3, 4, 2]), 'giro', 'complete')

INFO_APOBANK_GIRO = (['Kontonummer', 'Buchungstag', 'Wertstellung', 'Auftraggeber/Empfänger', 'Textschlüssel', 'Buchungstext', 'VWZ1', 'VWZ2', 'VWZ3', 'VWZ4', 'VWZ5', 'VWZ6', 'VWZ7', 'VWZ8', 'VWZ9', 'VWZ10', 'VWZ11', 'VWZ12', 'VWZ13', 'VWZ14', 'Betrag', 'Kontostand', 'Währung'], ('yes', [3, 4, 5, 6, 7, 8, 9, 10, 11]), ('yes', [0, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22], [0, 1, 2, 4, 3]), 'giro', 'complete')

INFO_SPARKA_GIRO = (['Auftragskonto', 'Buchungstag', 'Valutadatum', 'Buchungstext', 'Verwendungszweck', 'Begünstigter/Zahlungspflichtiger', 'Kontonummer', 'BLZ', 'Betrag', 'Währung', 'Info'], ('yes', [4, 5, 6]), ('yes', [0, 4, 5, 6, 7, 9, 10], [0, 1, 2, 4, 3]), 'giro', 'complete')

INFO_CONSORS_GIRO = (['Buchung', 'Valuta', 'Sender / Empfänger', 'IBAN / Konto-Nr.', 'BIC / BLZ', 'Buchungstext', 'Verwendungszweck', 'Kategorie', 'Stichwörter', 'Umsatz geteilt', 'Betrag in EUR'], ('yes', [2, 6, 7]), ('yes', [2, 3, 4, 6, 7, 8, 9], [0, 1, 2, 4, 3]), 'giro', 'complete')

INFO_DEUTSCHE_GIRO = (['Buchungstag', 'Wert', 'Umsatzart', 'Begünstigter / Auftraggeber', 'Verwendungszweck', 'IBAN', 'BIC', 'Kundenreferenz', 'Mandatsreferenz ', 'Gläubiger ID', 'Fremde Gebühren', 'Betrag', 'Abweichender Empfänger', 'Anzahl der Aufträge', 'Anzahl der Schecks', 'Soll', 'Haben', 'Währung', 'Umsatz in EUR'], ('yes', [3, 4, 5, 7]), ('yes', [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [0, 1, 2, 4, 3]), 'giro', 'complete')

INFO_COMMERZ_GIRO = (['Buchungstag', 'Wertstellung', 'Umsatzart', 'Buchungstext', 'Betrag', 'Währung', 'Auftraggeberkonto', 'Bankleitzahl Auftraggeberkonto','IBAN Auftraggeberkonto', 'Kategorie'], ('yes', [3, 9]), ('yes', [3, 5, 6, 7, 8, 9], [0, 1, 2, 4, 3]), 'giro', 'complete')

INFO_HYPOBANK_GIRO = (['Kontonummer', 'Buchungsdatum', 'Valuta', 'Empfänger 1', 'Empfänger 2', 'Verwendungszweck', 'Betrag', 'Währung', 'Vorgang'], ('yes', [3, 4, 5]), ('yes', [0, 3, 4, 5, 7], [0, 1, 3, 4, 2]), 'giro', 'complete')




def get_acctype_fullname(imported_acctype, filepath):
    #function returns full bank account name
    bank_fullnames_dict = {'apobank_giro': 'Apobank Girokonto',
                           'comdi_giro': 'Comdirect Girokonto',
                           'comdi_credit': 'Comdirect Kreditkarte',
                           'commerz_giro': 'Commerzbank Girokonto',
                           'consors_giro': 'Consorsbank Girokonto',
                           'deutsche_giro': 'Deutsche Bank Girokonto',
                           'dkb_giro': 'DKB Girokonto',
                           'dkb_credit': 'DKB Kreditkarte',
                           'Genossenschaft_giro': 'Genossenschaftsbank Girokonto',
                           'hypobank_giro': 'Hypovereinsbank Girokonto',
                           'MLP Banking_giro': 'MLP Banking Girokonto',
                           'sparka_giro': 'Sparkasse Girokonto',
                           'Triodos Bank_giro': 'Triodos Girokonto',
                           'Volksbank_giro': 'Volksbank Girokonto',
                           'unknown_account': 'Unknown bank account'}

    #get account name for standarbank_format
    if imported_acctype == 'standform1_giro':
        #first entry in standardbank_format csv file states bank name, but is skipped for raw data import, so has to be separately imported
        accountidentifier = pd.read_csv(filepath, sep=';', encoding='iso8859_15', nrows=0).columns[0]
        list_banksearchwords = ['Genossenschaft', 'MLP Banking', 'Triodos Bank', 'Volksbank']
        for entry in list_banksearchwords:
            if entry in accountidentifier:
                imported_acctype = entry+'_giro'
                break
            else:
                imported_acctype = 'unknown_account' #return unknown Account if format is recognized, but can't be linked to an account name
    else:
        pass #nothing to do for all other account type

    full_bankname = bank_fullnames_dict[imported_acctype]

    return full_bankname


def acc_type_tester(filepath):
    #test inputted file for multiple acctypes. Return Account type for further data processing
    #for loop tries accountt type. If error occurs account type is skipped. If account type matches account info data from dictionary is returned

    raw_data_none = []
    value = 'unsupported acctype'
    accinfo_none = 'No account info'

    def comdirect(filepath): #current account
        raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=list(range(0, 4)), index_col=5, thousands='.', decimal=',', skipfooter=2, engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_CAPY).reset_index(drop=True)
        
        if raw_data.columns.tolist() == INFO_COMDI_GIRO[0]: #raw data header matches final header
            ##fix current comdirect value csv export-problem
            if raw_data['Umsatz in EUR'].value_counts().empty:
                raw_data['Umsatz in EUR'] = raw_data['Buchungstext'].apply(lambda x: float(x.split('"')[1].replace(".", "").replace(",", ".")))
                raw_data['Buchungstext'] = raw_data['Buchungstext'].apply(lambda x: x.split('"')[0])
            else:
                pass

            return ('comdi_giro', raw_data)

        elif raw_data.columns.tolist() == ['Buchungstag', 'Umsatztag', 'Vorgang', 'Referenz', 'Buchungstext', 'Unnamed: 6']: #credit card
            raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=list(range(0, 4)), index_col=6, thousands='.', decimal=',', skipfooter=2, engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_CAPY).reset_index(drop=True)
            raw_data['Referenz'] = raw_data[raw_data.columns[3]].apply(lambda item: "{}{}".format('Ref. ', item)) #alter reference column

            return ('comdi_credit', raw_data)

        else:
            return ('other_acctype', raw_data)


    def deutschekreditbank(filepath):
        raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=list(range(0, 6)), thousands='.', decimal=',', engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_CAPY)
        #current account
        if raw_data.columns.tolist() == INFO_DKB_GIRO[0]: #raw data header matches final header
            return ('dkb_giro', raw_data)
        #credit card
        elif raw_data.columns.tolist() == ['Umsatz abgerechnet und nicht im Saldo enthalten', 'Wertstellung', 'Belegdatum', 'Beschreibung', 'Betrag (EUR)', 'Ursprünglicher Betrag', 'Unnamed: 6']:
            raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=list(range(0, 6)), index_col=6, thousands='.', decimal=',', engine='python', parse_dates=[1, 2], date_parser=DATEPARSER_CAPY).reset_index(drop=True)
            return ('dkb_credit', raw_data)

        else:
            return ('other_acctype', raw_data)


    def standardbank_format1(filepath): #currently only current account tested
        #most common date foramt is 'DD.MM.YYYY', so DATEPARSER_CAPY is default
        raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=list(range(0, 12)), skipfooter=3, thousands='.', decimal=',', engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_CAPY).reset_index(drop=True)

        #check if csv has the standardbank column labels
        if raw_data.columns.tolist() == ['Buchungstag', 'Valuta', 'Auftraggeber/Zahlungsempfänger', 'Empfänger/Zahlungspflichtiger', 'Konto-Nr.', 'IBAN', 'BLZ', 'BIC', 'Vorgang/Verwendungszweck', 'Kundenreferenz', 'Währung', 'Umsatz', ' ']:

            #decide if lowy dateparser should be used (check if all time1 (column 0) entries are Null)
            if all(raw_data[raw_data.columns[0]].isna()):
                raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=list(range(0, 12)), skipfooter=3, thousands='.', decimal=',', engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_LOWY).reset_index(drop=True)
                acctype_value = 'standform1_lowy'

            else:
                acctype_value = 'standform1_capy'

            raw_data['act'] = raw_data['Vorgang/Verwendungszweck'].apply(lambda x: x.split('\n')[0]) # get act label from transaction text
            #rename raw_data for further processing
            raw_data['Umsatz'] = raw_data['Umsatz'].mask(raw_data[' '] == 'S', -raw_data['Umsatz']) #adjust value (debit or credit) coded with "S" or "H" in empty column

            return (acctype_value, raw_data)

        else:
            return ('other_acctype', raw_data)

    def apobank(filepath):#currently only 'giro' tested
        
        raw_data = pd.read_csv(filepath, sep=',', skiprows=[], thousands='.', decimal=',', engine='python', parse_dates=[1, 2], date_parser=DATEPARSER_CAPY).reset_index(drop=True)
        
        if len(raw_data.columns) == 23:
            return ('apobank_giro', raw_data)
        else:
            return ('other_acctype', raw_data)

    def sparkasse(filepath):#currently only 'giro' tested
        
        raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=[], thousands='.', decimal=',', engine='python', parse_dates=[1, 2], date_parser=DATEPARSER_CAPY).reset_index(drop=True)

        #check if csv has the sparkasse column labels
        if raw_data.columns.tolist() == ['Auftragskonto', 'Buchungstag', 'Valutadatum', 'Buchungstext', 'Verwendungszweck', 'Beguenstigter/Zahlungspflichtiger', 'Kontonummer', 'BLZ', 'Betrag', 'Waehrung', 'Info']:

            #decide if lowy dateparser should be used (check if all time1 (column 0) entries are Null)
            if all(raw_data[raw_data.columns[1]].isna()):
                raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=[], thousands='.', decimal=',', engine='python', parse_dates=[1, 2], date_parser=DATEPARSER_LOWY).reset_index(drop=True)
                acctype_value = 'sparka_lowy'

            else:
                acctype_value = 'sparka_capy'

            #Rename Columns for further processing
            raw_data.columns = ['Auftragskonto', 'Buchungstag', 'Valutadatum', 'Buchungstext', 'Verwendungszweck', 'Begünstigter/Zahlungspflichtiger', 'Kontonummer', 'BLZ', 'Betrag', 'Währung', 'Info']

        else:
            acctype_value = 'other_acctype'

        return (acctype_value, raw_data)

    def consorsbank(filepath):

        raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=[], skipfooter=3, thousands='.', decimal=',', engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_CAPY)

        if raw_data.columns.tolist() == INFO_CONSORS_GIRO[0]:

            return ('consors_giro', raw_data)

        else:
            return ('other_acctype', raw_data)

    def deutschebank(filepath):#currently only 'giro' tested
        raw_data = pd.read_csv(filepath, sep=';', encoding='iso8859_15', skiprows=list(range(0, 4)), skipfooter=1, thousands='.', decimal=',', engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_CAPY).reset_index(drop=True)
        
        if raw_data.columns.tolist() == INFO_DEUTSCHE_GIRO[0][:-1]:

            raw_data['val'] = raw_data['Soll'].mask(raw_data['Soll'].isna(), raw_data['Haben'])#works as acc filter as well
            return ('deutsche_giro', raw_data)
        
        else:
            return ('other_acctype', raw_data)

    def commerzbank(filepath):#currently only 'giro' tested
        raw_data = pd.read_csv(filepath,  sep=';', encoding='utf-8-sig', skiprows=[], thousands='.', decimal=',', engine='python', parse_dates=[0, 1], date_parser=DATEPARSER_LOWY).reset_index(drop=True)
        
        if raw_data.columns.tolist() == INFO_COMMERZ_GIRO[0]:

            return ('commerz_giro', raw_data)

        else:
            return ('other_acctype', raw_data)

    def hypoverseinsbank(filepath):
        raw_data = pd.read_csv(filepath, sep=';', encoding='utf-16-le', skiprows=[], thousands='.', decimal=',', engine='python', parse_dates=[1, 2], date_parser=DATEPARSER_CAPY).reset_index(drop=True)

        if raw_data.columns.tolist() == ['Kontonummer', 'Buchungsdatum', 'Valuta', 'Empfaenger 1', 'Empfaenger 2', 'Verwendungszweck', 'Betrag', 'Waehrung']:
            #adjust column labels
            raw_data.columns = ['Kontonummer', 'Buchungsdatum', 'Valuta', 'Empfänger 1', 'Empfänger 2', 'Verwendungszweck', 'Betrag', 'Währung']
            raw_data['act'] = raw_data['Verwendungszweck'].apply(lambda x: x.split('/')[0]) # get act entry for every row from transaction text

            return ('hypobank_giro', raw_data)
        else:
            return ('other_acctype', raw_data)


    for accountfunc in (comdirect, deutschekreditbank, standardbank_format1, apobank, sparkasse, consorsbank, deutschebank, commerzbank, hypoverseinsbank):

        #skipperint = 0 ## Skipperint was used to establish read in, even if transactions in the first 3 rows haven't been credited yet (date columuns have unusual string values)

        try:
            value, raw_data = accountfunc(filepath)
        except:
            pass#nothing to do jump to next account type

        if value in ('other_acctype','unsupported acctype'):

            raw_data = raw_data_none
            continue
        else:
            break

    return (value, raw_data)


##function is only established to be able to control for errors with pandas data import values (i.e. if acc_type is recognized correctly)
def account_info_identifier(filepath):
    '''iter through accounts in text file and return accountype if found'''

    value, raw_data = acc_type_tester(filepath)
    
    #this extra loop was chosen deliberatly, so that acctype_recognition_tester return subtype of sparkasse and mlp/triodos
    if 'sparka' in value:
        imported_acctype = 'sparka_giro'

    elif 'standform1' in value:
        imported_acctype = 'standform1_giro'

    elif 'acctype' in value: # set account name to unknown if no account was recognised (for development)
        imported_acctype='unknown_account'

    else:
        imported_acctype = value


    # get account full name
    acctype_fullname = get_acctype_fullname(imported_acctype, filepath)

    accountinfo = globals()["INFO_"+imported_acctype.upper()] #get global variable of that specific account

    return (acctype_fullname, raw_data, accountinfo)


#This test function is only activated if script is run directly
def acctype_recognition_tester(folder_raw, filename):
    '''function needed for development. Data retrieved from local excel file to be read-in'''

    acctest_input = pd.read_excel(folder_raw+filename+'.xlsx', sheet_name='Testfiles')
    acctest_output = acctest_input.copy()
    test_acctypes = []
    test_acctypenames = []
    for entry in range(0, len(acctest_output)):
        test_filepath = folder_raw+acctest_input.iloc[entry][1]+'.csv'
        test_acctype = acc_type_tester(test_filepath)[0] #get acctype
        if 'sparka' in test_acctype:
            imported_acctype = 'sparka_giro'
        elif 'standform1' in test_acctype:
            imported_acctype = 'standform1_giro'

        elif 'acctype' in test_acctype: # set account name to unknown if no account was recognised (for development)
            imported_acctype='unknown_account'

        else:
            imported_acctype = test_acctype

        test_acctypename = get_acctype_fullname(imported_acctype, test_filepath) # get acctypename
         #append results
        # print results for control
        print(test_acctypename+':')
        print(acc_type_tester(test_filepath)[1]) #print raw data

        test_acctypes.append(test_acctype)
        test_acctypenames.append(test_acctypename)
    acctest_output['Testergebnis_Kontotyp'] = test_acctypes
    acctest_output['Testergebnis_Kontoname'] = test_acctypenames
    acctest_output.to_excel(folder_raw+filename+'_Results.xlsx', index=False, sheet_name='Testergebnisse')


##Development function for future adjustments to the account info dictionary
def accinfo_dict_writer(folder_raw, filename):
    '''function needed for development. Prints necessary code to be implemented in account info text file'''

    #read in account info dictionary excel
    acc_info_read = pd.read_excel(folder_raw+filename+'.xlsx', sheet_name='Data')

    #Print out entries in Excel in the correct way for integration in code:
    print('Liste der Einträge im Kontoinfo Dictionary:\n\n')
    for entry in range(0, len(acc_info_read)):
        print('Kontotyp:'+acc_info_read.iloc[entry][0]+'\n')
        print(acc_info_read.iloc[entry][0]+'_info = ('+acc_info_read.iloc[entry][1]+', '+acc_info_read.iloc[entry][2]+', '+acc_info_read.iloc[entry][3]+', '+acc_info_read.iloc[entry][4]+', '+acc_info_read.iloc[entry][5]+')\n\n')


#this snippet starts the testing code, only relevant for development
if __name__ == '__main__':
    print('Willkommen zum Testscript. Die Testfunktion wird gestartet!')
    folder_raw_test = input('Bitte geben Sie den genauen Ordnerpfad an, in dem sich die Exceldatei mit den Test und Entwicklungsinformationen (Kontotyp und Dateinamen). Die zu testenden csv-Dateien müssen in demselben Ordner liegen.\n')+'/'
    test_file = input('\nBitte geben Sie den Namen der Exceldatei ohne Dateiendung ein.\n')
    acctype_recognition_tester(folder_raw_test, test_file) #start account recognition
    print('Der Erkennungstest ist abgeschlossen. Die Ergebnisse sind in einer Excel ausgegeben worden.')

    #start accinfo_writer if selected
    printaccountinfo = input('\nSollen die Kontoinformationseinträge zum einfacheren Coden geplottet werden (ja oder nein)?\n')[0].lower()
    if printaccountinfo == 'j':
        accinfo_dict_writer(folder_raw_test, test_file)

        print('Vielen Dank!')
    else:
        print('Das Programm kann geschlossen werden.')
