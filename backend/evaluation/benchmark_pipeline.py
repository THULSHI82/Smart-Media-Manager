"""Measure preprocessing/storage optimisation and core image-analysis time.

Usage:
    python evaluation/benchmark_pipeline.py /path/to/photo1.jpg /path/to/photo2.jpg

The script prints measured values from the supplied files. It does not invent accuracy
metrics and it does not require the Flask server to be running.
"""
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.blur_service import analyse_blur
from services.classification_service import classify_image
from services.duplicate_service import compute_phash
from services.preprocessing_service import prepare_event_image


def measure(path: Path) -> dict:
    raw = path.read_bytes()
    start = perf_counter()
    prepared = prepare_event_image(raw)
    preprocessing_ms = (perf_counter() - start) * 1000

    start = perf_counter()
    blur = analyse_blur(prepared.original)
    phash = compute_phash(prepared.original)
    classification = classify_image(prepared.ai_image, face_count=0)
    analysis_ms = (perf_counter() - start) * 1000

    original = len(raw)
    optimised = len(prepared.optimized_bytes)
    saving = max(0.0, (1 - optimised / max(original, 1)) * 100)
    return {
        'file': path.name,
        'original_bytes': original,
        'optimized_bytes': optimised,
        'storage_saving_percent': round(saving, 2),
        'preprocessing_ms': round(preprocessing_ms, 2),
        'core_analysis_ms': round(analysis_ms, 2),
        'blur_score': blur['score'],
        'is_blurry': blur['is_blurry'],
        'perceptual_hash': phash,
        'classification_label': classification['label'],
        'classification_backend': classification['backend'],
    }


if __name__ == '__main__':
    files = [Path(item).expanduser() for item in sys.argv[1:]]
    files = [item for item in files if item.is_file()]
    if not files:
        print('Provide one or more JPEG/PNG/WebP image paths.')
        raise SystemExit(2)

    results = [measure(path) for path in files]
    for result in results:
        print(result)

    print({
        'files': len(results),
        'average_preprocessing_ms': round(sum(x['preprocessing_ms'] for x in results) / len(results), 2),
        'average_core_analysis_ms': round(sum(x['core_analysis_ms'] for x in results) / len(results), 2),
        'average_storage_saving_percent': round(sum(x['storage_saving_percent'] for x in results) / len(results), 2),
    })
