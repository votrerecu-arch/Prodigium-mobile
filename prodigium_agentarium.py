from typing import List, Tuple, Optional, Any
import asyncio

class Agent:
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization

    async def process(self, message: str) -> str:
        return f"[{self.name}] Je traite votre demande : {message}"

class KmerSourceAgent(Agent):
    def __init__(self):
        super().__init__("KmerSource", "Expert en sourcing et logistique Chine-Cameroun")
        self.contacts = {
            "WACO CARGO": {
                "description": "Spécialiste du fret aérien et maritime de la Chine vers le Cameroun.",
                "contacts": {
                    "Yaoundé": "+237 679 24 06 89 / 671 98 11 11",
                    "Douala": "+237 679 24 07 23 / 683 71 92 80",
                    "Chine": "+86 137 5420 2192"
                }
            },
            "Sino Shipping": {
                "description": "Transitaire international couvrant la route Chine-Afrique.",
                "site": "https://fr.sino-shipping.com"
            },
            "Handling and Transport SARL": {
                "description": "Accompagnement complet : sourcing, logistique et douane.",
                "site": "https://handlingandtransport.com"
            }
        }

    async def process(self, message: str) -> str:
        msg_lower = message.lower()

        if any(keyword in msg_lower for keyword in ["chine", "achat", "fournisseur", "commander", "alibaba", "1688"]):
            response = "### 🇨🇲 Guide d'Achat en Chine pour le Cameroun\n\n"
            response += "Pour réussir vos achats en Chine et vous faire livrer en toute sécurité au Cameroun, voici les étapes recommandées :\n\n"
            response += "1. **Sourcing** : Utilisez des plateformes fiables comme **Alibaba** (B2B), **1688.com** (meilleurs prix, nécessite un agent) ou **AliExpress**.\n"
            response += "2. **Paiement** : Utilisez Alipay, WeChat Pay (via agent) ou des cartes virtuelles internationales.\n"
            response += "3. **Expédition (Le Transitaire)** : C'est l'étape la plus cruciale. Voici des contacts sûrs qui livrent au Cameroun :\n\n"

            for name, info in self.contacts.items():
                response += f"#### {name}\n"
                response += f"- *Description* : {info['description']}\n"
                if "contacts" in info:
                    for loc, num in info["contacts"].items():
                        response += f"  - **{loc}** : {num}\n"
                if "site" in info:
                    response += f"  - **Site** : {info['site']}\n"
                response += "\n"

            response += "4. **Réception** : Vos colis arrivent généralement à Douala ou Yaoundé. Le transitaire gère souvent le dédouanement (système 'tout compris' au kg ou CBM).\n\n"
            response += "Avez-vous besoin d'un conseil spécifique sur un produit ou une plateforme ?"
            return response

        return "Je suis l'assistant KmerSource. Je peux vous aider à importer des marchandises depuis l'étranger, particulièrement de la Chine vers le Cameroun. Que souhaitez-vous acheter ?"

class Orchestrator:
    def __init__(self):
        self.agents = [
            KmerSourceAgent(),
            Agent("Logistique", "Expertise en transport international")
        ]
        self.agent_count = len(self.agents)

    async def route(self, message: str, auth: Any, thinking_mode: bool = False) -> Tuple[str, List[str], Optional[str]]:
        # Routage intelligent : si on parle d'achat/chine, on utilise KmerSource
        msg_lower = message.lower()
        target_agent = self.agents[1] # Logistique par défaut

        if any(keyword in msg_lower for keyword in ["chine", "achat", "fournisseur", "commander", "cameroun", "import"]):
            target_agent = self.agents[0] # KmerSource

        activated_agents = [target_agent.name]
        response = await target_agent.process(message)
        thinking = f"Activation de l'agent {target_agent.name} pour une expertise spécifique..." if thinking_mode else None

        return response, activated_agents, thinking
