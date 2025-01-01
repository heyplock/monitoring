import subprocess
import time
import re
import threading
import platform
import os
import sys

# Activer les séquences ANSI pour les couleurs dans l'invite de commande Windows
if platform.system() == "Windows":
    os.system("")

# Codes de couleur ANSI
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"

def ping_ip(ip):
    """Effectue un ping sur l'IP et retourne la sortie."""
    try:
        command = ["ping", "-n", "1", ip] if platform.system() == "Windows" else ["ping", "-c", "1", ip]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"{Colors.RED}Erreur lors du ping : {e}{Colors.RESET}")
        return None

def parse_ping_output(output):
    """Analyse la sortie d'un seul ping et retourne la latence."""
    avg_time = None

    # Extraire les temps de latence
    time_match = re.search(r"(temps|time)=([\d.]+)\s?ms", output)
    if time_match:
        avg_time = float(time_match.group(2))  # Temps moyen pour un ping unique
    
    return avg_time

def colorize_latency(value, average):
    """Retourne une couleur basée sur l'écart à la moyenne."""
    if value is None:
        return f"{Colors.RED}N/A{Colors.RESET}"
    diff = abs(value - average)
    if diff <= 10:  # Proche de la moyenne
        return f"{Colors.GREEN}{value:.2f} ms{Colors.RESET}"
    elif diff <= 30:  # Moyennement éloigné
        return f"{Colors.YELLOW}{value:.2f} ms{Colors.RESET}"
    else:  # Très éloigné
        return f"{Colors.RED}{value:.2f} ms{Colors.RESET}"

def monitor_ping(ip):
    """Effectue le monitoring du ping pour une IP donnée."""
    print(f"{Colors.CYAN}{Colors.BOLD}--- Monitoring de {ip} ---{Colors.RESET}")
    start_time = time.time()
    stop_monitoring = [False]

    # Variables pour stocker les statistiques cumulées
    total_packets = 0
    lost_packets = 0
    latencies = []

    def listen_for_stop():
        """Écoute l'appui sur la touche Entrée pour arrêter le monitoring."""
        input(f"{Colors.YELLOW}\nAppuyez sur Entrée pour arrêter le monitoring...{Colors.RESET}\n")
        stop_monitoring[0] = True

    thread = threading.Thread(target=listen_for_stop)
    thread.daemon = True
    thread.start()

    print(f"{Colors.BOLD}Résultats en temps réel :{Colors.RESET}")
    while not stop_monitoring[0]:
        output = ping_ip(ip)
        if output:
            total_packets += 1
            avg_time = parse_ping_output(output)
            if avg_time is not None:
                latencies.append(avg_time)
                overall_avg = sum(latencies) / len(latencies)
                sys.stdout.write(
                    f"\rPing #{total_packets}: {colorize_latency(avg_time, overall_avg)}    "
                )
                sys.stdout.flush()
            else:
                lost_packets += 1
                sys.stdout.write(f"\r{Colors.RED}Ping #{total_packets}: Échec{Colors.RESET}    ")
                sys.stdout.flush()
        else:
            lost_packets += 1
            sys.stdout.write(f"\r{Colors.RED}Ping #{total_packets}: Échec{Colors.RESET}    ")
            sys.stdout.flush()
        time.sleep(1)

    # Une fois que l'utilisateur a arrêté le monitoring, on affiche les stats
    end_time = time.time()
    print("\n")  # Passer à la ligne après le monitoring

    if latencies:
        overall_min = min(latencies)
        overall_max = max(latencies)
        overall_avg = sum(latencies) / len(latencies)
    else:
        overall_min = overall_max = overall_avg = None

    print(f"\n{Colors.CYAN}{Colors.BOLD}--- Résumé du Monitoring ---{Colors.RESET}")
    print(f"IP du lien pingé : {ip}")
    print(f"Temps total passé à pinger : {end_time - start_time:.2f} secondes")
    print(f"Nombre de paquets envoyés : {total_packets}")
    print(f"Nombre de paquets perdus : {Colors.RED}{lost_packets}{Colors.RESET}" if lost_packets else f"{Colors.GREEN}{lost_packets}{Colors.RESET}")

    if overall_avg is not None:
        print(f"Latence minimale : {colorize_latency(overall_min, overall_avg)}")
        print(f"Latence moyenne : {Colors.BOLD}{overall_avg:.2f} ms{Colors.RESET}")
        print(f"Latence maximale : {colorize_latency(overall_max, overall_avg)}")
    else:
        print(f"{Colors.RED}Aucune latence enregistrée (échec des pings).{Colors.RESET}")

def main():
    print(f"{Colors.CYAN}{Colors.BOLD}Bienvenue dans l'outil de monitoring !{Colors.RESET}")
    while True:
        ip = input("\nVeuillez entrer l'adresse IP à monitorer (ou 'q' pour quitter) : ").strip()
        if ip.lower() == "q":
            print(f"{Colors.GREEN}Fermeture de l'application. Au revoir !{Colors.RESET}")
            break
        monitor_ping(ip)

if __name__ == "__main__":
    main()
