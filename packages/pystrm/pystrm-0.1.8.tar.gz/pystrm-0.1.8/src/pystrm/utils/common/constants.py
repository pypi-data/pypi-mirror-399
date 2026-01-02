from datetime import datetime
from enum import Enum

from pystrm.utils.common.confs import fetch_conf, fetch_prop
from socket import gethostname
from xxhash import xxh32_intdigest

class Constants(Enum):

    RUN_ID = int(datetime.now().strftime('%Y%m%d')  + str(xxh32_intdigest("pystream" + datetime.now().strftime('%H:%M:%S.%f'))))

    CURRENT_DATE = datetime.today().strftime('%Y-%m-%d')

    INFRA_CFG = fetch_conf()

    TBL_CFG = fetch_prop()

    KAFKA_BROKERS = INFRA_CFG['Kafka']['kafka-broker-conf'] | {'client.id': gethostname()}

    KAFKA_SCHEMA_CLIENT = INFRA_CFG['Kafka']['kafka-schema-client-conf']
