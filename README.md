# The Passport Page of a Country That Isn't There

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/mizuseii/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/mizuseii/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

Entry for the [make.fun bounty "The Passport Page of a Country That Isn't There"](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318).

## What it is

`main.py` (pure Python 3.13 standard library, no network, no dependencies)
draws one image — an open passport spread for the invented **Republic of
Talmarin**, a small North Atlantic island nation whose capital is Port
Anselm and whose only arrivals are by sea ferry — and writes it to
`/output/entry.png` (1024×1024 PNG, well under the 1 MiB gate).

Left page, the data page: coat of arms, bilingual English/Talmarin fields
for Mara Ellison Vey (born 14 Mar 1994 in Port Anselm), a drawn portrait,
and a machine-readable zone with real MRZ check digits. Right page, the
visa page: arrival and departure stamps from neighbouring Meridia,
Ostravell and the Kestrel Isles, every date after the 02 Jun 2026 issue
date and before the 01 Jun 2036 expiry, plus a Kestrel Isles visitor visa
whose condition — landing by sea ferry only, no air arrivals at Port
Anselm — is the detail that reveals what kind of place Talmarin is.

## Run it

```sh
python3 main.py   # writes /output/entry.png
```

The program is deterministic: two runs produce byte-identical output
(verified locally, 42,877 bytes, 1024×1024).

## License

MIT — see [LICENSE](LICENSE).
