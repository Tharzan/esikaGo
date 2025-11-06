from hedera import (
    Client, PrivateKey, AccountId,
    TopicCreateTransaction, Status
)
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv() 

# 1. Configuration du Client 
OPERATOR_ID = AccountId.fromString(os.environ["MY_ACCOUNT_ID"])
OPERATOR_KEY = PrivateKey.fromString(os.environ["MY_PRIVATE_KEY"])

client = Client.forTestnet()
client.setOperator(OPERATOR_ID, OPERATOR_KEY)

# 2. Construction de la Transaction de Création de Topic
print("Tentative de création d'un nouveau Topic HCS sur le Testnet...")

transaction = (
    TopicCreateTransaction()
    # note (memo) pour identifier le Topic
    .setTopicMemo("Preuve de Document (PoD) de Tharcisse")
)

# 3. Signature, Soumission, et Récupération du Reçu
tx_response = transaction.execute(client)


receipt = tx_response.getReceipt(client)

# 4. Affichage du Résultat
if receipt.status == Status.SUCCESS:
    # 🚨 C'est ici que l'ID du nouveau Topic est créé !
    new_topic_id = receipt.topicId.toString()
    
    print("\n---------------------------------------")
    print("✅ TOPIC HCS CRÉÉ AVEC SUCCÈS !")
    print(f"L'ID du Topic HCS est : {new_topic_id}")
    print("---------------------------------------")
    
    print(f"\n💡 Copiez cet ID : vous l'utiliserez comme HCS_TOPIC_ID dans .env pour le hash.")
else:
    print(f"❌ ÉCHEC DE LA CRÉATION DU TOPIC. Statut : {receipt.status.toString()}")