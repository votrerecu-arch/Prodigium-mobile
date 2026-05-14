# KmerSource AI 🇨🇲🇨🇳

Une intelligence artificielle conçue pour aider les Camerounais à effectuer des achats à l'étranger (notamment en Chine) avec des contacts fiables et une livraison directe au Cameroun.

## Fonctionnalités
- **Sourcing** : Conseils sur les meilleures plateformes (Alibaba, 1688, etc.).
- **Logistique** : Liste de transitaires fiables (WACO CARGO, Sino Shipping, etc.) avec contacts WhatsApp/Téléphone.
- **Accompagnement** : Guide étape par étape du paiement à la réception du colis à Douala ou Yaoundé.

## Installation

```bash
pip install fastapi pydantic-settings uvicorn rich
```

## Utilisation

### Mode Console (Interactif)
Lancez l'IA directement dans votre terminal :
```bash
python3 main.py
```

### Mode API
Pour lancer le serveur API :
1. Modifiez `prodigium_config.py` ou définissez `DEPLOY_MODE=api`.
2. Lancez :
```bash
python3 main.py
```
L'API sera disponible sur `http://localhost:8000`. La documentation Swagger est accessible sur `/docs`.

## Structure du projet
- `main.py` : Point d'entrée de l'application.
- `prodigium_agentarium.py` : Orchestrateur et agents spécialisés (dont KmerSource).
- `prodigium_config.py` : Paramètres du système.
- `prodigium_models.py` : Modèles de données Pydantic.
