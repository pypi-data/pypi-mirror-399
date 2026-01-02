import logging
import logging.config
import sys
import os 
from pprint import pformat
from time import sleep
from typing import Any
from datetime import datetime
from pathlib import Path
from multiprocessing_logging import install_mp_handler


def main_function(mthd: str, conf_key: str, path: str = os.getcwd()) -> None: 

    if not os.path.exists(path):
        print(f'{path} does exists')
        sleep(1)
        sys.exit(1)

    os.chdir(path)

    from pystrm.utils.common.constants import Constants
    from pystrm.utils.mainCalls.yfUtils import  getLiveTickData

    config: dict[str, Any] = Constants.INFRA_CFG.value['Logging']

    if 'file_json' in config['handlers']:
        Path(Path.cwd()/'logs').mkdir(exist_ok=True)
        config['handlers']['file_json']['filename'] += datetime.now().strftime('%Y-%m-%d.json')

    logging.config.dictConfig(config)
    logger = logging.getLogger()

    install_mp_handler(logger)
    
    logger.info("Intitiating program with run_id : " + str(Constants.RUN_ID.value))

    __method_to_excute = {
        "liveYfinanaceTick": getLiveTickData
    }
    
    try:

        if mthd not in __method_to_excute.keys():
            msg = "List of operation mentioned in dictionary for this package"
            raise KeyError
        else:
            logger.info(f"Operation {mthd} exists. Validating other input")
        
        if (conf_key.split('.')[0] not in Constants.TBL_CFG.value.keys()) or (conf_key.split('.')[1] not in Constants.TBL_CFG.value[conf_key.split('.')[0]]):
            msg = f"key:{conf_key.split('.')[0]} and value: {conf_key.split('.')[1]} pair does not exists in tables.yml"
            raise KeyError
        else:
            logger.info(f"Configuration found in tables.yml for {conf_key}")
            logger.info("Config found for this operation from tables.yml are as below:")
            logger.info(f"\n{pformat(Constants.TBL_CFG.value[conf_key.split('.')[0]], indent=4)}")

        return __method_to_excute[mthd](conf_key)
    except TypeError:
        logger.critical(f"main() function takes exactly 2 arguments ({len(sys.argv[1:])} given)")
        sleep(1)
        sys.exit(1)
    except KeyError:
        logger.critical(f'Key not found: {msg}')
        sleep(1)
        sys.exit(1)
    except Exception as e:
        logger.critical("Error occur while initiating: " + str(e))
        sleep(1)
        sys.exit(1)


if __name__ == '__main__':

    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument("-m", "--method", type=str, help="Method to execute", required=True)
    parser.add_argument("-k", "--key", type=str, help="Key required for properties", required=True)
    parser.add_argument("-c", "--cfg_path", type=str, help="Config path of config files", required=False, default=os.getcwd())

    args = parser.parse_args()

    if hasattr(args, 'cfg_path'):
        main_function(args.method, args.key, args.cfg_path)
    else:
        main_function(args.method, args.key)
