import logging
import math
import asyncio
from time import sleep
from typing import Any
from operator import itemgetter
from datetime import datetime

from pystrm.kmain.kProducer import Kprod
from pystrm.utils.common.genUtils import get_clientSchema
from pystrm.utils.common.marketUtils import marketCheck
from pystrm.utils.logger.logDecor import logtimer, inOutLog

import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
import yfinance as yf  # noqa: E402

logger = logging.getLogger(__name__)


@logtimer
def dataDupCheck(data_dct: dict[str, Any], typ: str, data: dict[str, Any], symb: str) -> bool:
    
    data_chk = data.copy()
    data_chk.pop("recordtimestamp", None)

    if (typ + "." + symb) in data_dct.keys():
        if data_dct[typ + "." + symb] == data_chk:
            return False
        else:
            data_dct[typ + "." + symb] = data_chk
            return True
    else:
        data_dct[typ + "." + symb] = data_chk
        return True


@logtimer
async def validSend(kobj: Kprod, typ: str, data_dct: dict[str, Any], symb: str, data: dict[str, Any], schema_type: str, schema: object) -> None:
    if dataDupCheck(data_dct=data_dct, typ=typ, data=data, symb=symb):
        logger.info(f"New record found for symbol : {symb}")
        kobj.prodDataWithSerialSchema(schema=schema, data=data, mykey=symb, schema_type=schema_type)
    else:
        logger.info(f"Duplicate record found for symbol : {symb}")


# @logtimer
# async def asyncTicker(kobj: Kprod, symb: str, meth: str):
#     data = yf.Ticker(symb+".NS").__getattribute__(meth)
#     data_correction = {k: None if isinstance(v, float) and math.isnan(v) else v for k, v in data.items()}
#     return data_correction


@logtimer
async def asyncFastInfo(symb: str, meth: list[str]) -> dict[str, Any]:
    ct = datetime.now()
    data = dict(zip([item.lower() for item in meth], list(itemgetter(*meth)(yf.Ticker(symb+".NS").fast_info)))) | {"recordtimestamp": ct.strftime('%Y-%m-%dT%H:%M:%S.') + ct.strftime('%f')[:3]}
    data = {k: None if isinstance(v, float) and math.isnan(v) else v for k, v in data.items()}
    return data


@inOutLog
async def fastInfo(kobj: Kprod, symbol: list[str], param_dct: dict[str, Any]) -> None:
    """_summary_

    Args:
        symbol (str): symbol for which ticker data will be generated
    """

    indx: int = 0

    if len(symbol) == 0:
        logger.info("Symbol list is of zero size")
        return None

    schema = get_clientSchema(param_dct['prop_key'], param_dct['schema_type'])

    dupCheck = dict()

    while True: 
        # print(dupCheck)
        indx = indx % len(symbol)

        if indx == 0:
            sleep(1)
            if not marketCheck():
                return None

        try:  
            data = await asyncFastInfo(symbol[indx], param_dct['infolst'])
            await validSend(kobj, "fastInfo", dupCheck, symbol[indx], data, param_dct['schema_type'], schema)
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrrupt happened")
        except Exception as e:
            logger.error(str(e))
        
        if param_dct['type'] != 'Streaming' and indx == len(symbol) - 1:
            break
        
        indx += 1

    return None


# @inOutLog
# @logtimer
# async def multiTicker(kobj: Kprod, symbol: list[str], param_dct: dict[str, Any]) -> None:
#     """_summary_

#     Args:
#         symbol (str): symbol for which ticker data will be generated

#     Returns:
#         dict[str, Any]: Fetch ticker data 
#     """

#     # schema_client = SchemaRegistryClient(KAFKA_SCHEMA_CLIENT)

#     indx: int = 0

#     if len(symbol) == 0:
#         logger.info("Symbol list is of zero size")
#         return

#     while True: 
#         indx = indx % len(symbol)
#         try:
#             data = await asyncFastInfo(symbol[indx],  param_dct['infolst'])
#             await kobj.prodDataWithAvroSerialSchema(value=data, key=symbol[indx])
#             sleep(1)
#         except KeyboardInterrupt:
#             logger.warning("KeyboardInterrrupt happened")
#             break
#         except Exception as e:
#             logger.error(str(e))
        
#         if param_dct['type'] != 'Streaming':
#             sleep(5)
#             break
        
#         indx += 1
#     return None


@inOutLog
@logtimer
def procHandler(param_dct: dict[str, Any], symb: list[str]) -> None:
    """Fetch data from Yahoo Finance till market close in multiprocess and concurrrent waiting manner

    Args:
        param_dct (dict[str, str]): Parameter dictionary for execution
        symb (list[str]): List of stock symbols for fetch data
    """
    

    kobj = Kprod(topic=param_dct['prop_key'])

    __EXECUTE_METHOD = {
        # "multitick": multiTicker,
        "fastinfo": fastInfo
    }

    asyncio.run(__EXECUTE_METHOD[param_dct['ldt']](kobj, symb, param_dct))
    return None


def process_status(err):
    if err is not None:
        logger.error("Failed process: %s" % (str(err)))
    else:
        logger.info("Process Success")
        


