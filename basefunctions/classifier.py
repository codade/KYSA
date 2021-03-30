'''Classification class. Import of respective classification excel file is accomplished through user process call.
Accounts Data class accesses categorization functions. Every single data point in the respective "text" column of the imported files is
matched via regex check against existing values in classification table and the category returned. If no entry is found "other" is returned.
Classification table can be altered by user. Hardcoded category dictionary is only changeable through future updates.'''


import locale
import platform
import re
import string

import pandas as pd

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, 'German')
    FOLDER_SEP = '\\'
elif platform.system() == 'Darwin':
    locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
    FOLDER_SEP = '/'
else:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    FOLDER_SEP = '/'


#_______________________________________ read in history data for training machine learning algorithm _______________

def traindata_import(path, decrypt_success, language):
    '''Import saved training data'''
    if decrypt_success:
        training_data = pd.read_csv(path, sep=';')

    else:#create basic training dataframe (3 entries) if decryption failed
        if language == 'deu': #basic training dataframe in german
            training_data = pd.DataFrame({'scan text': ('Lastschrift Edeka', 'Lastschrift Hornbach', 'Überweisung Lohn/Gehalt'), 'cat': ('Supermarkt', 'Möbel & Wohn-\nbedarf', 'Lohn / Gehalt')})#fallback train data german
        else:
            training_data = pd.DataFrame({'scan text': ('withdrawal bank', 'rent flat street', 'wage transfer'), 'cat': ('cash withdrawal', 'rent', 'wage')}) #fallback train data english

    return training_data





#_______________________________________ Machine learning classification class _______________________________________

class MachineClassifier:
    '''Machine Learning Categorization class'''

    def __init__(self, training_data, language):

        #self.history_data=pd.read_csv(BytesIO(history_data),sep=';') #load transaction history data
        #start pipeline for machine learning categorization
        self.training_data = training_data
        #adjust locale if english is set as user language
        if language == 'eng':

            self.lang = 'eng'

            if platform.system() == 'Windows': #adjust locale if language choice is english
                locale.setlocale(locale.LC_ALL, 'English')
            elif platform.system() == 'Darwin':
                locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
            else:
                locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        else:
            self.lang = 'deu'

        self.pipeline = Pipeline([
            ('bow', CountVectorizer(analyzer=self.text_preprocess)),  # strings to token integer counts
            ('tfidf', TfidfTransformer()),  # integer counts to weighted TF-IDF scores
            ('classifier', MultinomialNB()),  # train on TF-IDF vectors w/ Naive Bayes classifier
            ])
        self.pipeline.fit(self.training_data['scan text'], self.training_data['cat'])


    def text_preprocess(self, text):
        '''Prepare data for subsequent categorization'''

        #Lowers text, removes punctuation and stopwords and returns a list of the cleaned words of the text
        # Check lowered characters to see if they are in punctuation
        nopunc = [char.lower() for char in text if char not in string.punctuation]

        # Join the characters again to form the string.
        nopunc = ''.join(nopunc)
        # Remove stopwords based on chosen language and return list of words
        if self.lang == 'eng':
            return [word for word in nopunc.split() if word not in stopwords.words('english')]

        else:
            return [word for word in nopunc.split() if word not in stopwords.words('german')]

    def machine_categorizer(self, data, noncategory_var):
        '''predicts possible category based on historical data. Main category is fixed'''

        subset = data[data['cat'] == noncategory_var].copy()
        subset['scan text'] = subset['act']+' '+subset['text']
        data.loc[data['cat'] == noncategory_var, 'cat'] = self.pipeline.predict(subset['scan text'])
        del subset
        return data

    def adjust_histo_data(self, histo_data):
        '''process data from excel to append it to existing training history data'''
        #add lines from manually adjusted excel files to history dataset
        histo_data['scan text'] = histo_data['act']+' '+histo_data['text'] #create scan text
        histo_data.dropna(subset=['scan text'], inplace=True) #drops empty values if present
        histo_data.drop(histo_data.columns[[0, 1]], axis=1, inplace=True) #drop 'act' and 'text' columns
        histo_data = histo_data.reindex(columns=histo_data.columns[[1, 0]]) #reindex data
        self.training_data = pd.concat([self.training_data, histo_data]) # ad new lines to history data file
        self.training_data.drop_duplicates(inplace=True, ignore_index=True) #drop identical data lines

    def traindata_export(self, training_datapath):
        '''write training data to csv'''

        self.training_data.to_csv(training_datapath, index=False, sep=';')


