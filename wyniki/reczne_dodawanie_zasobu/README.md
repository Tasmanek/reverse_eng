# Ręczne dodawanie zasobu — proces dla biznesu

Model pokazuje ręczne dodanie nowego zasobu w panelu administracyjnym, na podstawie lokalnego kodu mcod 2.62.3. Nie jest modelem importu XML ani CKAN. Nie uruchamiano aplikacji ani testu przeglądarkowego.

## Jak czytać diagram

1. Edytor wskazuje **„plik z dysku lub URL”**, uzupełnia pozostałe pola oraz status i klika **„Zapisz”**. Zgodnie z wymaganiem nie ma bramki wyboru pliku lub URL.
2. Portal sprawdza formularz. Błędy pól wymagają poprawy; poprawny formularz pozwala zapisać zasób.
3. Dla nowego opublikowanego zasobu zapis zleca przetwarzanie **po zatwierdzeniu transakcji**. Zapis formularza kończy się bez czekania na walidację i ocenę. Nowy szkic nie uruchamia tego samego przebiegu; pierwsza publikacja może go uruchomić później.
4. Osobna pula pokazuje przygotowanie zasobu: kontrolę adresu, kontrolę pliku, warunkową kontrolę danych i nadanie stopnia otwartości.
5. **Pomarańczowy podproces „NADAJ STOPIEŃ OTWARTOŚCI” to miejsce pierwszego obliczenia i zapisu oceny.** Jego wnętrze oraz kalkulatory mają własne diagramy.
6. Po udanej indeksacji danych system może zlecić osobne zadanie tworzenia plików pochodnych. Jeżeli nowy plik powstanie, następuje **ponowne obliczenie oceny** — drugi pomarańczowy krok.

Pule oznaczają odrębne przebiegi pracy. Linie przerywane między nimi są przepływami komunikatów i oznaczają zlecenie pracy, bez oczekiwania na jej zakończenie. Linie ciągłe opisują kolejność wewnątrz procesu.

## Co jest sprawdzane

| Etap | Znaczenie biznesowe | Przykładowe kontrole |
|---|---|---|
| Formularz przed zapisem | Czy da się przyjąć opis i wskazane źródło? | Wymagane pola i reguły metadanych; dla URL wymagany HTTPS; dla pliku obsługiwane rozszerzenie i zakaz archiwum chronionego hasłem. Szczególne reguły zależą m.in. od flag DGA/HVD. |
| Adres / pobranie | Czy dane pod podanym URL są dostępne i jaki mają typ? | Poprawność URL, HTTPS po przekierowaniu, HTTP 200, Content-Type, rozpoznanie pliku/API/WWW i formatu; dla pliku zapis kopii głównej. |
| Plik | Czy zapisany plik ma rozpoznawalny i obsługiwany format? | Analiza pliku, MIME, kodowania i zawartości archiwum; kontrola obsługi formatu; nieznane kodowanie CSV może dać błąd. Nie jest to uniwersalny skan antywirusowy ani audyt prawdziwości danych. |
| Dane tabelaryczne | Czy można odczytać dane zgodnie ze schematem i udostępnić ich wiersze? | Ustalenie schematu, walidacja danych, indeksowanie wierszy. Warunki wejścia: plik główny; format CSV/TSV/XLS/XLSX/ODS/SHP, także w obsługiwanym archiwum; instytucja inna niż developer. |
| Stopień otwartości | W jakiej postaci dane są udostępniane? | Brak formatu zasobu → 0; pliki → maksimum ich ocen; brak pliku głównego i istniejący link → ocena treści linku. Kalkulatory JSON/XML/RDF oraz tabela pozostałych formatów. |

**Nie każdemu zasobowi towarzyszą wszystkie kontrole.** URL rozpoznany jako API lub WWW bez pliku głównego nie przechodzi kontroli lokalnego pliku i tabeli. PDF może przejść kontrolę pliku, ale nie kwalifikować się do przetwarzania danych tabelarycznych.

## Plik z dysku a URL — różnica bez osobnej bramki wyboru

- **Plik z dysku:** formularz zapisuje plik główny; jego utworzenie dla opublikowanego zasobu zleca zadanie kontroli pliku. Nie wykonuje się pobrania HTTP z zewnętrznego serwera. Kontrola ustawia format i wewnętrzny link zasobu; po przewidzianych etapach może też zapisać status linku SUCCESS bez zewnętrznego żądania HTTP.
- **URL:** zapis zasobu zleca zadanie przygotowania adresu. Najpierw sprawdzany i pobierany jest URL, potem odpowiednio plik i dane. W przypadku API/WWW może nie być pliku głównego.

Na diagramie oba warianty połączono w jeden przebieg biznesowy; podpis „jeżeli podano URL” oznacza etap warunkowy, a nie dodatkową kontrolę HTTP pliku z dysku. Kod używa dwóch różnych entrypointów zadań.

