# UML — maszyna stanów oceny otwartości

Diagram zastępuje wcześniejszy schemat przepływu formalną notacją maszyny stanów UML.

- OcenaZapisana jest stanem złożonym z sześcioma alternatywnymi podstanami: Ocena 0–5.
- Przejście ze stanu złożonego oznacza możliwość uruchomienia przeliczenia z dowolnej dotychczasowej oceny. Nie ma ograniczenia przejść wyłącznie do wyższych wartości.
- PonowneObliczanie i ZapisywanieOceny opisują etapy pracy. Nie są nowymi wartościami statusu publikacji w bazie.
- Romb jest pseudostanem wyboru. Warunki [wynik = 0] ... [wynik = 5] są rozłączne i obejmują wszystkie prawidłowe wyniki.
- H jest historią płytką stanu złożonego: błąd obliczenia przed UPDATE prowadzi do ostatniej oceny, a nie automatycznie do zera.
- Błąd zapisu prowadzi do stanu niepotwierdzonego. Po sprawdzeniu bazy odczytana wartość określa odpowiedni podstan oceny. Nie zakładamy atomowości całego zapisu ocen plików i zasobu.
- To diagram częściowy dla istniejącego zasobu. Celowo nie narzuca domyślnego wejścia do Ocena 0; stan wejściowy wynika z bazy. Historia H ma już poprzedni podstan, ponieważ model obejmuje istniejącą ocenę.
- Status publikacji pozostaje niezależny: samo przeliczenie i zapis 0 nie ustawia draft ani flag usunięcia.
- Diagram opisuje pojedynczy przebieg przeliczenia. Nie jest analizą możliwych wyścigów kilku zadań działających równocześnie.

Pliki:

- stopnie_otwartosci_UML.png — obraz do prezentacji.
- stopnie_otwartosci_UML.pdf — wektorowa wersja do udostępnienia.
- stopnie_otwartosci_UML.svg — wektorowy diagram z ręcznie przygotowanym układem UML.
- stopnie_otwartosci_UML.puml — edytowalny zapis struktury i przejść PlantUML; automatyczny układ w PlantUML może różnić się od przygotowanego obrazu.

Podstawa: przeanalizowany wcześniej lokalny snapshot mcod 2.62.3; szczegółowe reguły i identyfikatory źródeł znajdują się w ../../algorytm_otwartosci_wspolny/README.md i ../../algorytm_otwartosci_wspolny/ZRODLA.json.

Weryfikacja: podgląd wizualny PNG, poprawność XML SVG, nagłówki PNG i PDF oraz zgodność listy sześciu warunków przejść. Nie testowano renderowania pliku PUML w zewnętrznym edytorze.
