from urllib.request import urlopen
from urllib.error import *
import requests
from time import sleep 
import os
import sys

import configs as cfg


def check_api_status(api:str, tries:str = 1)-> str:
	for _ in range(tries):
		web_val = ""
		# sleep(10)
		try:
				html = urlopen(api)
		except HTTPError as e:
				print("HTTPError", e.args[0])
		except URLError as e:
				print("Page not found !!!", e.args[0])
		else:
				web_val = len(html.read())
				print("Page up and running.")
	else:
		return web_val


def url_response(url: str) -> str:
  try:
   response = requests.head(url)
    # response = requests.head(url)
  except Exception as e:
    raise HTTPError
  else:
    if 'error' in response:
            return response.status
    else:
            return response
        

def main():
    for server in cfg.eks_ips.keys():
        resp = url_response(cfg.eks_ips[server]).status_code
        print(server, " has status code ", cfg.error_codes[resp])


if __name__ == "__main__":
    main()