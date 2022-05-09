import glob
import os
import math
import stanza
import config
import valemid
import statistics
import numpy

nlp = stanza.Pipeline('et',  processors='tokenize, lemma, pos')

#loeme confist input tekstide kataloogi
file_path = config.kataloog + '/*.txt' 
if file_path == "": 
    raise ValueError("Tekstide kaust pole määratud")

#loeme confist teksi taset, mida analüüsida
text_level = "A1"
text_level = config.tekstitase

#loeme confist output tekstide kataloogi
file_output_path = config.minukaust

#kirjutame tulemused väljundfaili
file_results_output_name = file_output_path + '/indeksid' + '.csv'
file_results_output = open(file_results_output_name, "w", encoding="utf8")
index_pealkiri = "Tekst" + chr(9) + "Sonade arv tekstis" + chr(9) + "Lemmade arv tekstis" + chr(9) + \
        "KLSS" + chr(9) + "JLSS" + chr(9) + "MAAS" + chr(9) + "UBER" + chr(9) + "MTLD" + chr(9) + "HDD" + chr(9) + "MSTTR" + chr(10) + chr(13)
#kirjuta pealkirja väljundfaili
file_results_output.write(index_pealkiri)
matrixRow = ""

#loeme antud taseme tekstid input kataloogist
text = ""
f_Name = []
f_Name_Level = ""
for filename in glob.glob(file_path):
   fBaseName = os.path.basename(filename)
   f_Name = fBaseName.split(' ')
   f_Name_Level = f_Name[0]
   if f_Name_Level == text_level:
       with open(os.path.join(os.getcwd(), filename), "r", encoding="utf8") as f:
            text = f.read()

            #tekst stanza paketi töötlemiseks
            doc = nlp(text)
            #teksti sõnade massiiv, punktuatsioon, numbrid ja sümbolid väljaarvatud
            words_array = []
            for s_sentence in doc.sentences: 
                for w_word in s_sentence.words:    
                    if w_word.upos != "PUNCT" and w_word.upos != "NUM" and w_word.upos != "SYM" and w_word.upos != "PROPN" \
                        and not (w_word._feats != None and (w_word._feats.find("NumForm=Digit") > 0 or w_word._feats.find("Abbr=Yes") >= 0)):
                        words_array.append(w_word)      

            #sõnade arv kokku
            words_count = len(words_array) 
            
            if words_count > 50:
                new_text = ""
                for j in range (0, len(words_array)):   
                    new_text = new_text + " " + words_array[j].text

                #unikaalsete lemmade massiv
                text_lemmas = []

                for j in range(0, words_count - 1):     
                    #teksti unikaalsed lemmad
                    if words_array[j].lemma.lower() not in text_lemmas:
                            text_lemmas.append(words_array[j].lemma.lower()) 
                    
                #lemmade arv tekstis
                lemmas_count = len(text_lemmas)

                KLSS = round(lemmas_count / math.sqrt(2 * words_count), 4)
                JLSS = round(lemmas_count /  math.sqrt(words_count), 4)
                MAAS = round((math.log(words_count) - math.log(lemmas_count)) / math.ldexp(math.log(words_count), 2), 4)
                UBER = round(math.ldexp(math.log(words_count), 2) / (math.log(words_count) - math.log(lemmas_count)), 4)
                MTLD = round(valemid.mtld_calc(words_array, ttr_threshold = 0.72), 4)
                HDD = round(valemid.hdd(words_array, sample_size = 42.0), 4)
                MSTTR = round(valemid.msttr(new_text, window_length = 50), 4)

                #maatriksi koostamine
                matrixRow = matrixRow +  format(KLSS) + " " + format(JLSS) + " " + format(MAAS) + " " + \
                    format(UBER) + " " + format(MTLD) + " " + format(HDD) + " " + format(MSTTR) + ";"
            
                index_row = fBaseName + chr(9) + format(words_count) + chr(9) + format(lemmas_count) + chr(9) + \
                    format(KLSS) + chr(9) + format(JLSS) + chr(9) + format(MAAS) + \
                    chr(9) + format(UBER) + chr(9) + format(MTLD) + chr(9) + format(HDD) + \
                    chr(9) + format(MSTTR) + chr(10) 

                #kirjuta tulemuse rida väljundfaili
                file_results_output.write(index_row)

#korista ära viimane ;
matrixRow = matrixRow[0: -1]
#koosta tulemuse maatriksi
results_matrix = numpy.matrix(matrixRow)
#arvuta tulpade keskmised
mean_array = results_matrix.mean(0)
#arvuta tulpade standardhälbed 
sDeviation_array = results_matrix.std(0)

index_row = chr(10) + chr(13)
file_results_output.write(index_row)

#kirjuta keskmise väljundfaili
index_row = ""
for j in range(0, 7):
     index_row = index_row + format(round(mean_array[0, j], 4)) +  chr(9)
index_row = index_row[0: -1]
index_row = text_level +  chr(9) + "keskmine" +  chr(9) + "0" + chr(9) + index_row + chr(10)
file_results_output.write(index_row)

#kirjuta standardhälbe väljundfaili
index_row = ""
for j in range(0, 7):
     index_row = index_row + format(round(sDeviation_array[0, j], 4)) +  chr(9)
index_row = index_row[0: -1]
index_row = text_level +  chr(9) + "standardhalve" + chr(9) + "0" + chr(9) + index_row + chr(10)
file_results_output.write(index_row)

file_results_output.close()
