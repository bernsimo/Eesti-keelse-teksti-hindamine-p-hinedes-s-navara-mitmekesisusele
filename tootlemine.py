#import json
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

#loeme confist output tekstide kataloogi
file_output_path = config.minukaust
#loeme confist uute tekstide arvu
text_parts = 1
text_parts = config.tekstide_arv

#loeme kõik .txt laiendiga tekstid input kataloogist
text = ""
for filename in glob.glob(file_path):
   with open(os.path.join(os.getcwd(), filename), "r", encoding="utf8") as f:
       text = text + f.read()

if text == "":
    raise ValueError("Tühi fail")

#tekst stanza paketi töötlemiseks
doc = nlp(text)
#teksti sõnade massiiv, punktuatsioon, numbrid ja sümbolid väljaarvatud
words_array = []
for s_sentence in doc.sentences: 
    for w_word in s_sentence.words:    
        if w_word.upos != "PUNCT" and w_word.upos != "NUM" and w_word.upos != "SYM" and w_word.upos != "PROPN" \
            and not (w_word._feats != None and (w_word._feats.find("NumForm=Digit") > 0 or w_word._feats.find("Abbr=Yes") >= 0)):
            words_array.append(w_word)      

#vaatame, mis tulemuseks sai, moodustame massiivist teksti 
new_text = ""
for j in range (0, len(words_array)):   
    new_text = new_text + " " + words_array[j].text

#kirjutame saadud teksti output kausta kontrollimiseks
file_output_name = file_output_path + '/tekst' + '.txt'
file_output = open(file_output_name, "w", encoding="utf8")
file_output.write(new_text)
file_output.close()

#sõnade arv kokku
words_count = len(words_array) 
#sõnade arv ühes osas
text_words_count = round(words_count / text_parts)

k_start = 0
k_end = text_words_count

#kirjutame tulemused väljundfaili
file_results_output_name = file_output_path + '/indeksid' + '.csv'
file_results_output = open(file_results_output_name, "w", encoding="utf8")
index_pealkiri = "Tykk" + chr(9) + "Sonade arv tekstis" + chr(9) + "Lemmade arv tekstis" + chr(9) + \
        "KLSS" + chr(9) + "JLSS" + chr(9) + "MAAS" + chr(9) + "UBER" + chr(9) + "MTLD" + chr(9) + "HDD" + chr(9) + "MSTTR" + chr(10) + chr(13)
#kirjuta pealkirja väljundfaili
file_results_output.write(index_pealkiri)
matrixRow = ""

for k in range (0, text_parts):
    #tekstiosa analüüsi jaoks
    words_subarray = words_array[k_start : k_end]

    new_text = ""
    for j in range (0, len(words_subarray)):   
        new_text = new_text + " " + words_subarray[j].text

    #teksti sõnade arv
    words_count = len(words_subarray)

    #unikaalsete lemmade massiv
    text_lemmas = []

    for j in range(0, words_count - 1):     
        #teksti unikaalsed lemmad
        if words_subarray[j].lemma.lower() not in text_lemmas:
                text_lemmas.append(words_subarray[j].lemma.lower()) 
        
    k_start = k_start + text_words_count
    k_end = k_end + text_words_count

    #lemmade arv tekstis
    lemmas_count = len(text_lemmas)

    KLSS = round(lemmas_count / math.sqrt(2 * words_count), 4)
    JLSS = round(lemmas_count /  math.sqrt(words_count), 4)
    MAAS = round((math.log(text_words_count) - math.log(lemmas_count)) / math.ldexp(math.log(words_count), 2), 4)
    UBER = round(math.ldexp(math.log(words_count), 2) / (math.log(words_count) - math.log(lemmas_count)), 4)
    MTLD = round(valemid.mtld_calc(words_subarray, ttr_threshold = 0.72), 4)
    HDD = round(valemid.hdd(words_subarray, sample_size = 42.0), 4)
    MSTTR = round(valemid.msttr(new_text, window_length = 50), 4)

    matrixRow = matrixRow +  format(KLSS) + " " + format(JLSS) + " " + format(MAAS) + " " + \
         format(UBER) + " " + format(MTLD) + " " + format(HDD) + " " + format(MSTTR) + ";"

    # print ("")
    # print ("[Tükk: {}]", format(k))
    # print("[Sõnade arv tekstis: {}]".format(words_count))
    # print("[Lemmade arv tekstis: {}]".format(lemmas_count))

    # print("[KLSS: {}]".format(KLSS))
    # print("[JLSS: {}]".format(JLSS))
    # print("[MAAS: {}]".format(MAAS))
    # print("[UBER: {}]".format(UBER))
    # print("[MTLD: {}]".format(MTLD))
    # #HD-D is an idealized version of voc-D
    # print("[HDD: {}]".format(HDD))
    # print("[MSTTR: {}]".format(MSTTR))

   
    index_row = format(k + 1) + chr(9) +  format(words_count) + chr(9) +  format(lemmas_count) + chr(9) + \
        format(KLSS) + chr(9) +  format(JLSS) + chr(9) +  format(MAAS) + \
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
     index_row = index_row + format(round(mean_array[0, j], 4)) + chr(10)
index_row = index_row[0: -1]
index_row = "keskmine" + chr(9) + "0" + chr(9) + "0" + chr(9) + index_row + chr(10)
file_results_output.write(index_row)

#kirjuta standardhälbe väljundfaili
index_row = ""
for j in range(0, 7):
     index_row = index_row + format(round(sDeviation_array[0, j], 4)) + chr(10)
index_row = index_row[0: -1]
index_row = "standardhalbe" + chr(9) + "0" + chr(9) + "0" + chr(9) + index_row + chr(10)
file_results_output.write(index_row)

file_results_output.close()