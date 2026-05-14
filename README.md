# KmerSource AI 🇨🇲🇨🇳

Une intelligence artificielle conçue pour aider les Camerounais à effectuer des achats à l'étranger (notamment en Chine) avec des contacts fiables et une livraison directe au Cameroun.

## Fonctionnalités
- **Scan complet** : Obtenez les données les plus récentes sur les tarifs de fret et les délais en demandant un "scan complet".
- **Plateforme Publique** : Recommandation et liens vers des outils de suivi en ligne faciles à utiliser (**Yemba Express**, **DamouCargo**).
- **Sourcing Assisté** : Conseils sur les meilleures plateformes (**1688**, **Alibaba**, **AliExpress**).
- **Contacts de Confiance** : Liste de transitaires vérifiés avec leurs numéros WhatsApp au Cameroun et en Chine.

## Installation

```bash
pip install fastapi pydantic-settings uvicorn rich
```

## Utilisation

### Mode Console (Interactif)
Lancez l'IA directement dans votre terminal pour discuter :
```bash
python3 main.py
```
*Commande recommandée : "Fait un scan complet"*

### Mode API (Public en ligne)
Pour déployer l'IA en ligne en tant que plateforme publique :
1. Assurez-vous que `DEPLOY_MODE` est réglé sur `api` dans `prodigium_config.py`.
2. Déployez sur un service comme **Render**, **Railway** ou **Google Cloud Run**.
3. L'API exposera des endpoints pour le chat (`/chat`) et la documentation automatique (`/docs`).

## Structure Technique
- `main.py` : Serveur FastAPI et logique d'orchestration.
- `prodigium_agentarium.py` : Intelligence métier de l'assistant KmerSource.
- `prodigium_nexus.py` : Outils de scan logistique.
- `prodigium_config.py` : Configuration système.
