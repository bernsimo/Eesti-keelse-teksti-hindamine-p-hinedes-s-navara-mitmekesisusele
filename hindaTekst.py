def analyzeText(textTyyp):
    import config
    import glob
    import os
    import math
    import stanza
    import valemid

    #loeb confist, kas tegu on üksiktekstiga või korpusega
    #TODO
    #kas lugeda parameetridest??
    #yksiktekst = textTyyp

    yksiktekst = config.yksiktekst  #1- üksisktekst, 0- korpus

    nlp = stanza.Pipeline('et',  processors='tokenize, lemma, pos')

    #loeme confist input tekstide kataloogi
    file_path = config.kataloog + '/*.txt' 
    if len(file_path) == 0: 
        raise ValueError("Tekstide kaust pole määratud")

    #loeme confist output  kataloogi
    file_output_path = config.minukaust

    #teksti taseme indeksite struktuur
    class IndValues:
        def __init__(self, txtLevel, KLSS_m, JLSS_m, MAAS_m, UBER_m, MTLD_m, HDD_m, MSTTR_m, KLSS_d, JLSS_d, MAAS_d, UBER_d, MTLD_d, HDD_d, MSTTR_d):
            self.txtLevel = txtLevel
            self.KLSS_m = KLSS_m
            self.JLSS_m = JLSS_m      
            self.MAAS_m = MAAS_m
            self.UBER_m = UBER_m
            self.MTLD_m = MTLD_m
            self.HDD_m = HDD_m
            self.MSTTR_m = MSTTR_m
            self.KLSS_d = KLSS_d
            self.JLSS_d = JLSS_d       
            self.MAAS_d = MAAS_d
            self.UBER_d = UBER_d
            self.MTLD_d = MTLD_d
            self.HDD_d = HDD_d
            self.MSTTR_d = MSTTR_d

    #teksti hindamise tulemuse struktuur
    class IndResult:
        def __init__(self, txtLevel, KLSS, JLSS, MAAS, UBER, MTLD, HDD, MSTTR, KLSS_d, JLSS_d, MAAS_d, UBER_d, MTLD_d, HDD_d, MSTTR_d):
            self.txtLevel = txtLevel
            self.KLSS = KLSS
            self.JLSS = JLSS      
            self.MAAS = MAAS
            self.UBER = UBER
            self.MTLD = MTLD
            self.HDD = HDD
            self.MSTTR = MSTTR
            self.KLSS_d = KLSS_d
            self.JLSS_d = JLSS_d       
            self.MAAS_d = MAAS_d
            self.UBER_d = UBER_d
            self.MTLD_d = MTLD_d
            self.HDD_d = HDD_d
            self.MSTTR_d = MSTTR_d

    #loeb confist sisse keskmised / standarthälved
    text_indexes = config.indexes_in
    if len(text_indexes) == 0:
        raise ValueError("Viga indeksite importimisel: indeksite maatriks puudub confis")

    text_indexes_lines = text_indexes.split('|')

    #koostab massiivi indeksite hoidmiseks
    IndArray = []
    line_data = []
    for j in range(0, len(text_indexes_lines)):
        line = text_indexes_lines[j]
        line_data = line.split(chr(9))

        if line_data[1][0:4] == "kesk":
            c1 = IndValues(line_data[0], 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0)
            c1.KLSS_m = float(line_data[2])
            c1.JLSS_m = float(line_data[3])
            c1.MAAS_m = float(line_data[4])
            c1.UBER_m = float(line_data[5])
            c1.MTLD_m = float(line_data[6])
            c1.HDD_m = float(line_data[7])
            c1.MSTTR_m = float(line_data[8])       
        else:
            if line_data[0] == c1.txtLevel:
                c1.KLSS_d = float(line_data[2])
                c1.JLSS_d = float(line_data[3])
                c1.MAAS_d = float(line_data[4])
                c1.UBER_d = float(line_data[5])
                c1.MTLD_d = float(line_data[6])
                c1.HDD_d = float(line_data[7])
                c1.MSTTR_d = float(line_data[8])
                IndArray.append(c1)
            else:
                raise ValueError("[Viga indeksite importimisel {} tase: vale maatriksi struktuur]", c1.txtLevel)

    #loeme üksiku .txt faili input kataloogist
    text = ""
    for filename in glob.glob(file_path):
        with open(os.path.join(os.getcwd(), filename), "r", encoding="utf8") as f:
            text = f.read()

    if len(text) == 0:
        raise ValueError("Viga teksti lugemisel, tühi tekst")

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

        print ("")
        print ("Teksti tüüp: üksiktekst") if yksiktekst == 1 else "Teksti tüüp: korpus"
        print ("Teksti indeksid:")
        if yksiktekst == 1:
            print("[KLSS: {}]".format(KLSS))
            print("[JLSS: {}]".format(JLSS))    
            print("[MTLD: {}]".format(MTLD))
        else:
            print("[MAAS: {}]".format(MAAS))
            print("[UBER: {}]".format(UBER))
            print("[HDD: {}]".format(HDD))
            print("[MSTTR: {}]".format(MSTTR))


    ResultArray = []
    for j in range(0, len(IndArray)):
        c1 = IndResult( IndArray[j].txtLevel, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        if KLSS < IndArray[j].KLSS_m - IndArray[j].KLSS_d:
            c1.KLSS_d = round(abs(KLSS - (IndArray[j].KLSS_m - IndArray[j].KLSS_d)), 4)
        else: 
            if KLSS >= IndArray[j].KLSS_m + IndArray[j].KLSS_d: 
                c1.KLSS_d = round(abs(KLSS - (IndArray[j].KLSS_m + IndArray[j].KLSS_d)), 4)  
            else:
                if KLSS >= IndArray[j].KLSS_m - IndArray[j].KLSS_d and KLSS < IndArray[j].KLSS_m + IndArray[j].KLSS_d:
                    c1.KLSS = 1
        
        if JLSS < IndArray[j].JLSS_m - IndArray[j].JLSS_d:
            c1.JLSS_d = round(abs(JLSS - (IndArray[j].JLSS_m - IndArray[j].JLSS_d)), 4)
        else: 
            if JLSS >=  IndArray[j].JLSS_m + IndArray[j].JLSS_d: 
                c1.JLSS_d = round(abs(JLSS - (IndArray[j].JLSS_m + IndArray[j].JLSS_d)), 4)  
            else:
                if JLSS >= IndArray[j].JLSS_m - IndArray[j].JLSS_d and JLSS < IndArray[j].JLSS_m + IndArray[j].JLSS_d:
                    c1.JLSS = 1

        if MAAS < IndArray[j].MAAS_m - IndArray[j].MAAS_d:   
            c1.MAAS_d = round(abs(MAAS - (IndArray[j].MAAS_m - IndArray[j].MAAS_d)), 4)
        else: 
            if MAAS >= IndArray[j].MAAS_m + IndArray[j].MAAS_d: 
                c1.MAAS_d = round(abs(MAAS - (IndArray[j].MAAS_m + IndArray[j].MAAS_d)), 4)
            else:       
                if MAAS >= IndArray[j].MAAS_m - IndArray[j].MAAS_d and MAAS < IndArray[j].MAAS_m + IndArray[j].MAAS_d:
                    c1.MAAS = 1
                    
        if UBER < IndArray[j].UBER_m - IndArray[j].UBER_d: 
           c1.UBER_d = round(abs(UBER - (IndArray[j].UBER_m - IndArray[j].UBER_d)), 4)
        else:
            if UBER >= IndArray[j].UBER_m + IndArray[j].UBER_d: 
                c1.UBER_d = round(abs(UBER - (IndArray[j].UBER_m + IndArray[j].UBER_d)), 4)
            else:
                if UBER >= IndArray[j].UBER_m - IndArray[j].UBER_d and UBER < IndArray[j].UBER_m + IndArray[j].UBER_d:
                    c1.UBER = 1

        if MTLD < IndArray[j].MTLD_m - IndArray[j].MTLD_d: 
            c1.MTLD_d = round(abs(MTLD - (IndArray[j].MTLD_m - IndArray[j].MTLD_d)), 4)
        else:
            if MTLD >= IndArray[j].MTLD_m + IndArray[j].MTLD_d: 
                c1.MTLD_d = round(abs(MTLD - (IndArray[j].MTLD_m + IndArray[j].MTLD_d)), 4)
            else:
                if MTLD >= IndArray[j].MTLD_m - IndArray[j].MTLD_d and MTLD < IndArray[j].MTLD_m + IndArray[j].MTLD_d:
                    c1.MTLD = 1

        if HDD < IndArray[j].HDD_m - IndArray[j].HDD_d: 
            c1.HDD_d = round(abs(HDD - (IndArray[j].HDD_m - IndArray[j].HDD_d)), 4)
        else:
            if HDD >= IndArray[j].HDD_m + IndArray[j].HDD_d: 
                c1.HDD_d = round(abs(HDD - (IndArray[j].HDD_m + IndArray[j].HDD_d)), 4)
            else:
                if HDD >= IndArray[j].HDD_m - IndArray[j].HDD_d and HDD < IndArray[j].HDD_m + IndArray[j].HDD_d:
                    c1.HDD = 1

        if MSTTR < IndArray[j].MSTTR_m - IndArray[j].MSTTR_d: 
            c1.MSTTR_d = round(abs(MSTTR - (IndArray[j].MSTTR_m - IndArray[j].MSTTR_d)), 4)
        else:
            if MSTTR >= IndArray[j].MSTTR_m + IndArray[j].MSTTR_d: 
                c1.MSTTR_d = round(abs(MSTTR - (IndArray[j].MSTTR_m + IndArray[j].MSTTR_d)), 4)
            else:
                if MSTTR >= IndArray[j].MSTTR_m - IndArray[j].MSTTR_d and MSTTR < IndArray[j].MSTTR_m + IndArray[j].MSTTR_d:
                    c1.MSTTR = 1
        
        ResultArray.append(c1)

    if len(ResultArray) == 0:
        raise ValueError("Viga ")

    print ("")
    print ("Hindamise tulemused A2, B1, B2, C1 järgi:") 

    for j in range(0, len(ResultArray)):
        print ("Tase: ", ResultArray[j].txtLevel) 

        if yksiktekst == 1:
            #lühike tekst
            print("[KLSS: {}]".format(ResultArray[j].KLSS))
            print("[KLSS_d: {}]".format(ResultArray[j].KLSS_d))
            print("[JLSS: {}]".format(ResultArray[j].JLSS))
            print("[JLSS_d: {}]".format(ResultArray[j].JLSS_d))
            print("[MTLD: {}]".format(ResultArray[j].MTLD))
            print("[MTLD_d: {}]".format(ResultArray[j].MTLD_d))
        else:
            #korpus
            print("[MAAS: {}]".format(ResultArray[j].MAAS))
            print("[MAAS_d: {}]".format(ResultArray[j].MAAS_d))
            print("[UBER: {}]".format(ResultArray[j].UBER))    
            print("[UBER_d: {}]".format(ResultArray[j].UBER_d))           
            print("[HDD: {}]".format(ResultArray[j].HDD))
            print("[HDD_d: {}]".format(ResultArray[j].HDD_d))
            print("[MSTTR: {}]".format(ResultArray[j].MSTTR))
            print("[MSTTR_d: {}]".format(ResultArray[j].MSTTR_d))
        print ("")

    print ("Kokkuvõte:") 

    if yksiktekst == 1:
        #lühike tekst
        ResultArray.sort(key=lambda x: x.KLSS_d, reverse=False)
        print ("KLSS järgi teksti tase: " + ResultArray[0].txtLevel)

        ResultArray.sort(key=lambda x: x.JLSS_d, reverse=False)
        print ("JLSS järgi teksti tase: " + ResultArray[0].txtLevel)

        ResultArray.sort(key=lambda x: x.MTLD_d, reverse=False)
        print ("MTLD järgi teksti tase: " + ResultArray[0].txtLevel)
    else:
        #korpus
        ResultArray.sort(key=lambda x: x.MAAS_d, reverse=False)
        print ("MAAS järgi teksti tase: " + ResultArray[0].txtLevel)

        ResultArray.sort(key=lambda x: x.HDD_d, reverse=False)
        print ("HDD järgi teksti tase: " + ResultArray[0].txtLevel)

        ResultArray.sort(key=lambda x: x.UBER_d, reverse=False)
        print ("UBER järgi teksti tase: " + ResultArray[0].txtLevel)

        ResultArray.sort(key=lambda x: x.MSTTR_d, reverse=False)
        print ("MSTTR järgi teksti tase: " + ResultArray[0].txtLevel)



analyzeText(0)