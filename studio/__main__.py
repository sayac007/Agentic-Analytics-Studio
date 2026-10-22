"""Run or verify the fixed Stage-A synthetic benchmark."""
import argparse
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run')
    run.add_argument('--output',type=Path,required=True,help='New output directory; existing paths are never overwritten')
    verify=sub.add_parser('verify')
    verify.add_argument('directory',type=Path)
    args=parser.parse_args()
    if args.command=='run':
        from .pipeline import run
        root=run(args.output)
        print(f'Validated synthetic Stage-A bundle: {root}')
    else:
        from .evaluate import verify_bundle
        verify_bundle(args.directory.resolve())
        print('Bundle hashes, contracts and holdout predictions verified')


if __name__=='__main__':
    main()
