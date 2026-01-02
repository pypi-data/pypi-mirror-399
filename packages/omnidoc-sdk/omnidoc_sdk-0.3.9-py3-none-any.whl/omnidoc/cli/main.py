import argparse
from omnidoc.pdf.pipeline import extract_pdf

def main():
    parser = argparse.ArgumentParser("omnidoc")
    parser.add_argument("command", choices=["extract"])
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "extract":
        doc = extract_pdf(args.file)
        if args.json:
            print(doc)
        else:
            print(doc.raw_text)

if __name__ == "__main__":
    main()
