'''This script helps to identify the acc type which is used in the data processing script. For further development 
purposes a little test function is implemented to directly test acc type recognition for future account implementations'''


import datetime
import locale
import pandas as pd
import platform
import os
import re


if platform.system()=='Windows':
    locale.setlocale(locale.LC_ALL, '')

else:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')


#necessary function to enable read-in even if singles dates are null values
def dateadjuster(val,timevar):
    try:
        if timevar=='capy':
            return datetime.datetime.strptime(val, "%d.%m.%Y")
        else: 
            return datetime.datetime.strptime(val, "%d.%m.%y")
    except:
        return pd.NaT


dateparser_capy = lambda x: dateadjuster(x,'capy')
dateparser_lowy = lambda x: dateadjuster(x,'lowy')


#function for creating account dictionary
def make_accinfo_dict():

    comd_giro_info=(["Buchungstag","Wertstellung (Valuta)","Vorgang","Buchungstext","Umsatz in EUR"],('no',[]),('no',[],[]),'giro',('yes','Bargeld','Bargeld\nComdirect'),['a','o'])

    comd_credit_info=(["Buchungstag","Wertstellung (Valuta)","Vorgang","Referenz","Buchungstext","Umsatz in EUR"],('yes',[3,4]),('yes',3,[0,1,2,3,4]),'credit',('no',"",""),['c','m','v'])

    dkb_giro_info=(['Buchungstag', 'Wertstellung', 'Buchungstext','Auftraggeber/Begünstigter', 'Verwendungszweck', 'Kontonummer', 'BLZ', 'Betrag (EUR)','Gläubiger-ID','Mandatsreferenz','Kundenreferenz'],('yes',[3,4,5]),('yes',[3,4,5,6,8,9,10],[0,1,2,4,3]),'giro',('yes','Kosten Lebens-\nhaltung','Einzahlungen'),['a','o'])

    dkb_credit_info=(["Umsatz abgerechnet und nicht im Saldo enthalten","Wertstellung","Belegdatum","Beschreibung","Betrag (EUR)","Ursprünglicher Betrag"],('no',[]),('yes',[0,5],[0,1,2,3]),'credit',('no',"",""),['c','m','v'])

    mlp_triodos_info=(["Buchungstag","Valuta","Auftraggeber/Zahlungsempfänger","Empfänger/Zahlungspflichtiger","Konto-Nr.","IBAN","BLZ","BIC","Vorgang/Verwendungszweck","Kundenreferenz","Währung","Umsatz","Vorgang"],('yes',[3,8,9]),('yes',[2,3,4,5,6,7,8,9,10],[0,1,3,4,2]),'giro',('no',"",""),['a','o'])

    apobank_info=(["Kontonummer","Buchungstag","Wertstellung","Auftraggeber/Empfänger","Textschlüssel","Buchungstext","VWZ1","VWZ2","VWZ3","VWZ4","VWZ5","VWZ6","VWZ7","VWZ8","VWZ9","VWZ10","VWZ11","VWZ12","VWZ13","VWZ14","Betrag","Kontostand","Währung"],('yes',[3,4,5,6,7,8,9,10,11]),('yes',[0,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22],[0,1,2,4,3]),'giro',('no',"",""),['a','o'])

    sparka_giro_info=(["Auftragskonto","Buchungstag","Valutadatum","Buchungstext","Verwendungszweck","Begünstigter/Zahlungspflichtiger","Kontonummer","BLZ","Betrag","Währung","Info"],('yes',[4,5,6]),('yes',[0,4,5,6,7,9,10],[0,1,2,4,3]),'giro',('no',"",""),['a','o'])

    deutschebank_info= (['Buchungstag', 'Wert', 'Umsatzart', 'Begünstigter / Auftraggeber', 'Verwendungszweck', 'IBAN', 'BIC', 'Kundenreferenz', 'Mandatsreferenz ', 'Gläubiger ID', 'Fremde Gebühren', 'Betrag', 'Abweichender Empfänger', 'Anzahl der Aufträge', 'Anzahl der Schecks', 'Soll', 'Haben', 'Währung', 'Umsatz in EUR'],('yes', [3,4,5,7]),('yes', [ 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [0, 1, 2, 4, 3]),'giro',('no', '', ''),['a', 'o'])

    commerzbank_info = (["Buchungstag", "Wertstellung", "Umsatzart", "Buchungstext", "Betrag","Währung", "Auftraggeberkonto", "Bankleitzahl Auftraggeberkonto","IBAN Auftraggeberkonto", "Kategorie"],('no', []),('yes', [ 5, 6, 7, 8, 9], [0, 1, 2, 3,4]),'giro',('no', '', ''),['a', 'o'])

    accinfo_dictionary={'comd_giro':comd_giro_info,'comd_credit':comd_credit_info,'dkb_giro':dkb_giro_info,'dkb_credit':dkb_credit_info,'mlp_triodos':mlp_triodos_info,'apobank':apobank_info,'sparka_giro':sparka_giro_info, 'deutschebank':deutschebank_info, 'commerzbank':commerzbank_info}
    return accinfo_dictionary



def acc_type_tester(filepath):
    #test inputted file for multiple acctypes. Return Account type for further data processing

    
    raw_data=[]
    value='unsupported acctype'

    def comdirect(filepath,skipperint):
        raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=[0,1,2,3]+list(range(5,5+skipperint)),index_col=5,thousands='.',decimal=',',skipfooter=2,engine='python',parse_dates=[0,1],date_parser=dateparser_capy).reset_index(drop=True)
        if len(raw_data.columns)==5:
            return ('comd_giro',raw_data)
        elif len(raw_data.columns)==6:
            raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=[0,1,2,3]+list(range(5,5+skipperint)),index_col=6,thousands='.',decimal=',',skipfooter=2,engine='python',parse_dates=[0,1],date_parser=dateparser_capy).reset_index(drop=True)
            raw_data["Referenz"]=raw_data[raw_data.columns[3]].apply(lambda item: "{}{}".format('Ref. ', item))
            return ('comd_credit',raw_data)
        else:
            return ("other_acctype",raw_data)


    def dkb_giro(filepath,skipperint):
        raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=[0,1,2,3,4,5]+list(range(7,7+skipperint)),index_col=11,thousands='.',decimal=',',engine='python',parse_dates=[0,1],date_parser=dateparser_capy).reset_index(drop=True)
        if raw_data.columns.tolist()==['Buchungstag','Wertstellung','Buchungstext','Auftraggeber / Begünstigter','Verwendungszweck','Kontonummer','BLZ','Betrag (EUR)','Gläubiger-ID','Mandatsreferenz','Kundenreferenz']:
            return ('dkb_giro',raw_data)
        else:
            return ("other_acctype",raw_data)

    def dkb_credit(filepath,skipperint):
        raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=[0,1,2,3,4,5]+list(range(7,7+skipperint)),index_col=6,thousands='.',decimal=',',engine='python',parse_dates=[1,2],date_parser=dateparser_capy).reset_index(drop=True)
        if len(raw_data.columns)==6:
            return ('dkb_credit',raw_data)
        else:
            return ("other_acctype",raw_data)


    def mlp_triodos(filepath,skipperint):
        raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=list(range(0,12))+list(range(13,13+skipperint)),skipfooter=3,index_col=12,thousands='.',decimal=',',engine='python',parse_dates=[0,1],date_parser=dateparser_lowy).reset_index(drop=True)
        raw_data['act'] = raw_data["Vorgang/Verwendungszweck"].apply(lambda x: x.split('\n')[0])
        return ('mlp_triodos',raw_data)

    def apobank(filepath,skipperint):
        raw_data=pd.read_csv(filepath,sep=",",skiprows=list(range(1,1+skipperint)),thousands='.',decimal=',',engine='python',parse_dates=[1,2],date_parser=dateparser_capy).reset_index(drop=True)
        if len(raw_data.columns)==23:
            return ('apobank',raw_data)
        else:
            return ("other_acctype",raw_data)

    def sparkasse(filepath,skipperint):
        raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=list(range(1,1+skipperint)),thousands='.',decimal=',',engine='python',parse_dates=[1,2],date_parser=dateparser_lowy).reset_index(drop=True)
        if raw_data.columns.tolist()==['Auftragskonto','Buchungstag','Valutadatum','Buchungstext','Verwendungszweck','Beguenstigter/Zahlungspflichtiger','Kontonummer','BLZ','Betrag','Waehrung','Info']:
            
            #check if capy dateparser is should be used
            if pd.isna(raw_data['Valutadatum'][2]):
                raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=list(range(1,1+skipperint)),thousands='.',decimal=',',engine='python',parse_dates=[1,2],date_parser=dateparser_capy).reset_index(drop=True)
                acctype_value='sparka_capy'

            else:
                acctype_value='sparka_lowy'
            
            #Rename Columns for further procressing
            raw_data.columns=["Auftragskonto","Buchungstag","Valutadatum","Buchungstext","Verwendungszweck","Begünstigter/Zahlungspflichtiger","Kontonummer","BLZ","Betrag","Währung","Info"]
             
        else:
            acctype_value="other_acctype"

        return (acctype_value,raw_data)

    def deutschebank(filepath,skipperint):
        raw_data=pd.read_csv(filepath,sep=";",encoding="iso8859_15",skiprows=[0,1,2,3]+list(range(5,5+skipperint)),skipfooter=1,thousands='.',decimal=',',engine='python',parse_dates=[0,1],date_parser=dateparser_capy).reset_index(drop=True)
        raw_data['val']=raw_data['Soll'].mask(raw_data['Soll'].isna(),raw_data['Haben'])
        return ('deutschebank',raw_data)

    def commerzbank(filepath,skipperint):
        raw_data=pd.read_csv(filepath,encoding="iso8859_15",skiprows=list(range(1,1+skipperint)),sep=";",thousands='.',decimal=',',engine='python',parse_dates=[0,1],date_parser=dateparser_lowy).reset_index(drop=True)
        raw_data.columns=["Buchungstag", "Wertstellung", "Umsatzart", "Buchungstext", "Betrag","Währung", "Auftraggeberkonto", "Bankleitzahl Auftraggeberkonto","IBAN Auftraggeberkonto", "Kategorie"]
        return ('commerzbank',raw_data)
    
  
  
    for fn in (comdirect, dkb_giro, dkb_credit, mlp_triodos, apobank, sparkasse, deutschebank, commerzbank):

        skipperint=0 ## Skipperint is used to establish read in, even if transactions in the first 3 rows haven't been credited yet (date columuns have unusual string values)
        while skipperint<3:
            try:
                value,raw_data=fn(filepath,skipperint)
            except:
                skipperint+=1
            else:
                break
        if value=="other_acctype" or value=='unsupported acctype':
            continue
        else:
            break
    
    return (value,raw_data)

