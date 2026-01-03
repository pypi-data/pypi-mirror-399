import argparse
import json

from .server import JupyterServer


def main():
    parser = argparse.ArgumentParser("apibean-jupyter")
    parser.add_argument("--root", help="Notebook root directory")
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int)
    parser.add_argument("--token")
    parser.add_argument("--no-lab", action="store_true")
    parser.add_argument("--info", action="store_true")

    args = parser.parse_args()

    server = JupyterServer(
        root_dir=args.root,
        ip=args.ip,
        port=args.port,
        token=args.token,
        lab=not args.no_lab,
    )

    if args.info:
        print(json.dumps(server.info, indent=2))
        return

    print(f"🚀 Jupyter starting at: {server.url}")
    server.start(blocking=True)
