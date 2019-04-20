# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 22:54:04 2019

@author: Viterbo, J.

This is a web scraper specifically created for extracting proceedings metadata from 
BDBComp website (http://www.lbd.dcc.ufmg.br/bdbcomp). 

It receives as input:
    
    1) The event acronym
    2) The event year
    3) The ID number of the event in BDBComp system
    
What does it do?
    
    1) It creates the directory "ACRONYM-YEAR" as a subdirectory of the working
       directory;
    2) For each paper listed in the event proceedings' page, it downlods the 
       respective PDF files and stores in the new directory;
    3) It creates a file called "Artigos.csv", containing the metadata relative 
       to all the papers listed in the event proceedings page, and stores it in
       new directory;
    4) It creates a file called "Autores.csv", containing the metadata relative 
       to the authors of the papers listed in the event proceedings page, and 
       stores it in new directory.
       
The information available at the event proceedings pages is not complete. The 
site contains only:
    - The original title of the paper (generally in Portuguese);
    - The abstract of the paper (generally in Portuguese);
    - The authors' names;
    - The numbers of the initial and final pages (NOT ALWAYS).
    
For some missing information, it was possible to complete:
    - The paper's language: it was determined using "GoogleTrans" API;
    - The title in English: title was translated using "GoogleTrans" API;
    - The abstract in English: abstract was translated using "GoogleTrans" API;
    - The number of pages: when not informed, it is determined with PyPDF2.
    
Besides, as BDBComp provides no information about sections, author's countries,
and author's e-mails, we assumed as default:  
    - "ART" for section
    - "BR" for author's country
    - "nomail@mail.com" for author's e-mail
    
IMPORTANT: Some useful information is still absent, such as:
    - Keywords
    - Author's affiliations
    
It is recommmended that after running the program, users should reviewed files
 "Artigos.csv" and "Autores.csv" to check if any correction is needed and to 
try to provide missing information. 
       
