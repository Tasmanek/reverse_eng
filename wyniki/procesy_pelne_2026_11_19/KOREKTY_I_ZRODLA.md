# CKAN, XML i ręczne dodawanie — uzupełnienie modeli AS-IS

Data: 19.11.2026. Podstawa: lokalny snapshot mcod 2.62.3. Nie dodano projektowanych blokad formatów/stopni ani flagi `is_archive`.

## Dlaczego poprzednie screeny różniły się zakresem

Widoki importu urywały szczegóły przy zapisie katalogu, a widok ręczny rozwijał także przygotowanie w tle. To niespójne poziomy szczegółowości, a nie brak konwersji w XML. XML i ręcznie dodane zasoby korzystają z tego samego algorytmu tworzenia plików pochodnych. CKAN ma rzeczywistą różnicę: `process_resource_from_url_task` zwraca sukces bez pobrania kopii dla zasobów CKAN. Standardowy nowy zasób CKAN nie przechodzi więc tej samej lokalnej indeksacji i konwersji.

## Co otworzyć

- `PREZENTACJA.html` — trzy uzupełnione widoki oraz 60 dodatkowych diagramów szczegółowych, lokalnie, bez CDN i połączeń sieciowych. Powiększanie, dopasowanie, osobne SVG; dokumentacja po najechaniu na element.
- `ckan_uzupelniony.bpmn`, `xml_uzupelniony.bpmn`, `manual_uzupelniony.bpmn` — porównywalne widoki główne, każdy z układem BPMN DI.
- `*_szczegoly.bpmn` — szczegółowe modele z podprocesami, odtworzone z wcześniejszych lokalnych modeli L2 i modelu ręcznego; wskazane poniżej fragmenty sprawdzono ponownie z kodem i poprawiono.
- `*_uzupelniony_01.svg` i `.png` — podglądy widoków głównych.

Nie odnaleziono projektu Visual Paradigm `.vpp`. JPEG nie zawiera edytowalnych elementów BPMN. Przygotowano nowe pliki BPMN; nie zmieniano projektu użytkownika ani zdjęć. Importu w Visual Paradigm nie przetestowano. Jeśli edytor pokazuje tylko jedną płaszczyznę diagramu, szczegóły można czytać w HTML/SVG.

## Najważniejsze poprawki do screenów

1. W CKAN i XML usunięto sugestię, że stopień jest obliczany synchronicznie w kroku zapisu. Zapis może zlecić przygotowanie po zatwierdzeniu transakcji. Import nie czeka na jego zakończenie.
2. Zastąpiono końcowy ciąg import → publikacja oddzielnym przebiegiem zleceń publikacji. Stan zapisu i sygnały mogą uruchamiać ES/RDF/powiadomienia niezależnie od przygotowania. Nie ma obecnie bramki „ocena co najmniej 2” warunkującej publikację.
3. Wprowadzono warunek uruchomienia przygotowania: zapis nie zawsze je zleca; nowy szkic nie ma standardowego przetwarzania. Sam opis lub format nie gwarantuje nowej oceny.
4. XML: dodano pobranie i rozpoznanie źródła, kopię główną dla pliku, kontrolę pliku i warunkowe dane tabelaryczne. API/WWW może nie mieć kopii. Nie wykluczono kopii i całego przetwarzania tylko na podstawie `remote`.
5. Ręczne dodanie: rozdzielono dwa rzeczywiste entrypointy — URL i zapisany plik z dysku. Upload nie wykonuje zewnętrznego pobrania URL. Nie jest to wybór nowej funkcjonalności; tak działa kod.
6. W XML i ręcznym procesie kwalifikacja tabeli wymaga pliku głównego, odpowiedniego formatu (CSV/TSV/XLS/XLSX/ODS/SHP, także rozpoznane wnętrze) i instytucji innej niż developer.
7. Dodatni wynik `success` z indeksacji zleca konwersje po zatwierdzeniu danych. Nie oznacza braku wszystkich błędnych wierszy (`failed`). Wyjątek przed tym miejscem może przerwać tę ścieżkę.
8. Pierwsza ocena następuje po przewidzianych kontrolach, także po niektórych obsłużonych błędach. Nie ma reguły „każdy błąd pomija ocenę / nadaje 0”. Sam nieobsłużony wyjątek oceny może przerwać zadanie przed nowym zapisem; szczegółowe modele pokazują granice błędów.
9. XML i ręczne konwersje: XLS/XLSX w formacie zasobu lub wnętrza archiwum, brak `linked`, dostępne dane i tabela → CSV UTF-8. Dostępny CSV główny lub pochodny, poza wyłączoną ścieżką CSV w archiwum → próba JSON-LD. Próba JSON-LD nie ma ogólnego warunku `not linked`.
10. Dla XML `linked` oznacza `availability=remote`. Dla ręcznego zasobu oznacza zewnętrzny URL. Dlatego ręczny zewnętrzny XLSX oraz XML remote XLSX nie dostają tej konwersji XLSX → CSV.
11. Zadanie konwersji po powrocie z `increase_openness_score()` zleca paczkę plików zbioru, a następnie — tylko po utworzeniu/odtworzeniu pochodnej — ponownie oblicza ocenę i warunkowo zleca ES/RDF. Wcześniejszy szczegółowy XML miał niedokładną kolejność zlecenia paczki; poprawiono przepływy i grafikę. Nieobsłużony wcześniejszy wyjątek może uniemożliwić zlecenie paczki.
12. Pierwsza ocena nie czeka na konwersje. Nie należy rysować ich jako obowiązkowego odcinka przed pierwszym wynikiem albo przed zakończeniem importu.
13. Odświeżenie po ocenie wymaga odpowiednich wyników przygotowania, a wywołanie aktualizacji ES/RDF dodatkowo stanu opublikowanego, nieusuniętego i nietrwale usuniętego.
14. Paczka plików zbioru jest osobnym zadaniem z kontrolą miejsca na dysku. Nie jest projektowaną flagą archiwum na zasobie. W szczegółowym XML pokazano także zlecenia wynikające z wycofania/przeniesienia.
15. Szczegółowy model ręczny otrzymał rozwiniętą konwersję wspólną z XML zamiast pojedynczego kroku „CSV / JSON-LD”; zawiera też zlecenie paczki zbioru.

