from whatthemullvad.mullvad_proxies_api import load_proxies_mullvad_api

def test_load_proxies_mullvad_api():
    test_proxy_list = load_proxies_mullvad_api()
    #print(test_proxy_list)
    for proxy in test_proxy_list:
        print(proxy)

test_load_proxies_mullvad_api()