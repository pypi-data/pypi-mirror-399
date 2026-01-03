import sys

from gunicorn.app.wsgiapp import run


def main():
    # uv run label-studio-paddleocr -- --workers 4 --log-level debug
    sys.argv = [
        "gunicorn",
        *sys.argv[1:],
        "label_studio_paddleocr._wsgi:app",
    ]

    run()


if __name__ == "__main__":
    main()
