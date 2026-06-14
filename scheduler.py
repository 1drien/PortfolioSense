# ============================================================
#  PortfolioSense — Scheduler automatique
#  Met a jour tous les modules chaque soir a 23h
#  Lancer une fois : python scheduler.py
# ============================================================

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import subprocess
import sys
import os

scheduler = BlockingScheduler()

def run(script):
    """Lance un script Python et affiche le resultat."""
    print(f"\n  > {script}...")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, "-X", "utf8", script],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env=env
    )
    if result.returncode == 0:
        print(f"  OK  {script} termine")
    else:
        print(f"  ERREUR dans {script} :")
        print(result.stderr[:500])

@scheduler.scheduled_job('cron', hour=23, minute=0)
def update_all():
    print(f"\n{'='*50}")
    print(f"  PortfolioSense -- Mise a jour automatique")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*50}")

    # 1. Data (toujours en premier)
    run("data/pipeline.py")
    run("data/stress_tests.py")
    run("data/drawdown.py")
    run("data/attribution.py")

    # 2. Optimisation
    if os.path.exists("optimization/optimizer.py"):
        run("optimization/optimizer.py")

    # 3. Risque
    if os.path.exists("risk/var.py"):
        run("risk/var.py")
    if os.path.exists("risk/backtest.py"):
        run("risk/backtest.py")

    # 4. ML
    if os.path.exists("ml/regimes.py"):
        run("ml/regimes.py")
    if os.path.exists("ml/shap_explainer.py"):
        run("ml/shap_explainer.py")

    print(f"\n  OK Mise a jour complete -- {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    print("PortfolioSense Scheduler demarre")
    print("Mise a jour automatique tous les soirs a 23h00")
    print("ATTENTION : l'ordinateur doit rester allume")
    print("Pour arreter : Ctrl+C\n")

    reponse = input("Lancer une mise a jour maintenant ? (o/n) : ")
    if reponse.lower() == "o":
        update_all()

    scheduler.start()