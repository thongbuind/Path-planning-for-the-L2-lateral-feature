import argparse
from pathlib import Path
from eval import openx


def main():
    parser = argparse.ArgumentParser(
        description="Validate ASAM XML against the vendored official schemas, without network access.",
    )
    parser.add_argument('paths', type=Path, nargs='*', default=[openx.ROOT / 'benchmark'])
    args = parser.parse_args()
    files = sorted({f for p in args.paths for f in (p.rglob('*') if p.is_dir() else [p])
                    if f.suffix in ('.xosc', '.xodr')})
    if not files:
        parser.error('no .xosc or .xodr files found')
    for path in files:
        openx.validate(path)
    print(f'{len(files)} files pass ASAM OpenSCENARIO 1.3.1 / OpenDRIVE 1.8.1 XSD')


if __name__ == '__main__':
    main()
