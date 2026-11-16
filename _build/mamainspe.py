"""Bouwt mama-in-spe/index.html uit mamainspe.json. Wordt aangeroepen door build.py.

Opzet zoals de vluchtkoffer (akkoord Ana 16 nov): per soort een rij kaartjes (budget, middel,
luxe), met foto, merk en label. Nieuw: een paar gewone links naar andere winkels (veld
'extern'); die krijgen een tekstkaartje zonder foto (foto's van andere winkels laden we niet)
en geen rel="sponsored", want daar is geen affiliate link.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "mama-in-spe", "index.html")

# (sleutel, klein woord, groot woord, kleur binnen het palet, knop op de voorpagina)
GROUPS = [
    ("zwanger", "voor", "nu", "pink", "Voor nu"),
    ("kraam", "voor", "straks", "yellow", "Voor straks"),
    ("verwennen", "even", "verwennen", "black", "Verwennen"),
    ("tech", "handige", "tech", "white", "Tech"),
    ("extra", "leuke", "extra's", "pink", "Extra's"),
]
OPTIE_VOLGORDE = ["budget", "middel", "luxe"]

# Korte uitleg onder de naam van een soort (alleen waar nodig).
NOTES = {
    "Bevallingsjurk": "Alleen middel en luxe: geen goede budgetoptie gevonden.",
    "Boek": "Budget: voor na de geboorte. Luxe: voor tijdens je zwangerschap.",
    "Kersenpitkussen": "Voor je nek of onderrug, niet op je buik.",
    "Cadeaubon bij een juwelier": "Bij Eenvoud koop je een bon door ze te mailen.",
}

FOOTER = """<footer class="pagefoot">
  <a class="handle" href="https://www.instagram.com/anaongefilterd/" target="_blank" rel="noopener">@anaongefilterd</a>
</footer>"""


def clean_name(name):
    """Productnaam voor alt-tekst, zonder maat (geen maatadvies)."""
    name = re.sub(r"\s*[–,]\s*maat\s.*$", "", name)
    return name.strip()


def tone_for(optie, tone):
    # Labels in de kleur van de groep; extern/extra in wit met zwarte rand, zodat het opvalt dat het anders is.
    return tone if optie in OPTIE_VOLGORDE else "white"


def card(p, tone):
    name = html.escape(clean_name(p["name"]))
    optie = html.escape(p["optie"])
    merk = html.escape(p.get("merk") or "Huismerk")
    label = f'<span class="brand">{merk}</span>\n  <span class="age age-{tone_for(p["optie"], tone)}">{optie}</span>'
    cls = f"opt-{p['optie']}" if p["optie"] in OPTIE_VOLGORDE else "opt-extra"
    if p.get("extern"):
        return (f'<li class="{cls}"><a class="card" href="{html.escape(p["link"])}" target="_blank" rel="noopener" '
                f'aria-label="{name}, {optie}, bekijk bij {merk}">\n'
                f'  <span class="ph tekst"><span>{name}</span><i aria-hidden="true">↗</i></span>\n  {label}\n</a></li>')
    # Foto altijd live van media.s-bol.com (bol-voorwaarden art. 3.2).
    img = (f'<img src="{html.escape(p["img"])}" alt="{name}" loading="lazy" referrerpolicy="no-referrer">'
           if p["img"] else "")
    return (f'<li class="{cls}"><a class="card" href="{html.escape(p["link"])}" target="_blank" rel="sponsored noopener" '
            f'aria-label="{name}, {optie}, bekijk op bol">\n'
            f'  <span class="ph">{img}</span>\n  {label}\n</a></li>')


def sort_key(p):
    o = p["optie"]
    return (OPTIE_VOLGORDE.index(o) if o in OPTIE_VOLGORDE else 9, 1 if p.get("extern") else 0, p["nr"])


def build(css_v):
    with open(os.path.join(ROOT, "_build", "mamainspe.json")) as f:
        products = json.load(f)

    sections = []
    for key, small, big, tone, _ in GROUPS:
        items = [p for p in products if p["group"] == key]
        order = []
        for p in items:
            if p["soort"] not in order:
                order.append(p["soort"])
        rows = []
        for soort in order:
            these = sorted((p for p in items if p["soort"] == soort), key=sort_key)
            opties = [p["optie"] for p in these if p["optie"] in OPTIE_VOLGORDE]
            # Vaste kolommen (budget | middel | luxe) alleen als elke optie hooguit één keer voorkomt.
            vrij = " vrij" if len(opties) != len(set(opties)) or not opties else ""
            note = NOTES.get(soort, "")
            note_html = f'\n    <p class="snote">{html.escape(note)}</p>' if note else ""
            rows.append(f"""  <div class="soort">
    <h3>{html.escape(soort)}</h3>{note_html}
    <ul class="grid trio{vrij}">
{chr(10).join(card(p, tone) for p in these)}
    </ul>
  </div>""")
        gnum_cls = "gnum sm" if len(big) > 7 else "gnum"
        sections.append(f"""<section class="page group-{tone}" id="{key}">
  <header class="ghead">
    <h2><span class="gunit">{small}</span> <span class="{gnum_cls}">{html.escape(big)}</span></h2>
    <p class="gcount">{len(order)} soorten</p>
  </header>
  <div class="soorten">
{chr(10).join(rows)}
  </div>
  {FOOTER}
</section>""")

    nav_links = "\n".join(f'    <a href="#{k}" class="j-{t}">{n}</a>' for k, _, _, t, n in GROUPS)
    nav = f'<nav class="jump" aria-label="Kies een onderdeel">\n{nav_links}\n  </nav>'

    page = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<title>Verlanglijst voor mama's in spé · @anaongefilterd</title>
<meta name="description" content="Wat kun je als mama in spé vragen voor Sint en Kerst? Mijn favorieten, per ding een budget-, middel- en luxe-optie.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Poppins:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../assets/gids.css?v={css_v}">
</head>
<body>
<main class="gids">

<section class="cover">
  <p class="sticker sintkerst" aria-hidden="true"><span>voor sint</span><b>&amp; kerst</b></p>
  <p class="kicker">@anaongefilterd</p>
  <h1><span class="t1 xl">Verlang-<br>lijst</span><span class="t2">voor</span><span class="t3"><mark>mama's in spé</mark></span></h1>
  <p class="intro">Dit zijn mijn favorieten voor op je verlanglijstje! Dingen die je als mama in spé écht gebruikt: nu, bij de bevalling én straks met je baby. Per ding kies je zelf: budget, middel of luxe. Tik op een kaartje en je ziet het direct in de winkel.</p>
  {nav}
  <p class="disclosure"><strong>Affiliate links:</strong> koop je via een link, dan krijg ik een kleine commissie van bol. Jij betaalt niets extra. Je koopt bij bol; deze gids is van mij, niet van bol. Kaartjes zonder foto zijn gewone links naar andere winkels; daar verdien ik niets aan.</p>
</section>

{chr(10).join(sections)}

<section class="thanks">
  <h2>Dank<span>je</span>wel!</h2>
  <p>Fijn dat je mijn lijst hebt bekeken. Stuur hem gerust door naar wie jou iets wil geven, en fijne feestdagen!</p>
  <a class="follow" href="https://www.instagram.com/anaongefilterd/" target="_blank" rel="noopener">Volg @anaongefilterd</a>
</section>

</main>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(page)
    bol = [p for p in products if not p.get("extern")]
    missing = [p["nr"] for p in bol if not p["img"]]
    print("geschreven:", OUT, "-", len(bol), "bol-producten +", len(products) - len(bol), "gewone links",
          f"(zonder foto: {missing})" if missing else "")
