# CKAN i XML — dokładny algorytm stopni otwartości

Model na podstawie lokalnego kodu mcod 2.62.3. Osobne przygotowanie CKAN i XML prowadzi do jednej wspólnej części oceny. To opis istniejącej implementacji, nie proponowana nowa polityka oceny. Sam stopień nie potwierdza jakości, aktualności ani prawdziwości danych.

## Najważniejsze rozróżnienie: brak stopnia, brak przeliczenia i stopień 1

| Sytuacja | Co rzeczywiście oznacza |
|---|---|
| **Obliczono i zapisano 0** | Algorytm zwrócił brak stopnia 1–5. To konkretny wynik, zapisany w polu oceny. |
| **Nie uruchomiono nowego przeliczenia** | Np. odrzucony import lub zbiór, brak sygnału przetwarzania, nowy szkic albo zmiana samego opisu/formatu. Może nie być nowego zasobu; istniejący nie dostaje nowej oceny. |
| **Obliczenie przerwał nieprzechwycony wyjątek** | Nie wykonano UPDATE nowej oceny zasobu. Istniejąca ocena pozostaje, nowy zasób ma zwykle domyślne 0. Nie należy automatycznie uznać tego za 0 ani 1 nadane przez algorytm. |
| **Obliczono i zapisano 1** | Najniższy dodatni stopień wynikający z określonych reguł, a nie uniwersalny wynik każdego błędu. |
| **Błąd podczas zapisu do bazy** | Nie potwierdzono pełnego zapisu. Ocena zasobu mogła być zaktualizowana przed błędem zapisu oceny któregoś pliku. Stan zależy od miejsca błędu i otaczającej transakcji. |

Pole Resource.openness_score nie jest opcjonalnym NULL: domyślnie ma **0**, zakres 0–5. Osobny rekord ResourceFile ma domyślnie **1**, ale to nie jest dowód przeprowadzenia oceny. Dlatego „brak stopnia” musi zostać doprecyzowany podczas rozmowy biznesowej.

## 1. Osobne wejścia CKAN i XML

**CKAN:** walidacja pobrania API/JSON/schematu oraz przyjęcie konkretnego zbioru → zapis zasobu i formatu → zlecenie przygotowania, jeśli spełniono warunki sygnału. Etap przygotowania CKAN pomija utworzenie pliku głównego i lokalną kontrolę danych tabeli. Ocena standardowo korzysta z linku i formatu zasobu zapisanego w bazie. Format może pochodzić z deklaracji dostawcy albo wcześniejszego rozpoznania; raport wskazuje też błąd propagacji formatu U-1. Nie ma lokalnych plików pochodnych w opisanej ścieżce.

**XML:** poprawne pobranie XML/MD5/XSD i przyjęcie całego wykazu → zapis zasobu → zlecenie przygotowania, jeśli spełniono warunki sygnału. Następnie URL, rozpoznanie typu i formatu, zapis pliku głównego, wymagane kontrole pliku i warunkowo danych tabeli. Po sukcesie indeksacji osobno zlecane są konwersje; pierwsza ocena nie czeka na ich zakończenie. XML remote także może mieć plik główny.

Błąd importu przed zapisem lub odrzucenie zbioru CKAN nie jest tym samym co błąd późniejszej oceny. Jeśli import nie utworzył zasobu, nie ma nowego zasobu, któremu można nadać stopień. Brak ponownej oceny istniejącego zasobu nie gwarantuje, że pozostanie on opublikowany — synchronizacja może go wycofać.

Błąd URL, pliku lub danych podczas przygotowania nie jest ogólną regułą „nie przyznawaj stopnia”. EntryPoint po przewidzianych etapach nadal próbuje wykonać update_resource_openness_score. Późniejszy wynik zależy od dostępnego stanu i ewentualnego wyjątku samej oceny.

## 2. Wspólny wybór źródła i wyniku zasobu