##function is only established to be able to control for errors with pandas data import values (i.e. if acc_type is recognized correctly)
def account_info_identifier(filepath):
    
    value,raw_data=acc_type_tester(filepath)
    accinfo_dict=make_accinfo_dict()
    
    #this complication was chosen deliberatly, so that acctype_recognition_tester return subtype of sparkasse
    if 'sparka' in value:
        accinfo_type='sparka_giro'
    else:
        accinfo_type=value
       
    return (accinfo_dict[accinfo_type],raw_data)


#This test function is only activated if script is run directly
def acctype_recognition_tester(folder_raw_test,filename):

    acctest_input=pd.read_excel(folder_raw_test+filename+'.xlsx',sheet_name="Testfiles")
    acctest_output=acctest_input.copy()
    test_list=[]
    for entry in range(0,len(acctest_output)):
        test_filepath=folder_raw_test+acctest_input.iloc[entry][1]+'.csv'
        test_list.append(acc_type_tester(test_filepath)[0])
    acctest_output["Testergebnis"]=test_list
    acctest_output.to_excel(folder_raw_test+filename+"_Results.xlsx",index=False,sheet_name='Testergebnisse')


##Development function for future adjustments to the account info dictionary
def accinfo_dict_writer(folder_raw_test,filename):

    #read in account info dictionary excel
    acc_info_read=pd.read_excel(folder_raw_test+filename+'.xlsx',sheet_name="Data")

    #Print out entries in Excel in the correct way for integration in code:
    print('Liste der Einträge im Kontoinfo Dictionary:\n\n')
    for entry in range(0,len(acc_info_read)):
        print("Kontotyp:"+acc_info_read.iloc[entry][0]+"\n")
        print(acc_info_read.iloc[entry][0]+"_info = ("+acc_info_read.iloc[entry][1]+','+acc_info_read.iloc[entry][2]+','+acc_info_read.iloc[entry][3]+",'"+acc_info_read.iloc[entry][4]+"',"+acc_info_read.iloc[entry][5]+','+acc_info_read.iloc[entry][6]+")\n\n")


#this snippet starts the testing code
if __name__ == "__main__":
    print('Willkommen zum Testscript. Die Testfunktion wird gestartet!')
    folder_raw_test=input('Bitte geben Sie den genauen Ordnerpfad an, in dem sich die Exceldatei mit den Test und Entwicklungsinformationen (Kontotyp und Dateinamen). Die zu testenden csv-Dateien müssen in demselben Ordner liegen.\n')+'/'
    filename=input('\nBitte geben Sie den Namen der Exceldatei ein.\n')
    recognition_test=acctype_recognition_tester(folder_raw_test,filename)
    print('Der Erkennungstest ist abgeschlossen. Die Ergebnisse sind in einer Excel ausgegeben worden.')

    #start accinfo_writer if selected
    printaccountinfo=input('\nSollen die Kontoinformationseinträge zum einfacheren Coden geplottet werden (ja oder nein)?\n')[0].lower()
    if printaccountinfo=='j':
        accinfo_dict_writer(folder_raw_test,filename)
        
        print('Vielen Dank!')
    else:
        print('Das Programm kann geschlossen werden.')