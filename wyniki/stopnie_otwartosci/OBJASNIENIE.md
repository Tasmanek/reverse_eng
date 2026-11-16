# Nadanie stopnia otwartości — CKAN i XML

## Gdzie dołączyć proces na Twoich zdjęciach

**W obu przypadkach punktem uruchomienia jest krok „Zapisz lub uaktualnij zbiory i zasoby”, a dokładniej zapis pojedynczego zasobu. Samo nadanie stopnia odbywa się później, w osobnym zadaniu przygotowania zasobu w tle.** Na udostępnionych zdjęciach nie ma osobnego zadania, które pokazuje to obliczenie.

| Twój diagram | Widoczny krok | Gdzie odbywa się nadanie stopnia |
|---|---|---|
| CKAN — górny proces na IMG_6024.jpeg, dalszy fragment u góry IMG_6025.jpeg | „Zapisz lub uaktualnij zbiory i zasoby” | Zapis zasobu może zlecić jego przygotowanie. W tym zadaniu: pobranie treści do oceny → obliczenie stopnia → zapis oceny → warunkowe odświeżenie publikacji. |
| XML — dolny proces na IMG_6025.jpeg; początek także na dole IMG_6024.jpeg | „Zapisz lub uaktualnij zbiory i zasoby” | Zapis zasobu może zlecić jego przygotowanie. Po rozpoznaniu zasobu i wymaganych kontrolach następuje ocena plików albo linku, zapis wyniku i warunkowe odświeżenie publikacji. |

**Propozycja uzupełnienia obu Twoich diagramów:** przy zapisie zasobu pokaż zlecenie do osobnej puli „Przygotowanie zasobu i nadanie stopnia otwartości”. W osobnej puli umieść odebranie zlecenia i odpowiedni załączony proces CKAN lub XML. Jeżeli modelujesz osobne pule, połącz je przepływem komunikatu, a nie przepływem sekwencji. Zlecenie jest wysyłane po zatwierdzeniu zapisu. Import nie czeka na ocenę ani na konwersje.

Nie należy wstawiać obowiązkowego obliczenia oceny za „Zapisz wynik i liczniki importu”, przed „Opublikuj dane” ani w kontroli „Cały plik poprawny?”. Wynik importu i przygotowanie zasobu to niezależne przebiegi; publikacja może być odświeżana ponownie, kiedy dostępna jest nowa ocena. Ocena dotyczy zasobu; status OK/OK_PARTIAL dotyczy importu.

Zapis nie zawsze uruchamia nowe obliczenie. Istotne są m.in. nowy publikowany zasób, zmiana linku, dostępności, odpowiednia zmiana wymuszenia typu lub przywrócenie. Sama zmiana nazwy formatu lub opisu może pozostawić poprzednią ocenę (U-3). Szczegółowe warunki pokazują wcześniejsze modele L2, w podprocesach publikacji i przygotowania zasobu.

Dodatkowa uwaga do zdjęć: w górnym procesie CKAN widoczna jest etykieta „Skonfiguruj źródło XML”. Jeśli oznacza konfigurację CKAN, warto zmienić ją na „Skonfiguruj źródło CKAN”.

## Co przygotowano

- **stopnie_otwartosci_ckan.bpmn** — samodzielny model CKAN; diagram główny i rozwijany podproces kalkulatora.
- **stopnie_otwartosci_xml.bpmn** — samodzielny model XML; diagram główny, ocena plików, kalkulator dla plików, kalkulator dla linku oraz osobny proces późniejszych konwersji.
- **PREZENTACJA.html** — opis dla biznesu i podglądy wszystkich diagramów, dostępne bez instalowania edytora.
- Pliki SVG — osobne podglądy poszczególnych diagramów, przydatne do prezentacji.

Pliki BPMN zawierają układ graficzny (BPMN DI). Otwórz je w edytorze BPMN obsługującym osobne diagramy podprocesów, np. bpmn-js. Podprocesy ze znakiem „+” mają własne diagramy. Osobny proces konwersji XML ma własny diagram. Model jest analityczny, niewykonywalny. SVG są podglądami; edytowalnym źródłem pozostaje BPMN.

## CKAN — algorytm biznesowy