#_______________________________________ Classifier class and import changeable classification table _______________________________________

class ClassificationProcess:
    '''classification class, steers regex classification and machine classification'''

    def __init__(self, class_dir, machineclassifier, langdict):

        self.langdict = langdict
        self.machineclassifier = machineclassifier

        #read in and transform search dict
        class_path = class_dir+FOLDER_SEP+self.langdict['tablename'][0]
        self.search_dict = pd.read_excel(class_path, engine='openpyxl', sheet_name=self.langdict['tablesheets'][0], usecols=[0, 1]).dropna() #reads in list and drops Nan-values
        self.search_dict.columns = ['search words', 'cat'] #rename columns
        self.search_dict['search words'] = self.search_dict['search words'].apply(lambda entry: ''.join(self.machineclassifier.text_preprocess(entry))) #Clean search words from punctuation and stopwords and lower charactes
        self.search_dict = self.search_dict.set_index('search words')['cat'].to_dict() #transform list into dictionary for later word-baded categorization process

        #read in main category relation list
        self.catlist = pd.read_excel(class_path, engine='openpyxl', sheet_name=self.langdict['tablesheets'][1], usecols=[0, 1]).dropna() #reads in list and drops Nan-values
        self.catlist.columns = ['cat', 'main cat'] #rename columns


    def fixedvalue_categorizer(self, raw_text):
        '''regex classification based on defined search words'''
        scan_text = ''.join(self.machineclassifier.text_preprocess(raw_text))
        #categorize transaction text in every row based on classification search words
        for key in self.search_dict.keys():
            if re.findall(key, scan_text):#'string' value is the string value in the 'text' column in one row. 'key' refers to the search word in this context
                return self.search_dict[key] # if search word ('key') was found in string, return the corresponding category
        else:
            return self.langdict['noncategory'][0]#return 'unclear' value, if nothing was found

    def assign_maincats(self, data):
        '''assigns main categories after regex classification'''
        data = data.merge(self.catlist, on='cat', how='left') #add respective main categories#
        data.loc[data['main cat'].isna(), 'main cat'] = self.langdict['noncategory'][1] #rename main category where no corresponding value was found in catlist

        return data

    def categorize_rawdata(self, data, purpose):
        '''function coordinating the whole classification process'''

        if purpose == 'cashbook':#filter empty category rows in cashbook and add categories
            data.loc[data['cat'].isna(), 'cat'] = data[data['cat'].isna()]['text'].apply(self.fixedvalue_categorizer)
        else:
            data["cat"] = data['text'].apply(self.fixedvalue_categorizer)  ## do categorization based on search words

        #adaptions for personal needs
        data.loc[(data['cat'] == 'Einzahlung Gemein-\nschaftkonto')&(data['val'] > 0), 'cat'] = self.langdict['acctransfer'][1]
        data.loc[(data['cat'] == self.langdict['acctransfer'][0])&(data['val'] > 0), 'cat'] = self.langdict['acctransfer'][1]
        data = self.assign_maincats(data) # assign main categories to every subcategory

        #do machine classification if unclear categories exist after fixed-value categorization
        if data['cat'].str.contains(self.langdict['noncategory'][0]).any():
            data = self.machineclassifier.machine_categorizer(data, self.langdict['noncategory'][0])
        else:
            pass

        return data
