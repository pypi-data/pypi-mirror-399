import argparse
import logging
import os
import sys

from label_studio_ml.api import init_app

from label_studio_paddleocr.model import PaddleOCR


def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)-5s [%(name)s::%(funcName)s::%(lineno)d] : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Label studio PaddleOCR")
    parser.add_argument(
        "-p", "--port", dest="port", type=int, default=9090, help="Server port"
    )
    parser.add_argument(
        "--host", dest="host", type=str, default="0.0.0.0", help="Server host"
    )
    parser.add_argument(
        "--kwargs",
        "--with",
        dest="kwargs",
        metavar="KEY=VAL",
        nargs="+",
        type=lambda kv: kv.split("="),
        help="Additional LabelStudioMLBase model initialization kwargs",
    )
    parser.add_argument(
        "-d", "--debug", dest="debug", action="store_true", help="Switch debug mode"
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--model-dir",
        dest="model_dir",
        default=os.path.dirname(__file__),
        help="Directory where models are stored (relative to the project directory)",
    )
    parser.add_argument(
        "--check",
        dest="check",
        action="store_true",
        help="Validate model instance before launching server",
    )
    parser.add_argument(
        "--basic-auth-user",
        default=os.environ.get("ML_SERVER_BASIC_AUTH_USER", None),
        help="Basic auth user",
    )
    parser.add_argument(
        "--basic-auth-pass",
        default=os.environ.get("ML_SERVER_BASIC_AUTH_PASS", None),
        help="Basic auth pass",
    )
    return parser.parse_args()


def main():
    init_logging()

    args = parse_args()

    # setup logging level
    if args.log_level:
        logging.root.setLevel(args.log_level)

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def parse_kwargs():
        param = dict()
        for k, v in args.kwargs:
            if v.isdigit():
                param[k] = int(v)
            elif v == "True" or v == "true":
                param[k] = True
            elif v == "False" or v == "false":
                param[k] = False
            elif isfloat(v):
                param[k] = float(v)
            else:
                param[k] = v
        return param

    kwargs = dict()

    if args.kwargs:
        kwargs.update(parse_kwargs())

    if args.check:
        print('Check "' + PaddleOCR.__name__ + '" instance creation..')
        PaddleOCR(**kwargs)

    app = init_app(
        model_class=PaddleOCR,
        basic_auth_user=args.basic_auth_user,
        basic_auth_pass=args.basic_auth_pass,
    )

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
else:
    # for uWSGI use
    app = init_app(model_class=PaddleOCR)
