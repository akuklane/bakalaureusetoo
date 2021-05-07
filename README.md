# Valimi suuruse mõju ekspressiooni kvantitatiivsete tunnuste lookuste täppiskaardistamisele lümfoblastoidrakuliinides

Bakalaureusetöö on kättesaadav TÜ arvutiteaduse instituudi [lõputööderegistrist](https://comserv.cs.ut.ee/ati_thesis/index.php?year=2021).


## Kasutamine
1. Projekt kasutab [Python 3.7](https://www.python.org/downloads/release/python-370/) interpretaatorit. 
Juhis interpretaatori seadistamiseks on leitav [siit](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#add-existing-interpreter).

2. Paketihalduriga [pip](https://pypi.org/project/pip/) keskkonna seadistamine: 
`pip install -r requirements.txt`.

2. Tulemuste analüüsi on kordamiseks saab jooksutada kaustas `src/` olevaid faile `analysis.py` ja `analysis_components.py`.

3. Tulemuste visualiseerimiseks on võimalik jooksutada kaustas `notebooks/` olevaid faile `results_visalisation.ipynb`, 
   `results_visalisation_components.ipynb` ja `genes_cs_visualisation.Rmd`.


## Lühikokkuvõte

Inimese genoomis leiduvad kodeerivad osad, mida nimetatakse geenideks. Geenides olevate geneetiliste variantide järjestuste 
põhjal sünteesitakse geeniekspressiooni käigus valke, mis määravad ära organismi fenotüübi. Geeniekspressiooni mõjutavad 
geneetilised variandid asuvad ekspressiooni kvantitatiivsete tunnuste lookustes ja omavad valgusünteesi kaudu olulist mõju 
tunnuste, seal hulgas haiguste ja häirete, avaldumisele. Sageli on taoliste haigusi ja häireid põhjustavate variantide 
tuvastamine ning nende poolt mõjutatavate geneetilistest mehhanismidest arusaamine variantide omavahelise korrelatsiooni 
tõttu keeruline. Kasutades täppiskaardistamist on võimalik süstemaatiliselt hinnata geneetiliste variantide põhjuslikkuse 
tõenäosust, leides tunnuse signaalile vastavalt vähemalt ühte põhjuslikku varianti sisaldavad usaldusväärsete variantide hulgad. 
Senini ei ole aga uuritud valimi suuruse mõju täppiskaardistamise täpsusele põhjuslike variantide leidmisel. Siinse bakalaureusetöö 
eesmärgiks oli uurida, kuivõrd suuremate valimite kasutamine võimaldab tõsta statistilist usaldusväärsust põhjuslike variantide 
leidmisel lümfoblastoidrakuliinides. Töö käigus leiti, et valimi suurenedes muutub täppiskaardistamine täpsemaks, kuna suureneb 
nii statistiline usaldusväärsus põhjuslike variante leida kui ka statistiline võimsus põhjuslike variante sisaldavaid 
usaldusväärsete variantide hulkasid tuvastada. Täpsemalt leiti suuremate valimite korral rohkem täppiskaardistatud 
usaldusväärsete variantide hulkasid, mis sageli sisaldasid väiksemal hulgal tõenäoliselt põhjuslike variante.
