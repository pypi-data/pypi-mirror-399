import argparse
from .my_mcp_server import mcp


def main():
    """finicr doc process: read file and extract information from the file"""
    parser = argparse.ArgumentParser(
        description="provider the file url path."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()