1. **Format zasobu jest dokładnie None → wynik 0**, bez oceniania linku i plików. Nawet gdy istnieje plik CSV, brak formatu zasobu zatrzymuje ten przebieg na 0. Pusty napis nie jest tym samym co None.
2. **Jest link i nie ma pliku głównego → oceń jedno źródło: link + format zasobu.** Wynik tego źródła jest wynikiem zasobu.
3. W przeciwnym razie oceń **wszystkie pliki zasobu**. Efektywny format pliku: compressed_file_format, a jeśli brak — format. Dla pliku jsonstat jest traktowany jak json; dla linku ta normalizacja nie występuje.
4. **Format pojedynczego pliku jest None → ocena tego pliku 1**, bez odczytu treści. Format całego zasobu None dawał wcześniej 0 — to dwie różne reguły.
5. Wynik zasobu to **maksimum ocen plików**. Pusta lista plików przy braku linku → 0. Wszystkie pliki z oceną 0 → wynik 0. Jeden plik ma 1, inny 3 → zasób ma 3. Stare pochodne pozostawione po zmianie pliku głównego także mogą wpływać na maksimum.
6. Najpierw obliczane są wszystkie wyniki, dopiero potem następuje UPDATE zasobu i ocen poszczególnych plików. Nieprzechwycony wyjątek obliczania jednego pliku może przerwać ocenę całego zasobu przed zapisem nowych wyników.

## 3. Jakie błędy NIE blokują automatycznie nadania stopnia

| Przypadek w samej funkcji oceny | Obsługa i możliwy wynik |
|---|---|
| **Timeout, błąd połączenia lub inny requests.RequestException przy pobraniu linku** | Wyjątek jest przechwycony; treść pozostaje None. Algorytm idzie dalej: PDF → 1, XLSX → 2, CSV → 3, JSON → 3, XML → 3, RDF/JSON-LD → 4, nieznany format → 1. To wyniki dla wskazanych formatów przy tym błędzie, nie dowód poprawności danych. |
| **HTTP 404/500 podczas pobrania do oceny** | get_source_data nie sprawdza status_code ani nie wywołuje raise_for_status. Wykorzystuje treść odpowiedzi i zapisany format. Np. odpowiedź 404 przy deklaracji CSV może dostać 3. Ten etap różni się od wcześniejszego download_file, który wymaga HTTP 200. |
| **JSON nie parsuje się jako JSON lub RDF/JSON-LD; pusty graf** | 3. Także brak treści po błędzie sieci. |
| **XML: brak treści, błędne parsowanie lub nieudany test przestrzeni nazw** | 3. |
| **XML przeszedł test na 4, ale test RDF/powiązań nie przeszedł albo zgłosił przechwycony wyjątek** | 4. |
| **Format RDF: błąd parsowania, brak trójek lub brak wymaganych powiązań** | 4. Także brak treści po błędzie sieci. |
| **Rozpoznane lokalne archiwum: wyjątek wewnątrz calculate_score_for_archive, inny niż PasswordProtectedArchiveError** | 1 dla tego źródła. Dotyczy też błędu otwarcia, ekstrakcji lub odczytu pliku wewnętrznego w tym try. |
| **Rozpoznane lokalne archiwum: PasswordProtectedArchiveError wewnątrz calculate_score_for_archive** | 0 dla tego źródła. Maksimum ocen innych plików może dać zasobowi wynik większy od 0. |

Kod oceny nie porównuje automatycznie każdej deklaracji formatu z rzeczywistą treścią. Nie należy interpretować gwiazdek jako potwierdzenia udanego pobrania, poprawnej tabeli lub jakości danych.

## 4. Kiedy nie powstaje nowa ocena

- Ocena nie została wywołana: nieaktywny/pominięty import, odrzucenie przed zapisem, odrzucony zbiór CKAN, przerwany zapis, nowy szkic, brak zmiany uruchamiającej przetwarzanie. Szczegółowe reguły sygnału są poza samym kalkulatorem; sam format/opis nie wymusza przeliczenia.
- **Lokalny plik nie istnieje lub nie daje się odczytać:** wyjątek z source.path, get_file_info albo open/read występuje przed try obsługi archiwum; nie jest zamieniany przez get_source_data na 1 ani 0. Przykłady: FileNotFoundError, PermissionError lub nieprzechwycony błąd rozpoznania MIME.
- Napis będący źródłem nie zaczyna się od `http`: funkcja traktuje go jak obiekt pliku i próbuje source.path; dla zwykłego napisu może to dać AttributeError.
- Inny nieprzechwycony wyjątek obliczania: np. problem ładowania zasobu, nieoczekiwany błąd poza lokalnym blokiem try. W kalkulatorze JSON test powiązań jest poza try parsowania; nieprzewidziany wyjątek w tym teście może propagować. Model pokazuje granicę błędu obliczania.
- Błąd podczas samego UPDATE wymaga osobnej diagnozy; nie jest regułą przypisania stopnia. Nie można zapewnić, że żaden wcześniejszy UPDATE się nie wykonał.

