# Gothic II: Przeznaczenie — Epilog · wiki

Polska solucja do Epilogu: 51 zadań, wskazówki, spis postaci i mapy. [O modyfikacji na Sefaris](https://www.sefaris.eu/przeznaczenie-epilog).

## Jak edytować wiki

Drobne poprawki możesz zgłosić bezpośrednio w przeglądarce:

1. Na podstronie wiki kliknij **Materiał źródłowy**. Otworzy się plik tej strony na GitHubie.
2. Zaloguj się na GitHubie i kliknij **ikonę ołówka**. Jeśli GitHub poprosi o utworzenie forka, utwórz własną kopię repozytorium.
3. Popraw treść i zapisz zmiany z krótkim opisem na osobnej gałęzi.
4. Utwórz **Pull Request** do repozytorium wiki. Napisz, co zmieniasz i dlaczego; opiekunowie sprawdzą zgłoszenie.

Zachowuj układ dokumentu i identyfikatory nagłówków, np. `{#nazwa-zadania}`, aby linki do zadań nadal działały.

Błąd lub brakującą informację możesz też zgłosić na [Discordzie Sefaris](https://discord.gg/9EVFJv5Uyf).

## Praca lokalna

Wymagane: Node.js 24 i pnpm 11.19.0. Pobierz własnego forka i w jego katalogu uruchom:

```sh
pnpm install --frozen-lockfile
pnpm start
```

Podgląd: [localhost:3013](http://localhost:3013). Zmiany w dokumentach są widoczne po zapisaniu pliku. Przed wysłaniem Pull Requesta uruchom:

```sh
pnpm check
```

Polecenie buduje wiki oraz sprawdza odnośniki, zasoby i indeks wyszukiwania.

## Gdzie wprowadzać zmiany

- `docs/` — treść stron. Zwykły tekst zapisuj w `.md`, a strony z komponentami, np. zakładkami lub filmami, w `.mdx`.
- `static/img/` — lokalne ilustracje oraz tło nagłówka.
- `sidebars.js` — układ menu. Dodając stronę, wzoruj się na sąsiednim dokumencie i dodaj ją do odpowiedniego działu.
- `site-profile.js` — dane modyfikacji i adresy wiki.
- `src/css/custom.css` — wspólny wygląd strony.

Zachowuj metadane na początku dokumentów, kotwice, warianty zadań i odnośniki do lokalnych ilustracji. Ostrzeżenia zapisuj jako `:::warning Uwaga`, porady jako `:::tip Wskazówka`, a dodatkowe informacje jako `:::info Informacja`. Zostaw puste wiersze po tytule ramki i przed zamykającym `:::`.

## Autorzy


**Polska solucja:** Codex (OpenAI) — tłumaczenie i opracowanie.

**Materiał bazowy:** niemiecka solucja, aktualizacja Lito z 15.07.2023.

**Twórcy modyfikacji:** [Drużyna Spolszczenia Destiny Team](https://www.sefaris.eu/przeznaczenie-epilog/contributors).

Motyw pochodzi ze wspólnego wzoru wiki Sefaris. Ikona Discorda pochodzi z Simple Icons (CC0), pozostałe ikony z Lucide.
