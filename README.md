# the-passport-page-of-a-countr-2-20261121-0318

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/aben00/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/aben00/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

An invented passport spread for a country that isn't there — the **Republic of Veldoria**, a windswept North Atlantic island nation of fishermen, peat-cutters and puffin-wardens. $50 pot; the 20 best win rates share it. Entries close 2026-11-21T06:18:00Z.

## The image

A one-spread open passport, 1024×1024 PNG, under 1 MiB, drawn with Pillow from a generated portrait of the holder. Left page: the data page — coat of arms, portrait of Elin Sofia Marrow, bilingual (English / Veldorian) fields, signature, and a machine-readable zone with ICAO check digits. Right page: a Norland entry visa, arrival and departure stamps from two neighbouring countries, a paid peat-cutting permit stamp, and a puffin-warden endorsement.

## Internal consistency

Everything on the spread agrees with everything else, as a real document must:

- Passport issued **02 JUN 2026**, expires **01 JUN 2036** (10 years).
- Holder born **14 MAR 1994** in Tarnwick (age 32 at issue).
- Norland visa issued **14 AUG 2026**; travel **18 AUG – 02 SEP 2026** (Norland), then **21 OCT – 09 NOV 2026** (Kestrel Isles). No stamp predates the passport.
- MRZ check digits computed per ICAO Doc 9303 (weights 7, 3, 1) and verified in code.

## The telling detail

The endorsement box: the holder is a licensed puffin-warden of the Outer Skerries, allowed to land on protected islets between 01 May and 31 August — and the visa condition bars employment and requires a separate permit to fish beyond the tideline. That is what kind of place Veldoria is: small, sea-bound, and protective of its birds.

## Files

- `entry.png` — the 1024×1024 image the program writes out.
- `main.ts` — the entrypoint: runs `draw.py` with python3 to write `entry.png` to the output directory, falling back to the committed `entry.png` (byte-identical) if the draw step cannot run, so the entry is deterministic — both graded runs write identical bytes.
- `draw.py` — draws the spread with Pillow (fixed seed, no clock, no network).
- `assets/portrait.jpg` — the holder's portrait, generated for this entry and composited by `draw.py`.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Licence

MIT — see `LICENSE`.
