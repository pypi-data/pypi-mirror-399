import requests

def check_url_via_socks5(SOCKS5_proxy: str, proxy_port: int, URL: str, proxy_hostname: str = "Test", max_time=3, verbosity=2) -> bool:
    """
    Checks if a given URL can be reached through a SOCKS5 proxy within a specified timeout.
    
    Parameters:
        SOCKS5_proxy (str): IP address or hostname of the SOCKS5 proxy
        proxy_port (int): port of the SOCKS5 proxy
        URL (str): the URL to be tested
        max_time (int, optional): maximum waiting time in seconds (default=3)
        verbosity: verbosity in output to terminal
    
    Returns:
        bool: True if the page was successfully loaded, False otherwise
    """

    # Build proxy configuration using SOCKS5 with hostname resolution
    proxies = {
        'http': f'socks5h://{SOCKS5_proxy}:{proxy_port}',
        'https': f'socks5h://{SOCKS5_proxy}:{proxy_port}',
    }

    try:
        # Attempt to send GET request through the proxy with a timeout
        response = requests.get(URL, proxies=proxies, timeout=max_time)

        if verbosity > 0:
            print(f"[SUCCES] Hostname: {proxy_hostname}")
        
        if verbosity >= 2:
                print(f"\t Socks name & port: {SOCKS5_proxy}:{proxy_port}")    
                # add to list with working proxies        

        if verbosity >= 3:
            print(f"\t Status code: {response.status_code}")

        if verbosity >= 2:
            print("") # Print an empty line

        # Return True if HTTP response indicates success
        return True
    
    except requests.RequestException as e:
        # Handle network, timeout, or proxy errors
        if verbosity >= 1:
            print(f"[FAILED] Hostname: {proxy_hostname}")
          
        if verbosity >= 2:
            print(f"\t Socks name & Port: {SOCKS5_proxy}:{proxy_port}")    
        
        if verbosity >= 3:
            print(f"\t Request failed: {e}")

        if verbosity >= 2:
            print("\n")

        return False

def try_all_proxies_from_list (proxy_list: list, URL: str, max_time=3, verbosity=3) -> list:
    """
    Test all SOCKS5 proxies from the given list against a specific URL.

    This function iterates through each proxy in the provided proxy list and
    checks whether the URL can be successfully accessed through that proxy.
    Proxies that succeed are collected and returned.

    Parameters:
        proxy_list (list): A list of proxy dictionaries, each containing at least
                           'socks_name', 'socks_port', and 'hostname' keys.
        URL (str): the URL to be tested
        max_time (int, optional): maximum waiting time in seconds (default=3)
        verbosity: verbosity in output to terminal

    Returns:
        list: A list of proxy dictionaries that successfully accessed the URL.
    """

    # List to store the proxies in that can access the URL
    working_proxies_list = list()

    for proxy in proxy_list:
        if check_url_via_socks5(proxy["socks_name"], proxy["socks_port"], URL, proxy["hostname"], max_time, verbosity):
            # add to list with working proxies
            working_proxies_list.append(proxy)

    return working_proxies_list
    
