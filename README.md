# Przeznaczenie — Epilog · polska wiki

Polska wiki dla **Przeznaczenia — Epilogu**, przygotowana na wspólnym szablonie Docusaurusa używanym przez wiki Sefaris. Przeniesiono całą dostarczoną niemiecką solucję: **51 zadań, 410 wpisów o postaciach, wskazówki i 3 mapy**. Nazwy oraz odpowiedzi dialogowe dopasowano do polskich tekstów gry. Strona jest gotowa do lokalnego przeglądania; przebieg zadań wymaga jeszcze pełnej weryfikacji w grze.

Repozytorium: [Sefaris/przeznaczenie-epilog-pl-wiki](https://github.com/Sefaris/przeznaczenie-epilog-pl-wiki). Stan przygotowania: **20 września 2026 r.**

## Cała Saga Przeznaczenie

Pracujemy docelowo nad polskimi solucjami do całej sagi, w kolejności:

**Przeznaczenie → Epilog → Przebudzenie → Korzenie Zła → Imperium Popiołów.**

| Część | Strona na Sefaris | Stan prac w tym katalogu |
| --- | --- | --- |
| Przeznaczenie | [Przeznaczenie](https://www.sefaris.eu/przeznaczenie) | Ma już osobne repozytorium `przeznaczenie-pl-wiki`. |
| Epilog | [Przeznaczenie Epilog](https://www.sefaris.eu/przeznaczenie-epilog) | Cała dostarczona solucja opracowana po polsku; lokalna wiki i indeks DE/PL. |
| Przebudzenie | [Przebudzenie — Saga Przeznaczenie](https://www.sefaris.eu/przebudzenie-destiny) | Kolejny etap. |
| Korzenie Zła | [Korzenie Zła](https://www.sefaris.eu/korzenie-zla) | Kolejny etap. |
| Imperium Popiołów | [Imperium Popiołów](https://www.sefaris.eu/imperium-popiolow) | Kolejny etap. |

Nazwy i odsyłacze sprawdzono na Sefaris. W katalogu modyfikacji można wyszukiwać słowo **Saga**. Właściwe Przebudzenie ma adres `przebudzenie-destiny` — na stronie jest też inny mod o nazwie Przebudzenie.

To repozytorium dotyczy wyłącznie Epilogu. Nie przenosimy do niego zadań, nazw ani mechanik innych części bez potwierdzenia w materiałach Epilogu. Wspólne zasady opracowania poniżej stosujemy również przy kolejnych częściach.

## Jak będziemy przygotowywać polską solucję

Właściciel będzie dostarczać **niemieckie skrypty**, **polskie skrypty lub teksty z gry** oraz **niemiecką solucję**. Materiały mogą przychodzić partiami. Pierwsza partia w `epilog_pliki` zawiera dwa eksporty tekstów CSV i solucję Markdown. Narzędzie połączyło 23 682 pary DE/PL i przygotowało mapowania nazw. Instrukcję importu, wyszukiwania i użycia dla kolejnych modów opisuje [materialy/README.md](materialy/README.md); pochodzenie i zakres danych zapisano w [rejestrze źródeł](materialy/zrodla.md).

1. **Rozpoznanie materiałów.** Zapisujemy część sagi, wersję gry/modyfikacji, język, pochodzenie i autorów. Zachowujemy oryginały bez zmian; tekst po ekstrakcji trzymamy osobno. Sprawdzamy kodowanie i polskie znaki.
2. **Powiązanie wersji DE i PL.** Dopasowujemy zadania, postacie, lokacje, przedmioty, dialogi i wpisy dziennika. Jeśli są dostępne, podstawą dopasowania są identyfikatory skryptowe, instancje i kontekst dialogu. Samo podobieństwo nazw nie wystarcza.
3. **Polskie nazewnictwo.** Nazwy widoczne w polskich skryptach lub tekstach z gry mają pierwszeństwo przed własnym tłumaczeniem z niemieckiego. Budujemy słownik DE → PL wraz ze wskazaniem źródła. Brak dopasowania zapisujemy do wyjaśnienia, zamiast wymyślać nazwę.
4. **Opracowanie solucji.** Niemiecka solucja jest podstawą opisu przejścia. Przepisujemy ją naturalną polszczyzną, z nazwami zgodnymi z polską grą, zachowując kolejność działań, warunki, wybory, konsekwencje, nagrody i ostrzeżenia. Nie skracamy informacji potrzebnych do ukończenia zadania.
5. **Weryfikacja w skryptach.** Sprawdzamy dostępne warunki rozpoczęcia i zakończenia, zależności, wymagane przedmioty, etapy oraz nagrody. Rozbieżności między niemiecką solucją a polską wersją zapisujemy ze źródłami. Zwykłe teksty lub dialogi nie potwierdzają całej logiki skryptów; przy braku kodu pozostawiamy odpowiednią informację niezweryfikowaną.
6. **Dodawanie do wiki partiami.** Publikowane opisy trafiają do `docs/`, a robocze zestawienia i pytania pozostają w `materialy/`. Epilog ma zadania alfabetycznie według polskich tytułów, osobne wskazówki i spis postaci w dziewięciu obszarach. Każdy opis ma stałą kotwicę i wskazanie źródeł w notatkach roboczych.
7. **Kontrola.** Sprawdzamy kompletność względem otrzymanej partii, spójność nazw, odnośniki, warianty oraz build. Weryfikację ze skryptami i sprawdzenie w samej grze odnotowujemy osobno — jedno nie oznacza drugiego.

Nie dopisujemy z pamięci brakujących zadań, dialogów, nagród ani warunków. Nie mieszamy wersji moda; niejasności i sprzeczności pozostają jawnie zapisane do rozstrzygnięcia. Oddzielamy autorstwo oryginału od polskiego opracowania.

Zakres migracji i decyzje o nazewnictwie opisuje [materialy/opracowanie.md](materialy/opracowanie.md). [materialy/migracja.json](materialy/migracja.json) wiąże wszystkie 51 zadań z kotwicami, 410 wpisów NPC z wierszami źródła oraz 3 mapy z sumami SHA-256. To rejestr przeniesionej partii, nie dowód przetestowania mechanik gry.

## Praca lokalna

Wymagane: **Node.js 24** i **pnpm 11.19.0**, zgodnie ze wspólnym szablonem wiki Sefaris. Polecenia uruchamiaj w głównym katalogu tego repozytorium:

```sh
pnpm install --frozen-lockfile
pnpm start
```

Podgląd: [localhost:3013](http://localhost:3013). Przed zakończeniem zmian uruchom:

```sh
pnpm check
```

Polecenie wykonuje istniejące testy spisu treści, buduje stronę i sprawdza lokalne odnośniki, zasoby, linki do plików źródłowych oraz indeks wyszukiwania. Nie potwierdza poprawności solucji w grze ani dostępności zewnętrznych stron.

Gotowy build można obejrzeć przez `pnpm serve`, również na porcie 3013. Zatrzymaj wcześniej serwer deweloperski, jeśli korzysta z tego portu.

## Struktura repozytorium

| Miejsce | Przeznaczenie |
| --- | --- |
| `docs/README.mdx` | Strona główna, odsyłacze do działów, autorzy i instrukcja edycji. |
| `docs/solucja/zadania.mdx` | 51 zadań, wzajemne odsyłacze, ostrzeżenia i 3 powiększane mapy. |
| `docs/poradnik/` | Wskazówki i 410 wpisów o postaciach w dziewięciu obszarach. |
| `materialy/` | Materiały wejściowe, słownik DE → PL, źródła ustaleń i notatki. Poza publikowaną stroną. |
| `sidebars.js` | Menu: strona główna, solucja, informacje dodatkowe. |
| `site-profile.js` | Nazwa Epilogu, adresy Sefaris, repozytorium i lokalny adres podglądu. |
| `static/img/` | Favicon, grafika Epilogu z Sefaris w nagłówku i trzy mapy z solucji. |
| `src/`, `plugins/` | Wspólny motyw i wyszukiwanie Sefaris. |
| `scripts/`, `.github/workflows/check.yml` | Kontrola projektu i build w CI. |

Do analizy tekstów służy `scripts/text_tools.py` (Python 3.10+, bez dodatkowych bibliotek). `pnpm texts:build` odtwarza indeks, `pnpm texts:search "nazwa"` wyszukuje pary DE/PL, a `pnpm texts:section "tytuł"` wyświetla fragment solucji. Testy narzędzia: `pnpm test:texts`. Wyniki robocze w `materialy/generated/` nie trafiają do Git ani na stronę wiki.

Ostrzeżenia zapisujemy jako `:::warning Uwaga`, porady jako `:::tip Wskazówka`, a dodatkowe informacje jako `:::info Informacja`. Zostawiamy puste wiersze po tytule ramki i przed zamykającym `:::`. Zachowujemy jawne kotwice nagłówków i odsyłacze między zadaniami. Menu ma kolejność: strona główna, solucja i jej wątki, na końcu informacje dodatkowe; bez pustych kategorii.

## Jak edytować wiki

Drobne poprawki możesz zgłosić bezpośrednio w przeglądarce:

1. Na podstronie wiki kliknij **Materiał źródłowy**. Otworzy się plik tej strony na GitHubie.
2. Zaloguj się na GitHubie i kliknij **ikonę ołówka**. Jeśli GitHub poprosi o utworzenie forka, utwórz własną kopię repozytorium.
3. Popraw treść i zapisz zmiany z krótkim opisem na osobnej gałęzi.
4. Utwórz **Pull Request** do repozytorium wiki. Napisz, co zmieniasz i dlaczego; opiekunowie sprawdzą zgłoszenie.

Zachowuj układ dokumentu i identyfikatory nagłówków, np. `{#nazwa-zadania}`, aby linki do zadań nadal działały.

Błąd lub brakującą informację możesz też zgłosić na [Discordzie Sefaris](https://discord.gg/9EVFJv5Uyf).

## Publikacja

Na tym etapie przygotowujemy wiki lokalnie. `site-profile.js` wskazuje `http://localhost:3013`; docelowa domena nie została jeszcze ustalona, więc nie dodano `CNAME` ani workflow publikacji. Workflow `check.yml` sprawdza wszystkie pushe i Pull Requesty.

Przed uruchomieniem GitHub Pages należy ustalić domenę, zmienić `url` w profilu, dodać zgodny `static/CNAME`, potwierdzić domyślną gałąź (lokalnie `main`) oraz przenieść workflow publikacji ze wspólnego wzoru Sefaris. Skrypt `verify-deployment.cjs` sprawdza domenę i gałąź. Git i publikację wykonuje właściciel.

## Autorzy

**Polska solucja:** Codex (OpenAI) — tłumaczenie i opracowanie.

**Materiał bazowy:** niemiecka solucja, aktualizacja Lito z 15.07.2023.

**Twórcy modyfikacji:** [Drużyna Spolszczenia Destiny Team](https://www.sefaris.eu/przeznaczenie-epilog/contributors).

Motyw pochodzi ze wspólnego wzoru wiki Sefaris. Ikona Discorda pochodzi z Simple Icons (CC0), pozostałe ikony z Lucide.
