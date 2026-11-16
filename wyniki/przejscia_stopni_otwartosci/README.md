# Przejścia między stopniami otwartości

Diagram pokazuje zmianę oceny istniejącego zasobu. Nie jest diagramem statusów publikacji ani specyfikacją wykonywalnego workflow.

- Punktem wyjścia jest dowolna dotychczasowa ocena 0–5.
- Przeliczenie wymaga wyzwalacza. Nowy wynik nie ma ograniczenia względem poprzedniego: możliwe są wzrost, spadek i brak zmiany. Nie znaczy to, że dowolny format może dostać dowolną ocenę — nadal obowiązują reguły kalkulatora.
- Błąd obliczenia przed UPDATE pozostawia poprzednią ocenę. Błąd podczas zapisu wymaga osobnego ustalenia stanu bazy; nie obiecujemy rollbacku.
- 0 to wynik oznaczający brak stopnia 1–5. Nie jest statusem szkicu, kosza ani błędu zadania.
- Zmiana oceny sama nie zmienia statusu publikacji. Zapis w bazie i odświeżenie informacji na portalu są osobnymi etapami.
- Przykład 5 → 1 wymaga, żeby w ścieżce plików nie pozostał żaden plik o wyższej ocenie. Przykład 5 → 0 z formatem None zakłada, że rzeczywiście uruchomiono nowe przeliczenie; sama zmiana formatu nie zawsze je wyzwala.
- „Zmiana reguł tabeli” oznacza zmianę schematu danych tabelarycznych lub znaków umownych w panelu opublikowanego zasobu, wywołującą rewalidację.
- Kwalifikujący harmonogram: włączona automatyczna data danych, która dla zewnętrznego zasobu plikowego uruchamia pełne przygotowanie. Nie jest to ogólny cykliczny audyt ocen wszystkich zasobów.

Podstawa: lokalny snapshot mcod 2.62.3 analizowany we wcześniejszym opracowaniu. Szczegółowe reguły i źródła: ../algorytm_otwartosci_wspolny/PREZENTACJA.html oraz ZRODLA.json w tym katalogu. Brak ponownego testu bieżącej produkcji.

Pliki: SVG (wektorowy diagram), PNG (obraz do prezentacji), PDF (wektorowa wersja do udostępnienia), MMD (edytowalne uproszczone źródło Mermaid).
