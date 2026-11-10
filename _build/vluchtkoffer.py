"""Bouwt vluchtkoffer/index.html uit vluchtkoffer.json. Wordt aangeroepen door build.py.

Opzet (anders dan de Sint-gids): groepen Mama/Baby/Partner, per soort één rij met
3 fotokaartjes (budget, middel, luxe). Op het kaartje alleen de foto en het label.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "vluchtkoffer", "index.html")

# (sleutel in json, naam op de pagina, kleur binnen het palet)
GROUPS = [
    ("mama", "mama", "pink"),
    ("baby", "baby", "yellow"),
    ("partner", "partner", "black"),
]
# Voorbeeld voor Ana: alleen Mama bouwen. Na akkoord: alle groepen.
BUILD_GROUPS = {"mama"}

OPTIES = ["budget", "middel", "luxe"]

# Naam boven de rij en korte uitleg (uit de briefing in Notion).
MATEN = "Andere maten kies je op bol."
SOORTEN = {
    "Voedingsbh": ("Voedingsbh", MATEN),
    "Nachthemd met knoopjes": ("Nachthemd met knoopjes", "Alleen middel en luxe: geen goede budgetoptie gevonden. " + MATEN),
    "Netbroekjes": ("Netbroekjes", "Zit vaak al in je kraampakket. " + MATEN),
    "Kraamverband": ("Kraamverband", "Zit vaak al in je kraampakket."),
    "Oplader extra lang snoer": ("Oplader met extra lang snoer",
                                 "Voor telefoons met USB-C. Luxe = Apple-adapter + Apple-kabel van 2 m, "
                                 "de langste kabel die Apple maakt."),
    "Mini doucheproducten": ("Mini doucheproducten", "Budget en middel: lege flesjes om zelf te vullen. Luxe: een gevulde set."),
    "Dikke sokken": ("Dikke sokken", MATEN),
    "Sloffen": ("Sloffen", MATEN),
    "Badjas": ("Badjas", "Lange modellen, over de knie. " + MATEN),
    "Wikkeldeken": ("Wikkeldeken", "Voor in de autostoel of kinderwagen, niet voor in bed."),
    "Overslagrompers 50/56": ("Overslagrompers maat 50/56", MATEN),
}

FOOTER = """<footer class="pagefoot">
  <a class="handle" href="https://www.instagram.com/anaongefilterd/" target="_blank" rel="noopener">@anaongefilterd</a>
</footer>"""


def clean_name(name):
    """Productnaam voor alt-tekst, zonder de gekozen maat (geen maatadvies)."""
    name = re.sub(r"\s*[–,]\s*maat\s.*$", "", name)
    name = re.sub(r"\s+(?:XS|S|M|L|XL|XXL)(?:/(?:XS|S|M|L|XL|XXL))?$", "", name)
    return name.strip()


def photo_link(p, optie, extra=""):
    name = html.escape(clean_name(p["name"]))
    # Foto altijd live van media.s-bol.com; zolang er nog geen foto-URL is, blijft de tegel leeg.
    img = (f'<img src="{html.escape(p["img"])}" alt="{name}" loading="lazy" referrerpolicy="no-referrer">'
           if p["img"] else "")
    return (f'<a class="card{extra}" href="{html.escape(p["link"])}" target="_blank" rel="sponsored noopener" '
            f'aria-label="{name}, {optie}, bekijk op bol">\n'
            f'  <span class="ph">{img}</span>')


def slot(items, optie, tone):
    label = f'<span class="age age-{tone}">{optie}</span>'
    if len(items) == 1:
        return f'<li class="opt-{optie}">{photo_link(items[0], optie)}\n  {label}\n</a></li>'
    # twee producten samen als één optie (bijv. adapter + kabel): twee foto-links, één label
    links = "\n".join(photo_link(p, optie) + "\n</a>" for p in items)
    return f'<li class="opt-{optie} duo"><span class="duo-ph">\n{links}\n</span>\n  {label}\n</li>'


def build(css_v):
    with open(os.path.join(ROOT, "_build", "vluchtkoffer.json")) as f:
        products = json.load(f)

    sections = []
    for key, title, tone in GROUPS:
        if key not in BUILD_GROUPS:
            continue
        items = [p for p in products if p["group"] == key]
        order = []
        for p in sorted(items, key=lambda p: p["nr"]):
            if p["soort"] not in order:
                order.append(p["soort"])
        rows = []
        for soort in order:
            name, note = SOORTEN.get(soort, (soort, ""))
            slots = []
            for optie in OPTIES:
                these = sorted((p for p in items if p["soort"] == soort and p["optie"] == optie), key=lambda p: p["nr"])
                if these:
                    slots.append(slot(these, optie, tone))
            note_html = f'\n    <p class="snote">{html.escape(note)}</p>' if note else ""
            rows.append(f"""  <div class="soort">
    <h3>{html.escape(name)}</h3>{note_html}
    <ul class="grid trio">
{chr(10).join(slots)}
    </ul>
  </div>""")
        sections.append(f"""<section class="page group-{tone}" id="{key}">
  <header class="ghead">
    <h2><span class="gunit">voor</span> <span class="gnum">{title}</span></h2>
    <p class="gcount">{len(order)} soorten</p>
  </header>
  <div class="soorten">
{chr(10).join(rows)}
  </div>
  {FOOTER}
</section>""")

    nav_links = "\n".join(f'    <a href="#{k}" class="j-{t}">{n.capitalize()}</a>' for k, n, t in GROUPS)
    nav = f'<nav class="jump" aria-label="Kies voor wie">\n{nav_links}\n  </nav>'

    page = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<title>Vluchtkoffer: inpaklijst voor mama, baby en partner · @anaongefilterd</title>
<meta name="description" content="Mijn inpaklijst voor de vluchtkoffer, met per ding een budget-, middel- en luxe-optie. Tik op een product om het op bol te bekijken.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Poppins:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../assets/gids.css?v={css_v}">
</head>
<body>
<main class="gids">

<section class="cover">
  <p class="sticker opties" aria-hidden="true"><span>per soort</span><b>3 opties</b></p>
  <p class="kicker">@anaongefilterd</p>
  <h1><span class="t1 xl">Vlucht&shy;koffer</span><span class="t2">inpaklijst voor <mark>mama, baby &amp; partner</mark></span></h1>
  <p class="intro">Dit zijn mijn favorieten voor in je vluchtkoffer! Voor jou, je baby én je partner. Per ding kies je zelf: budget, middel of luxe. Tik op een foto en je ziet het direct op bol.</p>
  {nav}
  <p class="disclosure"><strong>Affiliate links:</strong> koop je via een link, dan krijg ik een kleine commissie van bol. Jij betaalt niets extra. Je koopt bij bol; deze gids is van mij, niet van bol.</p>
</section>

{chr(10).join(sections)}

</main>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(page)
    built = [p for p in products if p["group"] in BUILD_GROUPS]
    missing = [p["nr"] for p in built if not p["img"]]
    print("geschreven:", OUT, "-", len(built), "producten", f"(zonder foto: {missing})" if missing else "")
