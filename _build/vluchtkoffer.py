"""Bouwt vluchtkoffer/index.html uit vluchtkoffer.json. Wordt aangeroepen door build.py.

Opzet (anders dan de Sint-gids): groepen Mama/Baby/Partner, per soort één rij met
3 fotokaartjes (budget, middel, luxe). Op het kaartje de foto, het merk en het label.
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
BUILD_GROUPS = {"mama", "baby", "partner"}

OPTIES = ["budget", "middel", "luxe"]

# Naam boven de rij en korte uitleg (uit de briefing in Notion). Geen maatadvies of "andere maten"-tekst.
SOORTEN = {
    "Nachthemd met knoopjes": ("Nachthemd met knoopjes", "Alleen middel en luxe: geen goede budgetoptie gevonden."),
    "Netbroekjes": ("Netbroekjes", "Zit vaak al in je kraampakket."),
    "Kraamverband": ("Kraamverband", "Zit vaak al in je kraampakket."),
    "Oplader extra lang snoer": ("Oplader met extra lang snoer",
                                 "Voor telefoons met USB-C. Luxe = Apple-adapter + Apple-kabel van 2 m, "
                                 "de langste kabel die Apple maakt."),
    "Mini doucheproducten": ("Mini doucheproducten", "Budget en middel: lege flesjes om zelf te vullen. Luxe: een gevulde set."),
    "Badjas": ("Badjas", "Lange modellen, over de knie."),
    "Wikkeldeken": ("Wikkeldeken", "Voor in de autostoel of kinderwagen, niet voor in bed."),
    "Overslagrompers 50/56": ("Overslagrompers maat 50/56", ""),
}

# Afvinklijst zonder links: Ana's eigen lijst "Vluchtkoffer Overig" uit de bonuspack (akkoord Ana 10 nov).
AFVINKLIJST = [
    ("Documenten", [
        "Identiteitsbewijs (ID-kaart of paspoort), voor mama én partner",
        "Zorgpas / verzekeringspas, voor mama én partner",
        "Verwijsbrief van verloskundige of gynaecoloog (als je die hebt)",
        "Overzicht medicatie / allergieën",
        "Zwangerschapsdossier",
        "Bloedgroepkaart (check of die in je zwangerschapsdossier zit)",
        "Contactgegevens verloskundigenpraktijk",
        "Contactnummer kraamzorgorganisatie",
        "Briefje met noodnummers: huisarts, verloskundige, ziekenhuis, 24/7 spoedlijn",
        "Uitgeprinte naam van je baby voor de registratie",
        "Bevallingsplan (geprint + digitaal)",
    ]),
    ("Eten en drinken", [
        "Kleingeld voor automaten (€25–€30)",
        "Aquarius",
        "Dextro Energy",
        "Dadels",
        "Gekoeld kokoswater",
        "Limonade",
        "Koekjes",
        "Mueslirepen",
        "Proteïnerepen",
        "Snelle Jelle",
        "Gesmeerde boterhammen",
        "Keelsnoepje of iets om op te zuigen",
        "Kauwgom",
    ]),
]

EBOOK_URL = "https://anaongefilterd.nl/checkout/klaar-voor-je-baby-e-book"

# Themadetail voorpagina: klein rolkoffertje met een sticker van een flesje (akkoord Ana 10 nov).
KOFFER = """<svg class="koffer" aria-hidden="true" viewBox="0 0 80 112" width="80" height="112">
    <path d="M29 30V8a4 4 0 0 1 4-4h14a4 4 0 0 1 4 4v22" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
    <rect x="6" y="28" width="68" height="72" rx="12" fill="#ff4fa0"/>
    <rect x="20" y="34" width="4" height="60" rx="2" fill="#111014" opacity=".18"/>
    <rect x="56" y="34" width="4" height="60" rx="2" fill="#111014" opacity=".18"/>
    <circle cx="23" cy="105" r="5" fill="#111014" stroke="#fff" stroke-width="2.5"/>
    <circle cx="57" cy="105" r="5" fill="#111014" stroke="#fff" stroke-width="2.5"/>
    <g transform="rotate(-12 42 64)">
      <circle cx="42" cy="64" r="17" fill="#ffe03d" stroke="#111014" stroke-width="2"/>
      <path d="M38.5 54.5c0-3 1.6-5 3.5-5s3.5 2 3.5 5z" fill="#ff4fa0" stroke="#111014" stroke-width="1.6" stroke-linejoin="round"/>
      <rect x="36" y="54.5" width="12" height="4" rx="1.2" fill="#111014"/>
      <rect x="36.5" y="58.5" width="11" height="17" rx="3.5" fill="#fff" stroke="#111014" stroke-width="1.6"/>
      <path d="M41 63h4M41 67h4M41 71h4" stroke="#ff4fa0" stroke-width="1.6" stroke-linecap="round"/>
    </g>
  </svg>"""

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
    # Onder de foto het merk (akkoord Ana 11 nov, variant A); geen merk bij bol = "Huismerk".
    merk = html.escape(items[0].get("merk") or "Huismerk")
    label = f'<span class="brand">{merk}</span>\n  <span class="age age-{tone}">{optie}</span>'
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
    nav_links += '\n    <a href="#afvinklijst" class="j-white">Afvinklijst</a>'

    checkgroups = []
    for title, items in AFVINKLIJST:
        lis = "\n".join(f'      <li><label><input type="checkbox"><span>{html.escape(i)}</span></label></li>' for i in items)
        checkgroups.append(f"""  <div class="soort">
    <h3>{html.escape(title)}</h3>
    <ul class="checklist">
{lis}
    </ul>
  </div>""")
    afvink = f"""<section class="page group-white" id="afvinklijst">
  <header class="ghead">
    <h2><span class="gunit">de</span> <span class="gnum sm">afvinklijst</span></h2>
    <p class="gcount">zonder links</p>
  </header>
  <div class="soorten">
{chr(10).join(checkgroups)}
  </div>
  {FOOTER}