1. Zadanie przygotowania zasobu rozpoczyna pracę po odebraniu zlecenia. W opisanym przebiegu CKAN nie tworzy pliku głównego ani lokalnych plików pochodnych.
2. Jeżeli format zasobu jest `None`, przyjmij stopień **0**.
3. W przeciwnym razie pobierz treść spod linku na potrzeby oceny. Użyj **formatu zapisanego w bazie**, który może pochodzić z deklaracji dostawcy. Pobranie nie oznacza zapisania kopii głównej.
4. Zastosuj reguły formatu i treści opisane poniżej. Archiwum pod linkiem nie przechodzi ścieżki oceny wnętrza lokalnego archiwum.
5. Zapisz ocenę zasobu w bazie. Datę weryfikacji zapisz tylko wtedy, gdy żąda tego zadanie.
6. Jeżeli przygotowanie zakończyło się sukcesem, nie ma odroczonych wyjątków, a zasób pozostaje opublikowany i nieusunięty, zleć odświeżenie wyszukiwarki i opisu RDF. W przeciwnym razie nie zlecaj tego końcowego odświeżenia; obsłuż ewentualny problem. Zapis oceny i pokazanie jej na portalu to dwa różne kroki.

## XML — algorytm biznesowy

1. Przygotuj zasób: sprawdź URL, rozpoznaj typ i format; dla pliku zapisz kopię główną, wykonaj wymagane kontrole pliku i danych. Dla API/WWW może nie być kopii głównej. Niepowodzenie wcześniejszej kontroli nie musi wykluczać samej próby oceny.
2. Jeżeli format **zasobu** jest `None`, stopień wynosi **0**.
3. Jeżeli nie ma pliku głównego, oceń treść spod linku według formatu zapisanego w bazie, podobnie jak w CKAN.
4. Jeżeli jest plik główny, oceń **każdy plik zasobu: główny i pochodne**. Format wnętrza archiwum ma pierwszeństwo przed formatem samego archiwum; `jsonstat` traktowany jest jak JSON.
5. Dla pojedynczego pliku bez formatu przyjmij **1**. To inna reguła niż brak formatu całego zasobu, który daje **0**.
6. Dla archiwum: zaszyfrowane → **0**; błąd odczytu → **1**; wiele plików → **1**, z wyjątkiem obsługi geotiff/shp; jeden plik → oceń plik wewnętrzny. W pozostałych przypadkach zastosuj kalkulator formatu i treści.
7. Stopień zasobu to **najwyższa ocena jego plików**. Zapisz wynik; odświeżenie publikacji zależy od tych samych warunków końcowych co w CKAN.

### Późniejsze podniesienie stopnia w XML

Po udanej indeksacji danych system zleca osobne zadanie konwersji. Pierwsze obliczenie oceny nie czeka na to zadanie.

- Gdy plik główny to XLS/XLSX, zasób nie jest `linked` i dostępne są dane tabeli, system tworzy pochodny CSV.
- Jeżeli dostępny jest CSV główny lub pochodny poza archiwum, system próbuje utworzyć JSON-LD. Powodzenie zależy od danych i dostępności usług; błąd nie daje nowego pliku.
- Jeśli powstanie nowy plik pochodny, system ponownie ocenia pliki, zapisuje maksimum i zleca warunkowe odświeżenie publikacji. Zadanie obejmuje też obsługę archiwum zbioru, pominiętą w tym diagramie, ponieważ nie ustala ona stopnia.

**Przykład:** sam XLSX ma 2; po utworzeniu CSV zasób może mieć 3; po udanej konwersji do JSON-LD może mieć 4 lub 5. Każdy wzrost wymaga powstania odpowiedniej postaci danych.

**Rozbieżność źródła:** skrót w zakładce „Stopień otwartości” mówi, że XML remote nie dostaje kopii. Bardziej szczegółowe SECTION-pliki-7 i SCEN-10 dopuszczają próbę JSON-LD z dostępnego CSV również dla remote, wykluczając tworzenie CSV z XLS/XLSX dla linked. Model zachowuje szczegółowe warunki wcześniejszego L2 (README V-03). Tego wariantu nie należy przedstawiać jako potwierdzonego testem działania produkcji. XML remote może też mieć plik główny; nie jest automatycznie równoważny ścieżce CKAN.

## Wspólne reguły przyznawania stopni

