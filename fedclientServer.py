from client import app
from flask_restful import Api, Resource
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Train a MMFed detector')
    parser.add_argument('ip', help='client ip')
    parser.add_argument('port', help='client port')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    api = Api(app)
    app.run(host=args.ip, port=args.port, debug=False)