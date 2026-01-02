import logging
import sys
from typing import Any
from time import sleep
from yaml import safe_load

logger = logging.getLogger(__name__)

def fetch_prop() -> dict[str, Any]:
    try:
        with open('tables.yaml', 'r') as tblinfo:
            prop_dict = safe_load(tblinfo.read())
    except Exception as e:
        logger.critical(f"Error occured for config file 'tables.yaml' : {str(e)}")
        sleep(1)
        sys.exit(1)

    return prop_dict


def fetch_conf() -> dict[str, Any]:
    try:
        with open('config.yaml', 'r') as cfginfo:
            conf_dict = safe_load(cfginfo.read())
    except Exception as e:
        logger.critical(f"Error occured for config file 'config.yaml' : {str(e)}")
        sleep(1)
        sys.exit(1)
        
    return conf_dict

