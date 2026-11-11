"""Vult de foto-URL's (media.s-bol.com) van een gids in via de bol Marketing Catalog API.

Gebruik:  python3 _build/bol_fotos.py vluchtkoffer          (alleen lege 'img')
          python3 _build/bol_fotos.py vluchtkoffer --alles  (alles opnieuw)

Leest _build/<gids>.json; elk product heeft een 'bol_id' (nummer uit de bol-link).
Per product: bol_id -> EAN -> product met foto, prijs en score. Schrijft 'img' terug
en toont welke producten nu niet te koop zijn of weinig/geen reviews hebben.

Inloggen: de sleutel "Gidsen foto's" (Marketing Catalog API) staat als netwerkgeheim
op de Claude-omgeving "anaongefilterd gidsen" en wordt automatisch toegevoegd aan
verzoeken naar login.bol.com. Hij staat dus niet in deze repo.
De foto's zelf worden niet opgeslagen: de gids laadt ze live van bol (art. 3.2).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_URL = "https://login.bol.com/token?grant_type=client_credentials"
BASE = "https://api.bol.com/marketing/catalog/v1"


def call(url, method="GET", headers=None):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode("utf-8", "replace")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    gids, alles = sys.argv[1], "--alles" in sys.argv
    path = os.path.join(ROOT, "_build", f"{gids}.json")
    products = json.load(open(path))

    status, tok = call(TOKEN_URL, "POST", {"Accept": "application/json", "Content-Length": "0"})
    if status != 200:
        raise SystemExit(f"Inloggen bij bol mislukt ({status}): {tok}")
    headers = {"Authorization": f"Bearer {tok['access_token']}", "Accept": "application/json",
               "Accept-Language": "nl"}

    niet_te_koop, geen_reviews, mist = [], [], []
    for p in products:
        if (p.get("img") and not alles) or not p.get("bol_id"):
            continue
        status, d = call(f"{BASE}/products/{p['bol_id']}/to-ean", headers=headers)
        time.sleep(0.35)
        if status != 200:
            mist.append(p["nr"]); print(p["nr"], "geen EAN:", status, d); continue
        q = "country-code=NL&include-image=true&include-offer=true&include-rating=true"
        status, prod = call(f"{BASE}/products/{d['ean']}?{q}", headers=headers)
        time.sleep(0.35)
        img = (prod.get("image") or {}).get("url", "") if status == 200 else ""
        if not img.startswith("https://media.s-bol.com/"):
            mist.append(p["nr"]); print(p["nr"], "geen foto:", status); continue
        p["img"] = img
        offer = prod.get("offer") or {}
        if offer.get("price") is None:
            niet_te_koop.append(p["nr"])
        if not prod.get("rating"):
            geen_reviews.append(p["nr"])
        print(p["nr"], img, offer.get("price"), prod.get("rating"), "|", (prod.get("title") or "")[:60])

    keys = list(products[0].keys())
    with open(path, "w") as f:
        f.write("[\n" + ",\n".join("  " + json.dumps({k: p.get(k, "") for k in keys}, ensure_ascii=False)
                                   for p in products) + "\n]\n")
    print(f"\nklaar. zonder foto: {mist}\nnu niet te koop op bol: {niet_te_koop}\ngeen score/reviews: {geen_reviews}")


if __name__ == "__main__":
    main()
