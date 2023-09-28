from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import os
from nltk.corpus import stopwords 

def datascrapper(url: str,urlID:str ):
    response = requests.get(url)

    # Check if the request was successful (status code 200 mean the site is responding properly)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extracting the article title 
        title_element = soup.find('h1','entry-title')  
        if title_element:
            article_title = title_element.text
        else:
            title_element = soup.find('h1','tdb-title-text')
            article_title = title_element.text

        # Extracting the article text 
        text_element = soup.find( class_='td-post-content tagdiv-type') 
        if text_element:
            article_text = text_element.text 
        else:
            text_element = soup.findAll( class_='tdb-block-inner td-fix-index')
            article_text=text_element[14].text

        # Folder where we save our text files containing the article content
        drct='C:/Users/aruna/OneDrive/Documents/DataengineerBlackcoffer/textt/'

        fn=drct+urlID+".txt"

        # Creating our text files which contains the article content
        with open(fn,'w', encoding='utf-8') as file:
            file.write(article_title)
            file.write('\n')
            file.write(article_text)
    #Incase if the site is not working properly state the url and urlID
    else:
        print("The website : "+url+" with urlID : "+urlID+ " does not exist")

def calculatePostiveScore(f1):
    positive_score=0
    for i in f1:
        if i.lower() in positive_words :
            positive_score+=1
    return positive_score

def calculateNegativeScore(f1):
    negative_score=0
    for i in f1:
        if i.lower() in negative_words:
            negative_score+=1
    return negative_score

def calculateSubjectivity(ns,ps,cleanWords):
    return (ns+ps)/((cleanWords)+0.000001)

def calculatePolarityScore(ns,ps):
    return (ps-ns)/((ps+ns)+0.000001)

def calculateCleanWords(f1):
    cleanWords=0
    for i in f1:
        if i.lower() not in stopWords:
            cleanWords+=1
    return cleanWords

def calculateAvgSentenceLength(noOfChars,noOfSentences):
    return noOfChars/noOfSentences

def count_syllables(word):
    return len(
        re.findall('(?!e$)[aeiouy]+', word, re.I) +
        re.findall('^[^aeiouy]*e$', word, re.I)
    )

def percOfComplexWords(noOfWords,cw):
    return cw/noOfWords

def calculateComplexWords(f1):
    cwords=0
    for i in f1:
        if count_syllables(i)>2:
            cwords+=1
    return cwords
def noOfWordsPerSentence(noOfWords,noOfSentences):
    return noOfWords/noOfSentences

def fogIndex(asl,pcw):
    return 0.4*(asl+pcw)

def syllableCountPerWord(totsyl,noOfWords):
    return totsyl/noOfWords

def avgWordLen(noOfChars,noOfWords):
    return noOfChars/noOfWords

# This function does the natural language processing of our text files 
def nlp(file_path):

    # List of sentences For sentence related calculations
    f2=open(file_path,'r',encoding='utf-8', errors='replace')
    a2=f2.read()
    a2=a2.replace("\n",'.')
    a2=a2.replace("\xa0",'')
    a2=a2.split('.')
    while("" in a2):
        a2.remove("")

    # List of words for calculations
    f1=open(file_path,'r',encoding='utf-8', errors='replace')
    a1=f1.read().replace('\n', '')
    a1=a1.split()

    # Removal of un-necessary punctuations
    punc='?!,.�' 
    translator = str.maketrans('', '', punc)

    # Removes given punctuation from each string in the list
    a1 = [text.translate(translator) for text in a1]

    # Calculating Cleanwords
    cleanWords=0
    for i in a1:
        if i.lower() in stopWords:
            a1.remove(i)
        else:
            cleanWords+=1

    # Calculating Personal Pronouns
    perPro=0
    for i in a1:
        if i.lower() in ['i','we','my','our','us']:
            perPro+=1

    # Calculating Syllables count
    totsyl=0
    for i in a1:
        totsyl+=count_syllables(i)

    # Calculating total number of characters
    noOfChars=0
    for i in a1:
        noOfChars+=len(i)

    noOfWords=len(a1)
    noOfSentences=len(a2)

    ns=calculateNegativeScore(a1)
    ps=calculatePostiveScore(a1)
    cleanWords=calculateCleanWords(a1)
    pos=calculatePolarityScore(ns,ps)
    sj=calculateSubjectivity(ns,ps,cleanWords)
    asl=calculateAvgSentenceLength(noOfChars,noOfSentences)#
    cw=calculateComplexWords(a1)
    pcw=percOfComplexWords(noOfWords,cw)
    fi=fogIndex(asl,pcw)
    awps=noOfWordsPerSentence(noOfWords,noOfSentences)
    sc=syllableCountPerWord(totsyl,noOfWords)
    awl=avgWordLen(noOfChars,noOfWords)

    f1.close()
    f2.close()
    return [ns,ps,pos,sj,asl,pcw,fi,awl,cw,noOfWords,sc,perPro,awl]

