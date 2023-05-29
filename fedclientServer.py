from client import app
from flask_restful import Api
import argparse
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

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