# WhatTheMullvad
Test if Mullvad SOCKS5 proxies can access a given URL.

## Disclaimer
Neither I nor this project is affiliated with [Mullvad](https://mullvad.net/en).
I created this tool for personal use, and I'm sharing it hoping other people may benefit from it.

## Description
Some websites block certain Mullvad IP-addresses. 
You can use the [Mullvad Browser](https://mullvad.net/en/browser) or the [Mullvad Browser Extension (beta)](https://mullvad.net/en/download/browser/extension) to use a Mullvad server that isn't blocked.
However, manually trying each Mullvad proxy to find out which ones aren't being blocked can be quite cumbersome.
You can use this tool to find out which Mullvad proxies work for a certain website, and which ones don't.

## Usage
```
python3 -m src.main [-h] [-v VERBOSITY] url
```
```
positional arguments:
  url                   The URL to test via Mullvad SOCKS5 proxies.

options:
  -h, --help            show this help message and exit
  -v VERBOSITY, --verbosity VERBOSITY
                        Verbosity level: (0, 0.5/s, 1, 2, 3). 
                        Default = 2. 
                        Use 's' or 0.5 to only show succesful proxies.
```

## Roadmap
- [ ] Adding the option to output to files
    - Multiple file formats
- [ ] Adding the option to filter by countrycode
- [ ] Adding the option to use a custom proxy list