if __name__ == "__main__":
    # Reading the given input data
    data=pd.read_excel(r'C:\Users\aruna\OneDrive\Documents\DataengineerBlackcoffer\input.xlsx')

    # Creating a dataframe for storing the output
    df=pd.DataFrame(data,columns=["URL_ID","URL"])
    df1=df

    # List of urls and urlids
    urls=[]
    for i in df['URL']:
        urls.append(i)
    urlIDs=[]
    for i in df["URL_ID"]:
        urlIDs.append(i)

    # Function to scrap the data and store it in text files with url_id as their name 
    for i in range(len(urls)):
        url=urls[i]
        urlId=str(urlIDs[i])
        datascrapper(url,urlId)

    # For initializing the stopwords hashmap from the given folder and also from the nltk package
    path = r"C:\Users\aruna\OneDrive\Documents\DataengineerBlackcoffer\StopWords"
    # Change the directory
    os.chdir(path)
    # Read text File
    stopWords=set()
    sw=[]
    def read_text_file(file_path):
        with open(file_path, 'r') as f:
            sw=(f.read().replace("|","").lower().split())
            for i in sw:
                stopWords.add(i)
    # Iterating through all files
    for file in os.listdir():
        # Checking whether file is in text format or not
        if file.endswith(".txt"):
            file_path = f"{path}\{file}"
            read_text_file(file_path)
    stow=set(stopwords.words('english'))
    stopWords=stopWords.union(stow)
    stopWords.add("")

    # Creating dictionary from given Positive_words
    positive_words={}
    f=open(r"C:\Users\aruna\OneDrive\Documents\DataengineerBlackcoffer\MasterDictionary\positive-words.txt")
    rdr=f.read().split()
    for i in range(len(rdr)):
        if rdr[i].lower() not in stopWords:
            positive_words[rdr[i]]=i
            
    # Creating dictionary from given Negative_words
    negative_words={}
    f=open(r"C:\Users\aruna\OneDrive\Documents\DataengineerBlackcoffer\MasterDictionary\negative-words.txt")
    rdr=f.read().split()
    for i in range(len(rdr)):
        if rdr[i].lower() not in stopWords:
            negative_words[rdr[i]]=i

    # Imputing our required parameters as headers in the desired output dataframe
    additional_headers = ['POSITIVE SCORE', 'NEGATIVE SCORE','POLARITY SCORE','SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS','FOG INDEX','AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT','SYLLABLE PER WORD','PERSONAL PRONOUNS','AVG WORD LENGTH']
    df1 = pd.DataFrame(df1, columns=df.columns.tolist() + additional_headers)

    # Path of our article text files folder 
    path = 'C:/Users/aruna/OneDrive/Documents/DataengineerBlackcoffer/Textt'
    os.chdir(path)
    ans=[]
    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".txt"):
            file_path = f"{path}/{file}"
            # print(file_path)
            [ans,ansu]=[(nlp(file_path)),float(file[0:-4])]

            # Find the row index where the value appears in the DataFrame
            row_index = df1.index[df1['URL_ID'] == ansu]
            columns_to_edit = ['POSITIVE SCORE', 'NEGATIVE SCORE','POLARITY SCORE','SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS','FOG INDEX','AVG NUMBER OF WORDS PER SENTENCE','COMPLEX WORD COUNT','WORD COUNT','SYLLABLE PER WORD','PERSONAL PRONOUNS','AVG WORD LENGTH']

            # Inserting the computed parameters in our output dataframe
            df1.loc[row_index, columns_to_edit] = ans
    
    df1.to_excel(r'C:\Users\aruna\OneDrive\Documents\DataengineerBlackcoffer\OUTPUT.xlsx',header=True,index=False)


