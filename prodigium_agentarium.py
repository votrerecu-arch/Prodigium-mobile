from typing import List, Tuple, Optional, Any
import asyncio
from prodigium_nexus import Nexus

class Agent:
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization

    async def process(self, message: str) -> str:
        return f"[{self.name}] Je traite votre demande : {message}"

class KmerSourceAgent(Agent):
    def __init__(self):
        super().__init__("KmerSource", "Expert en sourcing et logistique Chine-Cameroun")
        self.nexus = Nexus()
        self.contacts = {
            "WACO CARGO": {
                "description": "Fret aérien et maritime. Très fiable.",
                "contacts": {
                    "Yaoundé (Hollando)": "+237 679 24 06 89",
                    "Douala (Akwa)": "+237 679 24 07 23",
                    "Chine": "+86 137 5420 2192"
                }
            },
            "Handling and Transport": {
                "description": "Sourcing, logistique et dédouanement.",
                "site": "https://handlingandtransport.com"
            }
        }

    async def process(self, message: str) -> str:
        msg_lower = message.lower()

        if any(keyword in msg_lower for keyword in ["scan", "jour", "donnée", "donnee"]):
            scan_result = await self.nexus.live_logistics_scan()
            data = scan_result["data"]
            platform = data["top_platform"]

            response = "### 🔍 Résultats du Scan en Temps Réel (Chine-Cameroun)\n\n"
            response += f"Dernière mise à jour : {scan_result['timestamp']}\n\n"
            response += f"**1. Plateforme de référence (Facile et Public) :**\n"
            response += f"👉 **[{platform['name']}]({platform['url']})**\n"
            response += f"- *Description* : {platform['description']}\n\n"

            response += "**2. Alternatives pour le suivi de colis :**\n"
            for alt in data["alternative_tracking"]:
                response += f"- [{alt['name']}]({alt['url']})\n"

            response += f"\n**3. État du Marché :**\n"
            response += f"- **Tarifs** : {data['rates_trend']}\n"
            response += f"- **Délais** : {data['average_delivery']}\n"
            response += f"- **Sourcing recommandé** : {', '.join(data['recommended_sourcing'])}\n\n"
            response += "Utilisez ces liens pour vos achats et le suivi de vos marchandises."
            return response

        if any(keyword in msg_lower for keyword in ["chine", "achat", "fournisseur", "commander", "alibaba", "1688", "aide"]):
            response = "### 🇨🇲 Comment acheter en Chine depuis le Cameroun\n\n"
            response += "Voici les meilleures ressources pour vos achats :\n\n"
            response += "1. **Sourcing** : Utilisez **1688.com** pour les meilleurs prix d'usine ou **Alibaba**.\n"
            response += "2. **Logistique (Contacts Sûrs)** :\n\n"

            for name, info in self.contacts.items():
                response += f"#### {name}\n"
                response += f"- {info['description']}\n"
                if "contacts" in info:
                    for loc, num in info["contacts"].items():
                        response += f"  - **{loc}** : {num}\n"
                if "site" in info:
                    response += f"  - **Site** : {info['site']}\n"
                response += "\n"

            response += "3. **Suivi & Plateforme En Ligne** :\n"
            response += "Pour suivre vos colis en temps réel, utilisez la plateforme publique :\n"
            response += "👉 **[Yemba Express](https://yemba.com)**\n\n"
            response += "Dites-moi **'scan complet'** pour obtenir les tarifs et délais à jour."
            return response

        return "Je suis l'assistant KmerSource. Je vous aide pour vos achats à l'étranger. Essayez de demander un 'scan complet'."

class Orchestrator:
    def __init__(self):
        self.agents = [
            KmerSourceAgent(),
            Agent("Logistique", "Expertise en transport international")
        ]
        self.agent_count = len(self.agents)

    async def route(self, message: str, auth: Any, thinking_mode: bool = False) -> Tuple[str, List[str], Optional[str]]:
        msg_lower = message.lower()
        target_agent = self.agents[1]

        if any(keyword in msg_lower for keyword in ["chine", "achat", "fournisseur", "commander", "cameroun", "import", "scan", "jour", "aide"]):
            target_agent = self.agents[0]

        activated_agents = [target_agent.name]
        response = await target_agent.process(message)
        thinking = f"Analyse par l'agent {target_agent.name}..." if thinking_mode else None

        return response, activated_agents, thinking
