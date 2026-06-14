# ============================================================
#  PortfolioSense — Scheduler automatique
#  Met à jour tous les modules chaque soir à 23h
#  Lancer une fois : python scheduler.py
# ============================================================

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import subprocess
import sys
import os

scheduler = BlockingScheduler()

def run(script):
    """Lance un script Python et affiche le résultat."""
    print(f"\n  ▸ {script}...")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ {script} terminé")
    else:
        print(f"  ❌ Erreur dans {script} :")
        print(result.stderr)

@scheduler.scheduled_job('cron', hour=23, minute=0)
def update_all():
    """
    Met à jour tous les modules dans l'ordre chaque soir à 23h.
    L'ordre est important — chaque module dépend du précédent.
    """
    print(f"\n{'='*50}")
    print(f"  PortfolioSense — Mise à jour automatique")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*50}")

    # 1. Data (toujours en premier — tout le monde en dépend)
    run("data/pipeline.py")
    run("data/stress_tests.py")
    run("data/drawdown.py")
    run("data/attribution.py")

    # 2. Optimisation (dépend des données)
    if os.path.exists("optimization/main.py"):
        run("optimization/main.py")

    # 3. Risque (dépend de l'optimisation)
    if os.path.exists("risk/main.py"):
        run("risk/main.py")

    # 4. ML (dépend de tout)
    if os.path.exists("ml/main.py"):
        run("ml/main.py")

    print(f"\n  Mise à jour complète — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    print("PortfolioSense Scheduler démarré")
    print("Mise à jour automatique tous les soirs à 23h00")
    print("⚠  L'ordinateur doit rester allumé pour que le scheduler fonctionne")
    print("Pour arrêter : Ctrl+C\n")

    # Lance aussi une mise à jour immédiate au démarrage
    reponse = input("Lancer une mise à jour maintenant ? (o/n) : ")
    if reponse.lower() == "o":
        update_all()

    scheduler.start()