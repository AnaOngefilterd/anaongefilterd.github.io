# Gidsen-website @anaongefilterd

Elke gids is een eigen map (bijv. `sinterklaas-0-2/`), gebouwd met `python3 _build/build.py` uit `_build/products.json`. Stijl staat in `assets/gids.css`.

Vaste regels:
- Productfoto's altijd live van `media.s-bol.com` laden; nooit kopiëren of zelf hosten (bol-voorwaarden art. 3.2).
- Foto-URL's ophalen: `python3 _build/bol_fotos.py <gids>` (bol Marketing Catalog API; elk product in `_build/<gids>.json` heeft een `bol_id`). De sleutel "Gidsen foto's" staat als netwerkgeheim op de Claude-omgeving "anaongefilterd gidsen", niet in deze repo. bol.com zelf blokkeert de cloud.
- Kaartjes: alleen foto + leeftijdslabel, het hele kaartje is de affiliate link (`rel="sponsored noopener"`, `target="_blank"`).
- Affiliatetekst alleen op de voorpagina; onder elke pagina alleen `@anaongefilterd`.
- Kleuren roze, zwart, wit, geel; Playfair Display + Poppins. Stijl niet veranderen zonder akkoord van Ana.
- Bij elke wijziging een nieuwe `?v=` achter `gids.css` en andere assets, anders toont de telefoon een oude versie.
- Nieuwe gids eerst met `noindex`; weghalen als Ana hem definitief noemt.
- Blijft een GitHub Pages-deploy langer dan 10 minuten in de wachtrij, push een nieuwe commit.

De volledige werkwijze staat in de skill `affiliate-weekgids`.