**Ważne:** istniejący zasób z oceną 3 po nieudanej próbie obliczania może nadal mieć w bazie 3. „Nie przyznano nowej oceny” nie oznacza, że użytkownik zobaczy zero gwiazdek. Brak końcowego odświeżenia wyszukiwarki również nie jest dowodem braku zapisu oceny w bazie.

## 5. Dokładne warunki stopnia 0

0 jest zwracane, gdy:

- format zasobu jest None;
- nie ma linku ani plików do oceny (po przejściu warunku formatu);
- maksimum ocen wszystkich plików wynosi 0, np. jedyny oceniany plik jest rozpoznanym zaszyfrowanym archiwum;
- lokalne archiwum w ocenie pojedynczego źródła rzuca PasswordProtectedArchiveError wewnątrz obsługi archiwum; na poziomie zasobu obowiązuje potem maksimum.

Wartość domyślna nowego zasobu 0 przed wykonaniem oceny jest odrębną sytuacją. Algorytm nie zamienia ogólnie timeoutu, 404, błędnego JSON ani błędnego RDF na 0.

## 6. Dokładne warunki stopnia 1

**Dla pojedynczego źródła lub pliku:**

- plik ma format None — bez odczytu treści;
- nie ma kalkulatora treści, a pierwsze dopasowanie w tabeli formatów ma ocenę 1, np. PDF, TXT, DOC/DOCX, JPG/PNG, TIFF;
- nie ma kalkulatora ani dopasowania w tabeli — domyślnie 1; dotyczy także pustego napisu i niepasującej wielkości liter, jeśli taka wartość dotrze do kalkulatora bez wcześniejszej normalizacji;
- rozpoznane lokalne archiwum ma liczbę plików różną od 1, a jego efektywny format jest na liście ARCHIVE_EXTENSIONS. Kod obejmuje także puste archiwum;
- wewnątrz calculate_score_for_archive wystąpi inny wyjątek niż PasswordProtectedArchiveError — np. błąd otwarcia, ekstrakcji lub odczytu wnętrza.

**Dla całego zasobu:** w ścieżce linku wynik źródła 1 jest wynikiem zasobu. W ścieżce plików stopień zasobu wynosi 1 tylko wtedy, gdy **maksimum ocen plików = 1**. Gdy którykolwiek plik ma 2–5, zasób dostaje tę wyższą ocenę.

Archiwum pod linkiem nie jest oznaczane jako archiwum przez tę funkcję. Link z formatem ZIP standardowo wpada w brak kalkulatora i brak wpisu w tabeli → 1; nie dostaje 0 za zaszyfrowanie, bo ta ścieżka nie rozpoznaje wnętrza archiwum.

## 7. Stopnie 2–5

| Stopień | Dokładna reguła |
|---|---|
| **2** | Brak kalkulatora treści, pierwsze dopasowanie w tabeli ma 2: np. XLS/XLSX/XLB, GIF, WEBP, GRIB/GRIB2, NC, ODI, PPM, XBM. |
| **3** | Format bez kalkulatora ma 3 w tabeli, np. CSV/TSV/HTML/ODS/GEOJSON; albo JSON nie daje niepustego grafu RDF; albo XML nie przechodzi testu na 4. |
| **4** | JSON daje niepusty graf RDF, który nie spełnia testu powiązań; albo XML przechodzi test przestrzeni nazw, ale nie test na 5; albo format RDF nie daje warunków na 5, również przy błędzie parsowania. |
| **5** | JSON: odczytany niepusty graf i dodatni test powiązań. XML: najpierw test przestrzeni nazw, potem poprawne parsowanie RDF, niepusty graf i dodatni test powiązań. RDF i pokrewne: poprawne parsowanie, trójki w kontekstach grafu i dodatni test powiązań. |

Sama obecność formatu w tabeli ocen nie oznacza, że jego upload lub pobranie zostanie dopuszczone przez wcześniejsze kontrole.

Pełna tabela formatów znajduje się w **TABELA_FORMATOW.csv** i w prezentacji HTML. Pierwsze wystąpienie rozszerzenia w SUPPORTED_CONTENT_TYPES rozstrzyga ocenę domyślną. Dedykowany kalkulator ma pierwszeństwo przed tabelą; przykładowo JSON-LD ma kalkulator RDF, a JSON kalkulator JSON.

