import argparse

from whatthemullvad.mullvad_proxies_api import load_proxies_mullvad_api
from whatthemullvad.checkproxy import check_url_via_socks5, try_all_proxies_from_list

max_time = 3

def main():
    """
    Entry point for WhatTheMullvad command line tool.
    Handles command line arguments and controls verbosity, output file, and proxy filtering.
    """

    # --- Parse command line arguments ---
    parser = argparse.ArgumentParser(
        description="Test if Mullvad SOCKS5 proxies can access for a given URL.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-v", "--verbosity",
        default="2",
        help="Verbosity level: (0, 0.5/s, 1, 2, 3). \n" + 
             "Default = 2. \n" + 
             "Use 's' or 0.5 to only show succesful proxies."
    )

    #parser.add_argument(
    #    "-o", "--output",
    #    dest="output_filename",
    #    help="Output filename for results."
    #)

    #parser.add_argument(
    #    "-c", "--country",
    #    dest="country_code",
    #    help="Filter proxies by country code (e.g. 'NL', 'SE', 'US')."
    #)

    parser.add_argument(
        "url",
        help="The URL to test via Mullvad SOCKS5 proxies."
    )

    args = parser.parse_args()

    # --- Handle verbosity conversion ---
    if args.verbosity.lower() == "s":
        verbosity = 0.5
    else:
        try:
            verbosity = float(args.verbosity)

            if not(verbosity == 0.5 or verbosity == 1 or verbosity == 2 or verbosity == 3):
                print("[ERROR] Invalid verbosity value. Must be 0, 0.5, 1, 2, 3 or 's'.")
                return

        except ValueError:
            print("[ERROR] Invalid verbosity value. Must be 0, 0.5, 1, 2, 3 or 's'.")
            return

    # --- Load proxies ---
    proxy_list = load_proxies_mullvad_api(verbosity)

    # --- Filter by country if requested ---
    #if args.country_code:
    #    proxy_list = [
    #        p for p in proxy_list if p.get("country_code", "").lower() == args.country_code.lower()
    #    ]
    #    if verbosity >= 1:
    #        print(f"[INFO] Using proxies from country: {args.country_code.upper()} ({len(proxy_list)} found)")

    # --- Test proxies ---
    working_proxies = try_all_proxies_from_list(proxy_list, args.url, max_time, verbosity)

    # --- Handle output ---
    #if args.output_filename:
    #    try:
    #        with open(args.output_filename, "w") as f:
    #            for r in results:
    #                f.write(f"{r}\n")
    #        if verbosity >= 1:
    #            print(f"[INFO] Results saved to {args.output_filename}")
    #    except Exception as e:
    #        print(f"[ERROR] Could not write to output file: {e}")

if __name__ == "__main__":
    main()