## Ocena nie jest potwierdzeniem poprawności danych

W obu entrypointach próba obliczenia oceny znajduje się po przewidzianych kontrolach i nie jest bezwarunkowo pomijana po ich błędzie. Dlatego ścieżki pominięcia lub niepowodzenia kontroli prowadzą do podprocesu oceny dostępnego stanu. Wyjątek samego obliczania może przerwać zadanie; nie zakładamy, że każdy błąd daje 0 lub że zawsze powstanie nowa ocena.

Ocena i data mogą zostać zapisane przed decyzją o końcowym odświeżeniu publikacji. Dla URL kod wymaga sukcesu etapu URL, wymaganej kontroli pliku i braku odroczonych wyjątków; dla pliku z dysku sukcesu kontroli pliku i braku odroczonych wyjątków. Wywołanie aktualizacji opisów dodatkowo wymaga zasobu nadal opublikowanego i nieusuniętego. Sam wynik walidacji nie stanowi automatycznego cofnięcia zapisu ani zmiany statusu na szkic.

Bramka „Zindeksowano dane?” odpowiada warunkowi `if success` w kodzie. Nie oznacza gwarancji zindeksowania każdego wiersza bez błędu: wynik zawiera również `failed`.

## Konwersje

- XLS/XLSX → CSV: dostępne dane tabeli i zasób **nie jest linked**. Dla ręcznego dodania link zewnętrzny oznacza linked; plik z dysku z linkiem wewnętrznym może kwalifikować się do konwersji.
- CSV → JSON-LD: dostępny CSV główny lub pochodny poza archiwum; jest to próba, której powodzenie zależy od danych i usług.
- Nowy plik pochodny → przeliczenie maksimum ocen plików → warunkowe odświeżenie publikacji.

Pierwsze obliczenie nie czeka na konwersje; nie ma gwarantowanej kolejności ukończenia obu zadań. Dodatkowa obsługa archiwum zbioru, powiadomień i automatycznej daty danych została pominięta na widoku biznesowym, bo nie jest przedmiotem tego diagramu.

## Źródła kodowe

Snapshot: `/home/wojtek/ba-code-mapper/source_snapshots/mcod/backend/2.62.3/98b9855d7b47cb8fd8680ab70c6114f138ac46123ea1541fbce2664866f09578-tree/mcod/`.

| Obszar | Plik / symbol |
|---|---|
| Formularz: plik lub URL | `resources/forms.py:632` — LinkOrFileUploadForm; `:657` — AddResourceForm; clean_link, clean_file |
| Zapis zasobu i pliku | `resources/admin.py:880` — ResourceAdmin.save_model |
| Zlecenie dla URL | `resources/models.py:1937` — process_resource |
| Zlecenie dla nowego pliku | `resources/models.py:2012` — process_created_file |
| Kolejność etapów URL | `resources/tasks/entrypoint_res.py:81` |
| Kolejność etapów pliku z dysku | `resources/tasks/entrypoint_res_file.py:75` |
| Walidacja adresu i pobranie | `resources/link_validation.py:73`; `resources/tasks/process_resource_from_url.py:26` |
| Walidacja pliku | `resources/tasks/process_resource_file.py:33` |
| Kwalifikacja danych tabelarycznych | `resources/models.py:611` — is_data_processable |
| Walidacja, indeksacja i zlecenie konwersji | `resources/tasks/process_resource_file_data.py:75` — process_resource_file_data_task |
| Obliczenie i zapis oceny | `resources/models.py:1046` — get_openness_score; `resources/tasks/common.py:97` — update_resource_openness_score |
| Konwersje i ponowna ocena | `resources/models.py:914` — increase_openness_score; `resources/tasks/process_resource_file_data.py:45` |

Wcześniejszy raport harvestera jest materiałem uzupełniającym. Ten model dodatkowo weryfikuje ścieżkę ręcznego dodawania bezpośrednio w lokalnym kodzie. Nie potwierdza bieżącej produkcji.

## Pliki

- `reczne_dodawanie_zasobu.bpmn` — edytowalny BPMN z widokiem głównym, podprocesami i układem graficznym; kolory wyróżniają ocenę.
- `reczne_dodawanie_zasobu.png` — obraz do prezentacji.
- `reczne_dodawanie_zasobu.svg` — podgląd wektorowy, który można powiększać.
- `PREZENTACJA.html` — opis i wszystkie szczegółowe podglądy.

Model BPMN jest niewykonywalny. Podprocesy ze znakiem „+” mają osobne płaszczyzny diagramu. Nie testowano importu w konkretnym edytorze; sprawdzono XML, połączenia, granice procesów, osiągalność węzłów, kompletność grafiki oraz podgląd wizualny.
