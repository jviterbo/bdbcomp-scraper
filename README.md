# bdbcomp-scraper
Web scraper specifically created for extracting proceedings metadata from
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
    a) The original title of the paper (generally in Portuguese);
    b) The abstract of the paper (generally in Portuguese);
    c) The authors' names;
    d) The numbers of the initial and final pages (BUT NOT ALWAYS).
    
For some missing information, it was possible to complete:
    a) The paper's language: it was determined using "GoogleTrans" API;
    b) The title in English: title was translated using "GoogleTrans" API;
    c) The abstract in English: abstract was translated using "GoogleTrans" API;
    d) The number of pages: when not informed, it is determined with PyPDF2.
    
Besides, as BDBComp provides no information about sections, author's countries,
and author's e-mails, we assumed as default: "ART" for section, "BR" for author's 
country and "nomail@mail.com" for author's e-mail
    
IMPORTANT: Some useful information is still absent, such as Keywords and Author's 
affiliations.
    
It is recommmended that after running the program, users should reviewed files
 "Artigos.csv" and "Autores.csv" to check if any correction is needed and to 
try to provide missing information.