### Dokładność testu XML

Test na 4 wymaga treści, poprawnego parsowania, co najmniej jednej deklaracji przestrzeni nazw oraz korzenia posiadającego elementy potomne — kod sprawdza `if not root`. Następnie sprawdza, czy tag każdego elementu zawiera którąś z zadeklarowanych wartości namespace. Pojedynczy element `<a xmlns="urn:test"/>` bez dzieci daje 3. To techniczny test implementacji, nie pełna ocena jakości XML.

„XML” w kalkulatorze oznacza format ocenianych danych zasobu. Nie oznacza wykazu, z którego harvester importuje opisy zbiorów.

### Dokładność testu powiązań

Kod przechodzi po kontekstach grafu i bierze URIRef występujące jako podmiot lub obiekt trójki. Pomija trójki z predykatem zaczynającym się od przestrzeni rdf. Zbiera `urlparse(URI).netloc`; wynik jest dodatni, gdy znajdzie więcej niż jedną odmienną wartość. **Nie odfiltrowuje pustego netloc**, więc opis „więcej niż jedna domena” jest uproszczeniem. Kod zawiera TODO dotyczące definicji. Nie traktuj wyniku 5 jako pełnej certyfikacji Linked Open Data.

## 8. Archiwa — dodatkowe rozróżnienia

Lokalny plik jest oznaczany jako archiwum na podstawie rozpoznanego MIME. Jeżeli ma jeden plik wewnętrzny, wyodrębnia się go i przekazuje dalej do kalkulatora. Zachowuje się efektywny format przekazany przez analizę pliku, jeśli jest spoza listy rozszerzeń archiwów; w innym przypadku bierze rozszerzenie pliku wewnętrznego.

Jeżeli liczba plików jest różna od 1, efektywny format spoza ARCHIVE_EXTENSIONS powoduje przekazanie źródła dalej do kalkulatora. W praktyce dotyczy to m.in. geotiff/shp; kod nie ogranicza jednak tej gałęzi tylko do tych dwóch nazw. Jeżeli format jest rozszerzeniem archiwum, zwraca 1. Nie ma rekurencyjnego rozpakowywania: wyodrębnione dane dostają is_archive=False.

## 9. Użycie BPMN i dowody

Główny diagram ma dwa wejścia: CKAN i XML, osobne podprocesy przygotowania i jeden podproces wspólnej oceny. Wewnątrz oceny, ścieżka linku i pętla po plikach odwołują się do **tej samej procedury „WSPÓLNE — ocena pojedynczego źródła”**. Jej ciało nie jest powielane w BPMN. Jest to callActivity z calledElement wskazującym proces w tym samym pliku; sposób przejścia do tego diagramu zależy od edytora. Wszystkie rozwinięcia są także dostępne w prezentacji HTML.

Zdarzenia błędu pokazują przechwycenie lub propagację istniejących wyjątków. Nie oznaczają nowo dodanego handlera, zmiany polityki biznesowej ani rollbacku. Zdarzenia początkowe CKAN/XML reprezentują alternatywne wywołania, nie równoległe przetwarzanie tego samego zasobu.

Podstawa: lokalny snapshot mcod/backend/2.62.3/98b9855d7b47cb8fd8680ab70c6114f138ac46123ea1541fbce2664866f09578-tree. Kluczowe symbole: Resource.get_openness_score, ResourceFile.get_openness_score, get_source_data, calculate_score_for_archive, get_score, calculate_score_for_json/xml/rdf, graph_contains_linked_data, update_resource_openness_score, oba entrypointy zadań, SUPPORTED_CONTENT_TYPES i RDF_FORMAT_TO_MIMETYPE. **ZRODLA.json** zawiera dokładne ścieżki, linie i sumy SHA-256.

Weryfikacja: sprawdzenie struktury XML/BPMN, referencji i układu; wykonanie 22 celowanych przypadków funkcji wyodrębnionych AST z kodu. Sieć, parser RDF, MIME i czytnik archiwum zastąpiono kontrolowanymi atrapami. Rzeczywisty był m.in. odczyt lokalnego pliku i parser XML. To weryfikacja sterowania i reguł błędów, nie test integracyjny Django/Celery ani potwierdzenie bieżącej produkcji. Szczegóły w **WERYFIKACJA_PRZYPADKOW.json**.