## Jak czytać poziomy diagramów

Widoki główne nadal grupują czynności, np. szczegółowe walidacje schematów, operacje publikacji i obsługę wyjątków. Są mapą całego przebiegu od wejścia do zadań w tle. Modele `*_szczegoly.bpmn` rozwijają te obszary: konfigurację, pobieranie, walidację, zapis i sygnały, synchronizację, ocenę formatów, konwersje, publikację i błędy w obrębie istniejących modeli. Nie jest to twierdzenie o odwzorowaniu każdej metody monolitu, wszystkich niezależnych harmonogramów i wszystkich administracyjnych akcji systemu.

W przypadku CKAN brak konwersji oznacza standardową ścieżkę nowego importowanego zasobu. Wspólny entrypoint ma warunki obsługi istniejących plików; nietypowy zasób z wcześniej pozostawionymi plikami wymaga uwzględnienia rzeczywistego stanu.

## Mapa do kodu

Katalog bazowy: `/home/wojtek/ba-code-mapper/source_snapshots/mcod/backend/2.62.3/98b9855d7b47cb8fd8680ab70c6114f138ac46123ea1541fbce2664866f09578-tree/mcod`.

| Obszar | Plik / symbol |
|---|---|
| Termin i aktywność importu | `harvester/tasks.py`: `harvester_supervisor`, `import_data_task`; `harvester/models.py`: `import_needed`, `import_data` |
| Przyjęcie i zapis importu | `harvester/models.py`: `update_from_items`, `_update_or_create_resource`, `delete_stale_resources`; `harvester/serializers.py` |
| Zapis panelu | `resources/admin.py`: `ResourceAdmin.save_model`; `resources/forms.py` |
| Sygnały i kwalifikacja do przetwarzania | `resources/models.py`: `SIGNALS_MAP`, `process_resource`, `process_created_file`, `is_link_updated`, `is_data_processable`, `is_linked` |
| Przygotowanie URL i CKAN | `resources/tasks/entrypoint_res.py`; `resources/tasks/process_resource_from_url.py`: `is_imported_from_ckan` |
| Przygotowanie uploadu | `resources/tasks/entrypoint_res_file.py`; `resources/tasks/process_resource_file.py` |
| Indeksacja i zlecenie konwersji | `resources/tasks/process_resource_file_data.py`: `process_resource_file_data_task` |
| Warunki konwersji | `resources/models.py`: `increase_openness_score`, `get_csv_file_internal_url`, `convert_csv_to_jsonld` |
| Druga ocena i paczka | `resources/tasks/process_resource_file_data.py`: `increase_openness_score_task` |
| Obliczenie stopnia | `resources/models.py`: `get_openness_score`; `resources/tasks/common.py`: `update_resource_openness_score`; `resources/score_computation/score_calculation.py` |
| Odświeżenie publikacji | `resources/models.py`: `needs_es_and_rdf_db_update`, `update_es_and_rdf_db` |
| Paczka ZIP zbioru | `datasets/models.py`: `archive_files`; `datasets/tasks.py`: `archive_resources_files` |

## Weryfikacja i ograniczenia

Walidacja struktury XML i identyfikatorów, referencji BPMN, spójności incoming/outgoing, granic procesów i osiągalności węzłów widoków głównych oraz kontrola reguł konwersji. Wynik w `KONTROLA.json`. Podglądy SVG/PNG sprawdzono wizualnie. Nie uruchamiano aplikacji, parserów danych ani usług konwersji; nie wykonano testu produkcji ani importu Visual Paradigm. Część szczegółowych reguł pochodzi z wcześniejszych opracowań; ponownie czytane źródła i ich sumy kontrolne są w `ZRODLA.json`.

Materiały pozostają lokalne. Nie wykonano commita, push ani publikacji.
