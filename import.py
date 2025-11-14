# Script à exécuter dans votre terminal Python (pas dans Django)

import pyhanko

# Liste des modules courants où SimpleTrustRoot pourrait se trouver
potential_modules = [
    'pyhanko.keys', 
    'pyhanko.signatures.api',
    'pyhanko.pdf_utils.crypt.api',
    'pyhanko.sign.validation' # Très rare, mais possible
]

print("--- Tentative de localisation de SimpleTrustRoot ---")

found = False
for module_name in potential_modules:
    try:
        module = __import__(module_name, fromlist=['SimpleTrustRoot'])
        if hasattr(module, 'SimpleTrustRoot'):
            print(f"✅ TROUVÉ : from {module_name} import SimpleTrustRoot")
            found = True
            break
    except ImportError:
        # Poursuit la recherche
        pass

if not found:
    print("❌ ÉCHEC : SimpleTrustRoot n'a été trouvé dans aucune localisation courante.")

print("--------------------------------------------------")
