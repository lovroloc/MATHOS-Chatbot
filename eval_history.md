Baseline (naivni chunking, tekst bez naslova):
  answer_in_context: 15/20  (kolegiji 5/10, osoblje 10/10)
  URL top-1: 0/10

+ naslov u tekstu chunka, obogaćen tekst kolegija, websearch_to_tsquery:
  answer_in_context: 20/20  (kolegiji 10/10, osoblje 10/10)
  URL top-1: 10/10

Guardrails (6 pitanja): 5/6 ispravno odbijeno
  - 1 "neuspjeh" bio je zapravo ispravan odgovor s citiranim izvorom;
    eval pitanje je preformulirano
Nakon korekcije: 5/5

Baseline (naivni chunking):              15/20  (kolegiji 5/10)
+ naslov u chunku, obogaćen tekst:       20/20
Prošireni eval set (40 pitanja):         32/40
+ popravljena metrika:                   37/40



samo 41% zaposlenika u bazi ima javni profil na stranici, jer baza sadrži i vanjske i bivše suradnike koje web ne prikazuje.


# Evaluacija — povijest

## Retrieval (answer-in-context)

| Konfiguracija | Rezultat |
|---|---|
| Naivni chunking (800 znakova, fiksno) | 15/20 |
| + semantički chunking po odlomcima | 20/20 |
| Prošireni eval set (40 pitanja) | 32/40 |
| + naslov u tekstu chunka, obogaćen tekst kolegija | 37/40 |
| + strukturirani staff lookup, info dokument | 38/40 |

## Generacija (točnost odgovora)

| Konfiguracija | Rezultat |
|---|---|
| Prva mjerenja | 36/40 |
| + popravljen staff lookup, info dokument | 37/40 |
| + popravljena eval očekivanja | 38/38 (prekinuto na kvoti) |

## Guardrails

| Test | Rezultat |
|---|---|
| Odbijanje pitanja izvan opsega | 5/5 |

## Napomene
- Dio ranijih "promašaja" bili su artefakti metrike (dijakritika, en dash,
  format broja), ne greške sustava — popravljeno normalizacijom i
  listama prihvatljivih pojmova.
- 45 kolegija iz baze nema WP stranicu; 68 od 116 zaposlenika nema
  javni profil (vanjski i bivši suradnici).


Ablacijskom analizom utvrđeno je da hibridni dohvat ne nadmašuje čisto vektorsko pretraživanje na ovom korpusu. Leksička komponenta (BM25) samostalno postiže 36/40, no njezino uključivanje u fuziju ne donosi poboljšanje — smanjivanje njezine težine monotono popravlja rezultat sve dok se ne izjednači s čisto vektorskim pristupom. Razlog je vjerojatno nedostatak hrvatske konfiguracije za pretragu cijelog teksta u PostgreSQL-u: bez stemminga, upiti u prirodnom jeziku moraju biti spojeni OR operatorom, što unosi slabo relevantne kandidate visoko u poredak.

Eval set koji ne pokriva sve tipove upita može navesti na pogrešan zaključak o arhitekturi. U prvoj iteraciji, bez pitanja koja sadrže šifre kolegija, ablacija je sugerirala da leksička komponenta ne doprinosi. Nakon dodavanja pet takvih pitanja, hibridni dohvat nadmašuje čisto vektorski po svim mjerenim veličinama, a leksička komponenta rješava 5/5 upita po šifri naspram 2/5 koliko postiže vektorski pristup.


Ispitana je mogućnost odbijanja upita izvan opsega na temelju praga kosinusne sličnosti najboljeg dohvaćenog odsječka. Analiza pokazuje da se distribucije sličnosti za upite u opsegu (0.788–0.924) i izvan opsega (0.809–0.857) gotovo potpuno preklapaju. Pri pragu 0.86, koji odbacuje sve upite izvan opsega, zadržava se samo 27 od 45 legitimnih upita. Zaključeno je da prag sličnosti nije primjenjiv na ovom korpusu, te je odbijanje upita izvan opsega prepušteno sustavskom promptu, koji na testnom skupu postiže 5/5 ispravnih odbijanja.
=== PITANJA U OPSEGU ===
  min=0.788  prosjek=0.867  max=0.924

=== PITANJA IZVAN OPSEGA ===
  0.857  koliko ja imam ECTS-a
  0.833  jesam li položio Matematiku 1
  0.814  tko je predsjednik Republike Hrvatske
  0.809  napiši mi seminarski rad o grafovima
  0.813  koliko košta studij na FER-u
  0.831  kad je rok za prijavu na Erasmus 2027
  min=0.809  prosjek=0.826  max=0.857

=== ANALIZA PRAGA ===
  prag    zadržano u opsegu    odbijeno izvan opsega
  0.75              45/45                     0/6   
  0.76              45/45                     0/6   
  0.77              45/45                     0/6   
  0.78              45/45                     0/6   
  0.79              44/45                     0/6   
  0.80              44/45                     0/6   
  0.81              44/45                     1/6   
  0.82              43/45                     3/6   
  0.83              39/45                     3/6   
  0.84              37/45                     5/6   
  0.85              29/45                     5/6   
  0.86              27/45                     6/6   
  0.87              22/45                     6/6   
  0.88              16/45                     6/6   
  0.89              12/45                     6/6   
  0.90               7/45                     6/6   
  0.91               4/45                     6/6   
  0.92               1/45                     6/6   
  0.93               0/45                     6/6   
  0.94               0/45                     6/6   
  0.95               0/45                     6/6   


Ispitan je utjecaj cross-encoder rerankera (bge-reranker-v2-m3) na kvalitetu dohvata. Pri optimalnoj veličini skupa kandidata (8), reranker poboljšava pogodak izvornog URL-a s 20/22 na 21/22, dok točnost dohvaćenog konteksta ostaje nepromijenjena (44/45). Međutim, latencija dohvata raste s 84 ms na 2367 ms, odnosno 28 puta. Uzimajući u obzir da se dobitak svodi na jedan upit od 45, reranker nije uključen u konačnu konfiguraciju sustava.


Contextual Retrieval postiže isto poboljšanje pogotka izvora kao cross-encoder reranker (21/22 naspram 20/22), uz dodatno poboljšanje točnosti dohvaćenog konteksta (45/45 naspram 44/45), ali bez ikakvog povećanja latencije u trenutku upita, budući da se trošak generiranja konteksta plaća jednokratno pri indeksiranju. Napominjemo da je zbog ograničenja besplatnog API tiera kontekst generiran za samo 332 od približno 2660 odsječaka koji pripadaju višedijelnim dokumentima (12%), pa izmjereni učinak predstavlja donju granicu potencijalnog poboljšanja.