To reguły zaimplementowanego algorytmu opisanego w raporcie, a nie ogólny audyt zgodności z ideą pięciu gwiazdek.

| Format / sytuacja | Wynik algorytmu |
|---|---|
| Brak formatu zasobu (`None`) | 0 |
| PDF, JPG, TXT i wiele formatów dokumentowych | 1 — z tabeli formatów |
| XLS, XLSX | 2 — z tabeli formatów |
| CSV, TSV, HTML, ODS i inne odpowiednie formaty | 3 — z tabeli formatów |
| JSON | Próba odczytu jako RDF/JSON-LD: błąd lub pusty graf → 3; niepusty graf bez powiązań między domenami → 4; z powiązaniami → 5. |
| XML jako format ocenianych danych | Domyślnie 3; wszystkie elementy w przestrzeniach nazw → 4; dodatkowo poprawny RDF z powiązaniami między domenami → 5. |
| RDF i pokrewne, np. TTL, N3, NT, JSON-LD | Domyślnie 4; niepusty graf z powiązaniami między domenami → 5. |
| Format spoza tabeli, bez dedykowanego kalkulatora | 1 |

„Powiązania między domenami” oznaczają tutaj konkretną heurystykę kodu: URI z więcej niż jednej domeny, z pominięciem predykatów `rdf:`. Raport wskazuje, że sam kod zawiera TODO dotyczące tej definicji. Nie należy interpretować tego jako pełnego audytu Linked Open Data.

„XML” w wierszu kalkulatora oznacza **format danych zasobu**, a nie plik wykazu, z którego harvester pobiera listę zbiorów. Analogicznie odpowiedź JSON z API CKAN nie przesądza o formacie każdego zasobu.

## Różnice istotne dla biznesu

| Obszar | CKAN | XML |
|---|---|---|
| Co jest oceniane | Treść pod linkiem i zapisany format zasobu | Pliki główne i pochodne; przy braku pliku głównego treść pod linkiem |
| Źródło formatu | Może być deklaracją dostawcy; wcześniejszy błąd propagacji formatu U-1 może wpływać na zapis | Rozpoznanie podczas przygotowania pliku; dla ścieżki linku format z bazy |
| Łączenie ocen | Brak maksimum lokalnych plików w opisanej ścieżce | Maksimum ocen wszystkich plików zasobu |
| Archiwa | Bez lokalnego rozpoznawania wnętrza na potrzeby oceny linku | Specjalne reguły dla zapisanych archiwów |
| Konwersje podnoszące ocenę | Brak w opisanym przebiegu | Warunkowe CSV i JSON-LD, późniejsze przeliczenie |
| Reguły JSON / XML / RDF | Te same kalkulatory | Te same kalkulatory |

Przykład z raportu: PDF zadeklarowany w CKAN jako CSV otrzymał **3**, ponieważ algorytm kierował się zapisanym formatem. Zwykła strona HTML również uzyskała **3**. Sama ocena nie potwierdza prawdziwości, kompletności ani aktualności danych. W XML stare pliki pochodne mogą pozostać po wymianie pliku głównego i nadal wpływać na maksimum (U-12).

## Podstawa i granice ustaleń

Opracowanie opiera się na obu przesłanych JPEG, czterech istniejących BPMN, README oraz lokalnym raporcie `../harvester_walidacje_ckan_xml.html` (mcod 2.62.3, frontend 3.5.2, aktualizacja raportu 2026-11-08). Nie analizowano ponownie repozytorium aplikacji ani bieżącej produkcji.

Kluczowe dowody: `tab=ocena` (SECTION-ocena-5..8, ROW-ocena-001..003), `tab=pliki` (SECTION-pliki-7..8), kroki O2/O3/O9..O15/OALL/PB4 oraz OINCREASE/OREFRESH, sekwencje SX-316..323 i SC-307..312, SCEN-10, U-1, U-3, U-12 i rozbieżność V-03 w README.

Wyjątki pobierania linku wymagają ostrożności: wykorzystane materiały nie uzasadniają jednej uniwersalnej reguły „błąd pobrania = stopień 0”. Diagramy nie wprowadzają takiej reguły. Pokazują normalny przebieg oceny i udokumentowane wyniki specjalne (np. zaszyfrowane archiwum), a możliwy wyjątek nie stanowi gwarancji zapisania nowej oceny.
