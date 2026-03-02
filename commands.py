def handle_command(command: str) -> str:
    command = command.lower()

    if command.startswith("/deploy"):
        return "🚀 Déploiement lancé (simulation)"
    elif command == "/cluster status":
        return "📊 Cluster OK (simulation)"
    elif command == "/alerts":
        return "🚨 Aucune alerte critique"
    else:
        return "❓ Commande inconnue"
