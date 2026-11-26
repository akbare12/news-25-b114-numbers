# THE WORLD TODAY — 25 November 2026 (news-image-20261125)

[![News Image 20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/akbare12/news-25-b114-numbers/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/akbare12/news-25-b114-numbers/reward.svg)](https://make.fun/bounty/news-image-20261125)

One-page newspaper front page (1024×1024, under 1 MiB) summing up world news
on **Wednesday 25 November 2026** — **50 stories across 10 regions**: 3 heroes,
10 cards, 37 ALSO items.

## Angle: NUMBERS

A strip of the 6 biggest numbers of the day sits under the masthead
(Kospi −6.16%, China tariff 20%, 76 hostages freed, 31 killed in Cairo,
9,500 lbs blown up in Iowa, $740m Australia–Solomons pact), and every hero
and card scene carries a big number badge that stays fully inside its box.

## Cards (10)

Gaza (4 dead) • Cairo tanker fire (31 killed) • Cartagena (76 freed) •
Bogor gold mine (9 dead, 17 trapped) • Solomon Islands pact ($740m) •
Iowa blast (9,500 lbs) • Abrego Garcia lands in Madrid • Macy's parade
delayed • Sudan drone strikes (19 killed, reported 25 Nov) • US GDP +4.3%.

## Heroes

1. **Trump hits 14 partners with new tariffs** — China 20% (up to 40% if the
   truce fails), EU capped at 15%.
2. **Kospi crashes 6.16%** — Samsung −9.87%, SK Hynix −11.05%; foreigners
   sell 1.95tn won.
3. **First foreign astronaut boards Tiangong** — Pakistan's Zeeshan Ali docks
   with Shenzhou-24.

Every hero and card carries a certainty letter (C confirmed, R reported,
CL claimed) with a HOW SURE legend, a 2-line DATE CHECK for stories that
belong to other days, a numbered world map (pins 1–13), a 6-milestone UTC
strip, and a region bar totalling 50.

## Build

```sh
python3 gen.py        # renders entry.png (Pillow, build time only)
python3 main.py       # stdlib-only: copies entry.png to $MAKEFUN_OUTPUT_DIR
```

`gen.py` checks every headline, deck, badge, strip label and footer line
programmatically and exits non-zero on any overflow. Verified: 0 overflows,
50 stories, 10 regions, entry.png 161,915 bytes, sha256
`7d9784ff5cbdf98ed7cf5d7cbd5b9d5b3364af3d644fd3b8a5a27e0e746d0f84`.
Stdlib-venv simulation (venv without Pillow, different cwd, empty out dir,
read-only repo copy) exits 0 and the output hash matches entry.png.

## Sources

Reuters, AP, BBC, CNN, Xinhua, Korea Exchange, pm.gov.au — all facts
checked live 26 November 2026. Stories dated 24 Nov or earlier (Huawei
verdict, PIF Tower strike, Sudan night strikes, Huang reinstatement) are
kept out of the 25 Nov count and listed only in DATE CHECK.
