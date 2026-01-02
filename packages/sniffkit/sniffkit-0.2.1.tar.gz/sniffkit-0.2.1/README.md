# sniffkit

Tool for extracting live HLS (`.m3u8`) stream URLs from dynamically loaded web players using browser performance logs.

## Install
pip install sniffkit

## Usage
sniffkit -g  "<url>"
sniffkit -ok "<url>"

Flags:
- -g   Generic extractor
- -ok  for (mobile Safari context)

## Python
from sniffkit.core import sniff_m3u8_g
from sniffkit.okru import okru_m3u8p

## Notes
- URLs may be temporary or IP-bound
- No content is downloaded

## Disclaimer
Use this tool only on sites you are allowed to use. 
You are responsible for complying with applicable laws and terms of service.

## License
Copyright © 2025 Shadi Kabajah.
Permission is granted to use this software for personal, non-commercial purposes only.
Copying, modification, or redistribution is not permitted.