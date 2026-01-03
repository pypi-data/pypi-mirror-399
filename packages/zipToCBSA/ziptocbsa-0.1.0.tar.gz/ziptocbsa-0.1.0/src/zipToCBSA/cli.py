import argparse
from .zipToCBSA import convert

def main():
    parser = argparse.ArgumentParser(description="Lookup OMB/HUD CBSA(s) associated with USPS ZIP Code")
    parser.add_argument("zip", help="5-digit ZIP code")
    args = parser.parse_args()

    result = convert(args.zip)
    print(result)

if __name__ == "__main__":
    main()
