# rtbolidozor_tools

Nástroje pro ruční správu indexace a detekce multibolidů.

## Automatické zpracování (django-Q)

Následující tasky běží automaticky přes django-Q worker (`django_q` kontejner):

| Task | Interval | Popis |
|------|----------|-------|
| `tasks.file_index` | každých 15 min | Indexace nových souborů ze /storage do DB (posledních 2 hodiny) |
| `tasks.run_meteor_clusterer` | každých 15 min | Hledání multibolid shluků za posledních 30 dní |
| `tasks.updateStationStatus` | každou hodinu | Aktualizace stavu stanic |

---

## Ruční zpracování historických dat

Pokud potřebuješ zpracovat historická data (např. po výpadku nebo zpětně),
spusť oba kroky v pořadí: nejprve indexaci, pak hledání multibolidů.

### 1. Indexace souborů do DB

```bash
./reindex_history.sh YYYY-MM-DD [YYYY-MM-DD]
```

- První parametr: datum od (povinný)
- Druhý parametr: datum do (volitelný, výchozí = dnes)

Příklady:
```bash
# Od února 2026 do dnes
./reindex_history.sh 2026-02-01

# Konkrétní rozsah
./reindex_history.sh 2026-02-01 2026-04-30
```

Pro dlouhé období doporučujeme spustit ve screenu:
```bash
screen -dmS reindex bash -c './reindex_history.sh 2026-02-01 2>&1 | tee /tmp/reindex.log'
# Sledování průběhu:
tail -f /tmp/reindex.log
```

### 2. Hledání multibolidů

```bash
./run_multibolid_history.sh YYYY-MM-DD [YYYY-MM-DD]
```

Stejné parametry jako reindex_history.sh. Spouštět až po dokončení indexace.

Příklady:
```bash
./run_multibolid_history.sh 2026-02-01
./run_multibolid_history.sh 2026-02-01 2026-04-30
```

---

## Ostatní skripty

| Soubor | Popis |
|--------|-------|
| `find_multibolid.py` | Vstupní bod pro MeteorClusterer (výchozí rozsah 30 dní) |
| `index_bh.py` | Jednorázová indexace pevně daného rozsahu |
| `file_structure_to_db.py` | Import struktury souborů do DB |
| `all_stations_to_retaired.py` | Přesun všech stanic do stavu retired |
| `backfill_duration.py` | Doplní chybějící `duration` u eventů z meta.csv souborů |

---

## Doplnění chybějící délky trvání (duration) u eventů

Mnoho eventů může mít `duration = NULL` z důvodu pořadí zpracování
(meta.csv byl zaindexován dříve než met.fits) nebo výpadku indexace.

Skript `backfill_duration.py` projde všechny eventy bez duration,
odvodí cestu k příslušnému hodinovému meta.csv souboru a doplní hodnotu.
Zpracovává po kombinacích **stanice × měsíc**, takže průběh je viditelný.

### Spuštění (doporučeno ve screenu — může trvat hodiny)

```bash
screen -dmS backfill_duration bash -c '
  docker exec django_q python3 /tools/backfill_duration.py 2>&1 | tee /tmp/backfill_duration.log
'
# Sledování průběhu:
tail -f /tmp/backfill_duration.log
```

### Ukázka výstupu

```
Celkem eventu bez duration: 2294794
Kombinaci (stanice × mesic): 188

[1/188] ALFAPCE-R0 2024/01 — 20802 eventu → doplneno: 18500, bez CSV: 0, nenalezeno v CSV: 2302
[2/188] BPB-R1 2024/01 — 5310 eventu → doplneno: 5102, bez CSV: 208, nenalezeno v CSV: 0
...
=== HOTOVO ===
  Doplneno celkem:       ...
  Meta.csv nenalezeno:   ...   ← soubor neexistuje na disku
  Radek v CSV nenalezen: ...   ← met.fits v CSV chybí (záznam byl smazán apod.)
```

### Poznámka k `file_index`

`file_index` doplňuje duration pouze u **nově** zaindexovaných meta.csv souborů.
Pokud met.fits přijde do DB až po zpracování meta.csv, duration zůstane NULL.
`backfill_duration.py` je určen právě pro zpětné doplnění těchto případů.
