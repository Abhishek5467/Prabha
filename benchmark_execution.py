"""Benchmark the frozen CNN's sampled and constant-symbol execution modes."""
from pathlib import Path
import argparse
import csv
import json
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=360)
    parser.add_argument('--blocks', type=int, default=5)
    parser.add_argument('--warmups', type=int, default=1)
    parser.add_argument('--threads', type=int, choices=range(1, 65), default=1)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    for name in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS']:
        os.environ[name] = str(args.threads)
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / 'core-py'))
    from prabha.systems.cnn_benchmark import benchmark
    from prabha.product import VERSION
    out = args.out or root / 'results' / 'release_benchmarks' / ('run_' + str(time.time_ns()))
    if out.exists():
        raise SystemExit('Output already exists. Choose a fresh --out directory.')
    out.mkdir(parents=True)
    result = benchmark(root, {'count': args.count, 'blocks': args.blocks, 'warmups': args.warmups})
    result['software_version'] = VERSION
    (out / 'benchmark.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    with (out / 'timings.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['block', 'order', 'method', 'seconds'])
        writer.writeheader(); writer.writerows(result['rows'])
    print(json.dumps({'results_folder': str(out), 'count': result['count'], 'blocks': result['blocks'],
                      'median_seconds': result['median_seconds'],
                      'waveform_over_symbol': result['waveform_over_symbol'],
                      'maximum_logit_difference': result['maximum_symbol_waveform_logit_difference'],
                      'claim_scope': result['claim_scope']}, indent=2))


if __name__ == '__main__':
    main()