</section>"""
    nav = f'<nav class="jump" aria-label="Kies voor wie">\n{nav_links}\n  </nav>'

    page = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
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
  {KOFFER}
  <p class="kicker">@anaongefilterd</p>
  <h1><span class="t1 xl">Vlucht&shy;koffer</span><span class="t2">inpaklijst voor</span><span class="t3"><mark>mama, baby &amp; partner</mark></span></h1>
  <p class="intro">Dit zijn mijn favorieten voor in je vluchtkoffer! Voor jou, je baby én je partner. Per ding kies je zelf: budget, middel of luxe. Tik op een foto en je ziet het direct op bol.</p>
  {nav}
  <p class="disclosure"><strong>Affiliate links:</strong> koop je via een link, dan krijg ik een kleine commissie van bol. Jij betaalt niets extra. Je koopt bij bol; deze gids is van mij, niet van bol.</p>
</section>

{chr(10).join(sections)}

{afvink}

<section class="ebook" id="e-book">
  <p class="kicker">mijn e-book</p>
  <h2>Klaar voor <span>je baby!</span></h2>
  <p>De complete vluchtkoffer-inpaklijst is één van de 6 bonussen bij mijn <em>Klaar voor je baby!</em> e-book: dé must-read voor elke zwangere vrouw en moeder. Alles wat je moet weten, regelen en kopen. Eerlijk en ongefilterd.</p>
  <ul class="ticks">
    <li>175 pagina's: van kraamzorg, verzekeringen en verlof tot je relatie, momrage en hoe het écht is om moeder te zijn</li>
    <li>Hoe je de eerste 6 weken overleeft</li>
    <li>Verlof voor jezelf en je partner, óók als je zzp'er bent</li>
    <li>6 bonussen: de Mega Checklist per trimester, de favorietenlijst met 500 producten, de uitzetlijst per seizoen, wat je wel en niet vergoed krijgt van je zorgverzekering, de top 10 zorgverzekeringen voor zwangere vrouwen en <strong>de vluchtkoffer-inpaklijst</strong></li>
  </ul>
  <p class="price"><b>€19</b><span>minder dan een romper die je baby twee weken draagt</span></p>
  <a class="buy" href="{EBOOK_URL}" target="_blank" rel="noopener">Ja, dit wil ik!</a>
</section>

<section class="thanks">
  <h2>Dank<span>je</span>wel!</h2>
  <p>Fijn dat je mijn lijst hebt bekeken. Heel veel succes de laatste weken, en laat me weten wat er in jouw vluchtkoffer gaat!</p>
  <a class="follow" href="https://www.instagram.com/anaongefilterd/" target="_blank" rel="noopener">Volg @anaongefilterd</a>
</section>

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
