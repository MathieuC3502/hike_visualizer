# Visualiseur de Randonnées
Site web : https://mathieuc3502.github.io/hike_visualizer/
Cet outil a pour but de visualiser des randonnées personnelles en région PACA

## Fonds de Cartes Disponibles
- OpenStreetMap (https://www.openstreetmap.org/)
- OpenTopoMap (https://opentopomap.org)

Les informations d'élévation et de dénivelé ont été obtenues à partir de [RGE ALTI](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_RGE-ALTI?redirected_from=geoservices.ign.fr), à 5 mètres de résolution au sol.

## Randonnées et Points d'Intérêts
Les randonnées et points d'intérêts présents sur la carte ont été ajoutés manuellement. D'autres viendront s'y ajouter plus tard.

## Comment lancer le code

### Etapes de Setup
- Télécharger le DEM RGE ALTI à 5M en Bouches-du-Rhône : [Telechargement RGE ALTI](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_RGE-ALTI)
- Merger toutes les petites tuiles de DEM en une seule (code et méthode détaillée non fournis actuellement)
- Sauvegarder le résultat final mergé comme un Raster .tif
- Editer dans *./src/config.py* la variable ***DEM_PATH***

### Etapes de Lancement
- Installer et activer l'environnement
- Lancer 'python .\src\preprocess\preprocess.py'
- Après, lancer 'python .\src\build_map.py'

Le fichiers *./docs/index.html* sera alors mis à jour et exploitable

## Problèmes actuels
- Les .shp en entrée doivent contenir une seule ligne. S'ils en contiennent plusieurs, aucun merge n'est fait. Les tentatives de merge avec "union" causent des problèmes car elles suppriment les allez/retour sur le même chemin, ou rangent les segments dans le mauvais ordre, causant des "sauts" non naturels de l'un à l'autre. La "solution" actuelle est de redessiner proprement les paths à la main dans QGIS, mais cela est peu pratique. (Actuellement tous les chemins sont tracés à la main dans QGIS. Mais si l'on trace le chemin en plusieurs segments puis qu'on les merge, on tombe dans le même problème !). Il faut travailler la pipeline tracé-merge pour s'assurer de la cohérence/qualité des tracés --> Voir fichier ./src/preprocess/build_elevation_profiles.py
- Il faut ajouter les informations de la rando dans le cadre prévu à cet effet (distance totale et dénivelés peuvent surement etre calculés à partir des infos déjà disponible, la description et le nom formatté seront peut-être à ajouter manuellement) --> Voir fichier ./src/assets/trail_info.js
- La gestion des données, le stockage, le rangement etc... N'est pas travaillé, correct ou "propre", à étudier 
