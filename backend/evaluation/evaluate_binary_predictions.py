"""Calculate reproducible binary metrics for face, blur or duplicate predictions.

CSV format: actual,predicted where each value is 0 or 1.
Usage: python evaluation/evaluate_binary_predictions.py results.csv
"""
import csv
import sys


def metrics(path: str):
    tp = tn = fp = fn = 0
    with open(path, newline='', encoding='utf-8') as handle:
        for row in csv.DictReader(handle):
            actual, predicted = int(row['actual']), int(row['predicted'])
            if actual == 1 and predicted == 1: tp += 1
            elif actual == 0 and predicted == 0: tn += 1
            elif actual == 0 and predicted == 1: fp += 1
            elif actual == 1 and predicted == 0: fn += 1
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return {'sample_size': total, 'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python evaluation/evaluate_binary_predictions.py results.csv')
    for key, value in metrics(sys.argv[1]).items():
        print(f'{key}: {value:.4f}' if isinstance(value, float) else f'{key}: {value}')
