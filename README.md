# KmerSource AI 🇨🇲🇨🇳

Une intelligence artificielle complète pour aider les Camerounais à effectuer des achats à l'étranger (notamment en Chine) avec des contacts fiables et une livraison directe au Cameroun.

## 🌟 Plateforme Facile à Utiliser
L'application inclut désormais une **interface web conviviale**. Une fois lancée, ouvrez simplement votre navigateur sur `http://localhost:8000` pour discuter avec l'IA.

## 🚀 Déploiement Complet (Public en ligne)

Pour rendre cette IA publique et accessible à tous via un lien internet :

1. **GitHub** : Mettez ce code sur votre compte GitHub.
2. **Render** : Créez un compte sur [Render.com](https://render.com).
3. **Nouveau Web Service** : Connectez votre dépôt GitHub.
4. **Configuration** :
   - **Environment** : `Python`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Variables d'environnement** :
   - `DEPLOY_MODE` : `api`

Render vous fournira un lien public (ex: `https://kmersource-ai.onrender.com`) que vous pourrez partager.

## ✨ Fonctionnalités Clés
- **Scan complet** : Données à jour sur les tarifs de fret et les délais (Air/Mer).
- **Interface Web** : Chat interactif facile pour tous.
- **Sourcing** : Conseils sur 1688, Alibaba et AliExpress.
- **Contacts WhatsApp** : Transitaires vérifiés (WACO Cargo, etc.).

## Installation Locale

```bash
pip install -r requirements.txt
python3 main.py
```