"""

import os
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from pathlib import Path
from bs4 import BeautifulSoup
from googletrans import Translator
from PyPDF2 import PdfFileReader


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def getart(link):
    """
    Attempts to get the content at `url` that corresponds to an article
    page.
    """
    html = simple_get(link)
    return BeautifulSoup(html,"html5lib")

def save_pdf(num,url):
    """
    Downloads an saves a PDF file corresponding to an article.
    """
    if num < 10:
        filename = "00"+str(num)+".pdf"
    elif num < 100:
        filename = "0"+str(num)+".pdf"
    else:
        filename = str(num)+".pdf"
    filename = Path(filename)
    response = get(url)
    filename.write_bytes(response.content)
    return filename


""" 
Creates a set of lists to store article's info
"""
langlist = list()
titlelist = list()
titleenlist = list()
abstractlist = list()
abstractenlist = list()
pageslist = list()

""" 
Creates a set of lists to store author's info
"""
autnumlist = list()
firstlist = list()
middlelist = list()
lastlist = list()

""" 
Input data
"""
abbrev = input("Digite o acrônimo do evento: ")
year = input("Digite o ano da edição do evento: ")
codlink = input ("Digite o ID da página do evento no BDBComp: ")

""" 
Creating directory
"""
newpath = abbrev+"-"+year
try:
    os.mkdir(newpath)
    print("\nCreating the directory \""+newpath+"\" to store output files")
except FileExistsError:
    print("\nOutput files will be stored in directory \""+newpath+"\"")
os.chdir(newpath)

""" 
Getting the content of the index page 
"""
html = simple_get("http://www.lbd.dcc.ufmg.br/bdbcomp/servlet/Evento?id="+codlink)

res = BeautifulSoup(html,"html5lib")

divs = res.findAll('div', class_= 'titulo')
for div in divs:
    tituloconf = div.text
    print("\nExtracting metadata for the proceedings of: "+tituloconf)
 
translator = Translator()

""" 
Extracting information about pagination 
"""
divs = res.findAll('div', class_='conteudo')
itens = divs[0].findAll("li")
for item in itens:
    flag = 0
    for child in item.children:
        if flag == 1:
            pages = str(child) 
            pages = pages.replace('<i>.','')
            pages = pages.replace('</i>','')
            pages = pages.replace('<p>','')
            pages = pages.replace('</p>','')
            pages = pages.replace('\n',' ')
            pages = pages.rstrip('\r\n')
            pages = pages.lstrip()
            pages = pages.rstrip()
            pageslist.append(pages)
            flag = 0
        if str(child).find("Trabalho") != -1:
            flag = 1
tags = divs[0].findAll("a")

""" 
Extracting information about title, authors, etc 
"""
k = 1
tamaut = 0
for tag in tags:
    s = tag['href']
    if s.startswith("Trabalho"):
        link = "http://www.lbd.dcc.ufmg.br/bdbcomp/servlet/" + s
        art = getart(link)
        """ 
        Extracting title 
        """
        divs = art.findAll('div', class_= 'titulo')
        for div in divs:
            titulo = div.text
            titlelist.append(titulo)
#            print(str(k)+": "+titulo)
        """ 
        Extracting authors 
        """
        auts = art.findAll('a')
        for aut in auts:
            autlink = aut['href']
            if autlink.startswith("Autor"):
                tamaut = tamaut + 1
                autname = aut.text
                autnames = autname.split(' ')
                first = autnames[0]
                autnames.pop(0)
                autnames.reverse()
                last = autnames[0]
                autnames.pop(0)
                autnames.reverse()
                middle = ""
                for x in autnames:
                    middle = middle + x +" "
                middle = middle.rstrip()
                autnumlist.append(str(k))
                firstlist.append(first)
                middlelist.append(middle)
                lastlist.append(last)
                #print(str(k)+": "+first+" "+middle+" "+last)
            """ 
            Collecting PDF file 
            """
            if autlink.startswith("http://www.lbd.dcc.ufmg.br/colecoes"):
                print("Downloading paper "+str(k)+"...")
                filename = save_pdf(k,autlink)
                """ 
                Checking number of pages of PDF file, if there is no pagination 
                """
                if pageslist[k-1] == "":
                    f = open(filename,'rb')
                    pdf = PdfFileReader(f)
                    pageslist[k-1] = str(pdf.getNumPages())
                    #print(pageslist[k-1])
                    f.close
        """ 
        Extracting abstract 
        """
        divs = art.findAll('div', class_= 'conteudo')
        for div in divs:
            pars = div.findAll('p')
            i = 1
            for par in pars:
                if i == 5:
                    abst = str(par)
                    abst = abst.replace('<p>','')
                    abst = abst.replace('</p>','')
                    abst = abst.rstrip('\r\n')
                    abst = abst.lstrip('\r\n')
                    abstractlist.append(abst)
#                    print(abst+'\n')
                    langtit = translator.detect(titulo).lang
                    if abst != "":
                        lang = translator.detect(abst).lang
                    else:
                        lang = langtit
                    if lang != langtit:
                        lang = langtit
                    langlist.append(lang)
                    """ 
                    Translating title and abstract 
                    """
                    if lang != 'en':
                        print("Translating paper "+str(k)+" title and abstract...")
                        abstrans = translator.translate(abst)
                        absen = abstrans.text
                        tittrans = translator.translate(titulo)
                        titen = tittrans.text
                    else:
                        absen = abst
                        titen = titulo
                    abstractenlist.append(absen)
                    titleenlist.append(titulo)
#                    print("From "+ lang + ": " + absen+'\n')
                i = i + 1
        k = k + 1
tam = k - 1

print(str(tam)+" articles found, with "+str(tamaut)+" authors\n")
        
""" 
Writing "Artigos.cvs" 
"""
artfile = open("Artigos.csv", "w", encoding="utf-8")
artfile.write("seq;language;sectionAbbrev;title;titleEn;abstract;abstractEn;keywords;keywordsEn;pages;fileLabel;fileLink\n")

for k in range(0,tam):
    artfile.write(str(k+1)+";"+langlist[k]+";ART;"+titlelist[k]+";"+titleenlist[k]+";\""+abstractlist[k]+"\";\""+abstractenlist[k]+"\";;;\""+pageslist[k]+"\";PDF;\n")
    artfile.flush
    k = k + 1
artfile.close

""" 
Writing "Autores.cvs" 
"""
autfile = open("Autores.csv", "w", encoding="utf-8")
autfile.write("article;authorFirstname;authorMiddlename;authorLastname;authorAffiliation;authorAffiliationEn;authorCountry;authorEmail;orcid;authorBio;authorBioEn\n")

for k in range(0,tamaut):
    autfile.write(autnumlist[k]+";"+firstlist[k]+";"+middlelist[k]+";"+lastlist[k]+";;;BR;nomail@mail.com;;;\n")
    autfile.flush
    k = k + 1
autfile.close
                
autfile = open("Autores.csv", "w", encoding="utf-8")
autfile.write("article;authorFirstname;authorMiddlename;authorLastname;authorAffiliation;authorAffiliationEn;authorCountry;authorEmail;orcid;authorBio;authorBioEn\n")

for k in range(0,tamaut):
    autfile.write(autnumlist[k]+";"+firstlist[k]+";"+middlelist[k]+";"+lastlist[k]+";;;BR;nomail@mail.com;;;\n")
    autfile.flush
    k = k + 1
autfile.close
