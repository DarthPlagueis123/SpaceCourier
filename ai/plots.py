import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_history(history, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with open(history, newline='') as file:
        rows = list(csv.DictReader(file))
    if not rows:
        return
    plt.style.use('dark_background')
    for field, title, filename, color in (
        ('score', 'Episode score', 'score_history.png', '#84e3dc'),
        ('moving_average_score', 'Score: trailing 50 episodes', 'moving_average.png', '#f5cf84'),
        ('loss', 'Mean Huber loss per episode', 'loss.png', '#eaa298'),
        ('epsilon', 'Exploration probability', 'epsilon.png', '#b6a5e4')):
        valid = [r for r in rows if r[field]]
        fig, ax = plt.subplots(figsize=(9, 4.5), layout='constrained')
        ax.plot([int(r['episode']) for r in valid], [float(r[field]) for r in valid], color=color, linewidth=1)
        ax.set(title=title, xlabel='Completed training episode', ylabel=field.replace('_', ' ').title())
        ax.grid(alpha=.15)
        fig.savefig(output/filename, dpi=150)
        plt.close(fig)
