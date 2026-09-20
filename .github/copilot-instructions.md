# Edycja wiki

## Zakres bieżącego etapu — Epilog

README ma standardowy układ pozostałych wiki: opis, edycja, uruchamianie, pliki i autorzy. Nie dodawaj do niego planu całej sagi ani ustaleń dotyczących przyszłej współpracy. Lokalny plan jest poza repozytorium, w `../SAGA_PRZEZNACZENIE.md` w katalogu projektu `wikis`; nie kopiuj go do plików przeznaczonych do pushu. Organizacja źródeł i narzędzia są w `materialy/README.md`. Dostarczono `../epilog_pliki`: eksporty tekstów DE/PL i niemiecką solucję, bez pełnej logiki skryptów. Przeniesiono całą tę partię: 51 zadań, wskazówki, 410 wpisów o postaciach i 3 mapy. Rejestr pochodzenia jest w `materialy/migracja.json`, decyzje redakcyjne w `materialy/opracowanie.md`. Nie dodawaj przykładowych zadań ani treści innych części sagi. Polskie skrypty/teksty są źródłem nazw, niemiecka solucja podstawą opisu przejścia, a pełne skrypty (gdy będą dostępne) służą weryfikacji logiki. Braki i rozbieżności zapisuj w notatkach roboczych; nie zgaduj.

Do wyszukiwania używaj `python scripts/text_tools.py search` i `section`; po zmianie źródeł wykonaj `build`. Konfiguracja to `materialy/epilog.json`. Czytaj DE z niemieckiego eksportu i PL z polskiego; druga kolumna językowa może zawierać kopię z uszkodzonym kodowaniem. Łącz po `ID + SYMBOL + USE + TRACE`, nie po kolejności, samym ID ani samej nazwie. Statusy `review`/`context_review` i powtarzające się nazwy wymagają sprawdzenia. Nie poprawiaj ręcznie `materialy/generated/`, bo wyniki są odtwarzane. Po zmianie narzędzia uruchom również `pnpm test:texts`.

Domena publikacji to `https://przeznaczenie-epilog.mody.sefaris.eu`; utrzymuj zgodność `site-profile.js` i `static/CNAME`. Lokalny podgląd używa portu 3013. Workflow `pages.yml` po pushu na domyślną gałąź lub ręcznym uruchomieniu z tej gałęzi sprawdza profil, wykonuje `pnpm test:texts` i `pnpm check`, a następnie publikuje katalog `build/` na GitHub Pages. Pozostałe gałęzie i Pull Requesty sprawdza `check.yml` bez wdrożenia. Źródłem publikacji w ustawieniach Pages musi być GitHub Actions.

## Publiczny tekst i autorstwo

Zgodnie z decyzją właściciela polska solucja jest podpisana: **Codex (OpenAI) — tłumaczenie i opracowanie**. Zachowuj ten podpis na stronie głównej i w README, obok odrębnej informacji o materiale bazowym (aktualizacja Lito z 15.07.2023) i twórcach moda.

Strony `docs/` są gotowym poradnikiem dla graczy. Nie dodawaj uwag o tłumaczeniu, imporcie, brakujących skryptach, nieprzeprowadzonych testach ani sformułowań „według oryginału”, „autor solucji podaje”, „tak zapisano w źródle”. Pochodzenie, uzasadnienia, ograniczenia i kwestie do sprawdzenia dokumentuj w `materialy/`. W solucji zachowuj praktyczne ostrzeżenia i warunki, opisane bezpośrednio. Nie zamieniaj brakującej informacji w wymyślony fakt ani nie deklaruj przeprowadzenia testów w grze. Nagłówek korzysta z lokalnej kopii grafiki Epilogu z Sefaris: `static/img/epilog-background.webp`.

## Zasady wspólne

Zachowuj treść, autorów na stronie głównej i jawne kotwice zadań. Zwykłe dokumenty zapisuj w `.md`, komponenty w `.mdx`. Przed zakończeniem uruchom `pnpm check`. Git i publikację wykonuje właściciel.

## Wspólny układ menu i wyróżnień

- Menu: Strona główna, Solucja i pozostałe działy z zadaniami, na końcu Informacje dodatkowe (konfiguracja, porady, teleporty, mapy i spisy). Nie twórz pustej kategorii i zachowuj rozwijane lokacje rozdziałów.
- Ostrzeżenia: `:::warning Uwaga`; porady: `:::tip Wskazówka`; warunki i fakty: `:::info Informacja`. Dobieraj rodzaj po znaczeniu, nie tylko po dawnej etykiecie. Krytyczną blokadę gry można oznaczyć `:::danger Uwaga`.
- Po otwarciu i przed zamknięciem ramki `:::` zostaw pusty wiersz. Nie powtarzaj tytułu jako „UWAGA:” w treści. Zachowuj listy, warianty, liczby i powiązane media; nie obejmuj uwagą dalszego opisu zadania.
- Cytaty `>` służą autentycznym wypowiedziom lub listom z gry. Nie używaj ich do wyróżniania instrukcji autora, nagród ani opisów strony. Ramki działają również w zwykłych `.md` i nie wymagają MDX.
- README repozytorium i strona główna używają wspólnej sekcji „Jak edytować wiki” z bazy. Instrukcja edycji jest jednakowa we wszystkich wiki; nazwa, adres, materiały i autorzy dotyczą danego moda. Zachowuj zgodne osoby i role w obu sekcjach „Autorzy”; nie kopiuj autorstwa z przykładowego NB.
- Nagłówek strony głównej pokazuje heroDescription z site-profile.js: jedno zdanie o fabule lub charakterze danego moda na podstawie jego opisu na Sefaris. Zachowuj wspólny komponent HomeHeader i styl opisu; nie przenoś opisu innego moda ani autorstwa do nagłówka.

- Spis „Na tej stronie” używa wspólnego `src/theme/TOCItems/`: po dojściu do końca przewijanej strony zaznacza ostatnią sekcję, a przy przewijaniu w górę wraca do pozycji czytania. Zachowuj identyczny mechanizm w bazie i wiki; test regresji jest częścią `pnpm check`.
