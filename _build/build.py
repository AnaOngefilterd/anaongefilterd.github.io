"""Bouwt de gids-pagina uit products.json. Gebruik: python3 _build/build.py"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "sinterklaas-0-2", "index.html")

GROUPS = [
    ("0-6", "0–6", "maanden", "pink"),
    ("6-12", "6–12", "maanden", "yellow"),
    ("1", "1", "jaar", "black"),
    ("2", "2", "jaar", "white"),
]

with open(os.path.join(ROOT, "_build", "products.json")) as f:
    products = json.load(f)

FOOTER = """<footer class="pagefoot">
  <a class="handle" href="https://www.instagram.com/anaongefilterd/" target="_blank" rel="noopener">@anaongefilterd</a>
</footer>"""


def card(p, tone):
    name = html.escape(p["name"])
    return f"""<li><a class="card" href="{html.escape(p['link'])}" target="_blank" rel="sponsored noopener" aria-label="{name}, {html.escape(p['age'])}, bekijk op bol">
  <span class="ph"><img src="{html.escape(p['img'])}" alt="{name}" loading="lazy" referrerpolicy="no-referrer"></span>
  <span class="age age-{tone}">{html.escape(p['age'])}</span>
</a></li>"""


sections = []
for key, num, unit, tone in GROUPS:
    items = [p for p in products if p["group"] == key]
    if not items:
        continue
    cards = "\n".join(card(p, tone) for p in items)
    sections.append(f"""<section class="page group-{tone}" id="leeftijd-{key}">
  <header class="ghead">
    <h2><span class="gnum">{num}</span> <span class="gunit">{unit}</span></h2>
    <p class="gcount">{len(items)} tips</p>
  </header>
  <ul class="grid">
{cards}
  </ul>
  {FOOTER}
</section>""")

nav_links = "\n".join(
    f'    <a href="#leeftijd-{k}" class="j-{t}">{n} {"mnd" if u == "maanden" else u}</a>'
    for k, n, u, t in GROUPS if any(p["group"] == k for p in products))
nav = f'<nav class="jump" aria-label="Kies een leeftijd">\n{nav_links}\n  </nav>'

page = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>40 Sinterklaastips 0–2 jaar · @anaongefilterd</title>
<meta name="description" content="Mijn favoriete Sinterklaascadeaus voor kinderen van 0 tot 2 jaar. Tik op een product om het op bol te bekijken.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Poppins:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../assets/gids.css?v=1793893628">
</head>
<body>
<main class="gids">

<section class="cover">
  <div class="pepernoten" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
  <p class="sticker" aria-hidden="true"><span>pakjesavond</span><b>5 dec</b></p>
  <p class="kicker">@anaongefilterd</p>
  <h1><span class="big">40</span><span class="t1">Sinterklaas&shy;tips</span><span class="t2">voor <mark>0–2 jaar</mark></span></h1>
  <p class="intro">Dit zijn mijn favorieten! Speelgoed waar mijn kids echt heel veel plezier mee hebben gehad, én dingen die ik zelf het liefst cadeau geef. Tik op een product en je ziet het direct op bol.</p>
  {nav}
  <p class="disclosure"><strong>Affiliate links:</strong> koop je via een link, dan krijg ik een kleine commissie van bol. Jij betaalt niets extra. Je koopt bij bol; deze gids is van mij, niet van bol.</p>
</section>

{chr(10).join(sections)}

<section class="thanks">
  <div class="pepernoten small" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
  <h2>Dank<span>je</span>wel!</h2>
  <p>Fijn dat je mijn tips hebt bekeken. Veel plezier met pakjesavond, en laat me weten wat je hebt gekozen.</p>
  <a class="follow" href="https://www.instagram.com/anaongefilterd/" target="_blank" rel="noopener">Volg @anaongefilterd</a>
</section>

</main>
</body>
</html>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write(page)
print("geschreven:", OUT, "-", len(products), "producten")
