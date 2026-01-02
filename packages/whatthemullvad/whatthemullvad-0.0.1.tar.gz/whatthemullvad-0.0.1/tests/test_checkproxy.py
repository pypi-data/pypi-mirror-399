from whatthemullvad.checkproxy import check_url_via_socks5

def test_check_url_via_socks5():
    test_ip = "al-tia-wg-socks5-003.relays.mullvad.net"
    test_port = 1080
    test_url = "https://www.antoniusstramproy.nl/fotos-2024/"
    test_timeout = 5
    test_result = check_url_via_socks5(test_ip, test_port, test_url)
    print(test_result)

test_check_url_via_socks5()