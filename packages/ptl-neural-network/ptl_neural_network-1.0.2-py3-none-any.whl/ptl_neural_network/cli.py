from . import run, train
import argparse

def main():
    parser = argparse.ArgumentParser(prog="ptl-neural-network")
    sub = parser.add_subparsers(dest="command", required=True)

    p_a = sub.add_parser("train", help="Trains a neural network.")
    p_a.set_defaults(func=run.main)

    p_b = sub.add_parser("run", help="Runs a neural network.")
    p_b.set_defaults(func=train.main)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
