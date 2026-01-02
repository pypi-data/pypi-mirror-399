import requests

def load_proxies_mullvad_api(verbosity=2):
    """
    Load proxies from Mullvad Wireguard API endpoint.

    Returns:
        list of dict: A list of proxies where each proxy is a dictionary containing
                      'hostname', 'country_code', 'socks_name', and 'socks_port'.
    """

    if verbosity >= 2:
        print("Loading all proxies from Mullvad API...")

    mullvad_api_url = "https://api.mullvad.net/www/relays/wireguard/"
    proxy_list = []

    try:
        response = requests.get(mullvad_api_url, timeout=5)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        # Iterate over each relay object in the JSON response
        for relay in data:
            if relay.get("active") is True:
                proxy = {
                    "hostname": relay.get("hostname"),
                    "country_code": relay.get("country_code"),
                    "socks_name": relay.get("socks_name"),
                    "socks_port": relay.get("socks_port"),
                }
                proxy_list.append(proxy)

    except (requests.RequestException, ValueError) as e:
        # If there is an error during request or JSON parsing: print error
        print(f"[ERROR] Something went wrong while loading proxies from Mullvad API: {e}")

    if verbosity >= 2:
        print("Loaded all proxies from Mullvad API\n")

    return proxy_list




