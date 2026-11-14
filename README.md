# Santadoku

Puzzle logique de Noël pour **iOS**, **Android** et **Web** (Expo / React
Native + React Native Web), dérivé de Zombidoku : mêmes mécaniques, thème
entièrement refait.

## Le jeu

La grille N×N est découpée en N **quartiers** colorés. Place **1 Père Noël 🎅**
par ligne, par colonne et par quartier, sans que deux Pères Noël ne se
touchent (même en diagonale), sinon les rennes s'emmêlent !

- Tap : barre une case (note sans risque). Double-tap : pose un Père Noël
  (une erreur coûte une vie ❤️ sur 3, sauf en mode Zen). Glisser pour barrer
  plusieurs cases.
- Bonus : 💡 indice par déduction logique, 🎅 Père Noël auto, 🦌 renne (barre 3
  cases fausses). Rechargeables avec des biscuits 🍪 ou une pub récompensée.
- **Défi du Père Noël** quotidien (9×9 identique pour tous, débloqué au niveau 21).
- **Jours consécutifs** ⭐ façon calendrier de l'Avent, avec bonus croissants.
- **Compagnon** lutin à nourrir de biscuits : 10 paliers (🧝 → 🎄), accessoires.
- **Cadeaux 🎁 et traîneaux 🛷** à ouvrir (gratuit, pub ou biscuits).
- Boutique (RevenueCat), retrait des pubs, 6 langues (fr, en, es, de, it, pt).
- Musique et bruitages **synthétisés** (`scripts/generate-audio.py`) : mélodies
  traditionnelles du domaine public (Jingle Bells, Douce nuit,
  We Wish You a Merry Christmas), aucune attribution requise.

Le moteur (`src/engine/`) génère des grilles à solution unique jusqu'à 16×16.
Les noms internes du code (`zombie`, `brains`, `autoCats`, `mice`, `bat`)
viennent de Zombidoku et ont été conservés pour limiter les risques : seuls
l'affichage, les textes et les assets sont rethématisés
(🧟→🎅, 🧠→🍪, 🦇→🦌, 🪦→🎁, ⚰️→🛷, 🌙→⭐).

## Lancer

```bash
npm install
npm run web       # navigateur
npm run android   # Android (Expo)
npm run ios       # iOS (Expo)
```

Regénérer sons et musiques : `python scripts/generate-audio.py`.
Regénérer les icônes : `node scripts/generate-icons.mjs` (nécessite `pngjs`).
Regénérer les animations Lottie : `node scripts/generate-lottie.mjs`.

## À faire avant publication (je ne peux pas le faire à ta place)

1. `npx eas-cli init` (crée le projet EAS ; `projectId` absent de `app.config.ts`).
2. AdMob : créer les apps Santadoku Android/iOS et les blocs Récompensé +
   Interstitiel, remplir `src/config/adIds.js`, puis `USE_TEST_ADS = false`.
3. RevenueCat : créer le projet et les produits `santadoku_*` (voir
   `src/config/revenuecat.ts`), coller les clés publiques `appl_` / `goog_`.
4. Héberger `public/privacy.html` (GitHub Pages) et remplir la fiche store
   avec `docs/store-submission.md`.
5. `npx eas-cli build --platform android --profile production`.
