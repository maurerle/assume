import logging
from dataclasses import dataclass, field

import pandas as pd
from mango import Role
from mango.messages.message import Performatives

from assume.common.market_objects import (
    ClearingMessage,
    MarketConfig,
    OpeningMessage,
    Order,
    Orderbook,
)

from pathlib import Path

import nest_asyncio
import pandas as pd
from pathlib import Path
import yaml
from mango import RoleAgent, create_container
from mango.util.clock import ExternalClock
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
from tqdm import tqdm
import time


class WriteOutput(Role):
    def __init__(self,
        inputs_path: str,
        scenario: str,
        study_case: str,
        database_uri: str = "",
        export_csv_path: str = ""
        ):

        super().__init__()

        # load the config file
        path = f"{inputs_path}/{scenario}"
        with open(f"{path}/config.yml", "r") as f:
            config = yaml.safe_load(f)
            config = config[study_case]
            self.simulation_id = config['id']
           
            self.export_csv = config['export_config']['export_csv']

            self.write_orders_frequency = config['export_config']['write_orders_frequency']
        
        self.export_csv_path = export_csv_path
        self.p = Path(self.export_csv_path)
        self.p.mkdir(parents=True, exist_ok=True)
        print('test, we triggered the right event? yes')
        self.db = database_uri

    async def handle_message(self, message):
        if message.get('type') == 'store_order_book':
            self.write_market_orders( message.get('data'), self.write_orders_frequency)

        elif message.get('type') == 'store_market_results':
            self.write_market_results(self, message.get('data'))

        elif message.get('type') == 'store_units':
            self.write_units_defintion(self, message.get('unit_type'), message.get('data'))



    def write_market_results(self, market_meta):
        df = pd.DataFrame.from_dict(market_meta)
        df['simulation']=self.simulation_id
        
        if self.export_csv:
            
            market_data_path = self.p.joinpath("market_meta.csv")
            df.to_csv(market_data_path, mode="a", header=not market_data_path.exists())

        df.to_sql("market_meta", self.db.bind, if_exists="append")



    async def write_market_orders(self, market_result, frequency):


        # TODO write market_result or other metrics
        df = pd.DataFrame.from_dict(market_result)
        if len(df)>0:
            
            #have to drop tuple of agent_id because sql does not like to write tuple inot db
            #or we trasnform it to a string
            df["agent_id"]=df["agent_id"].astype(str)
            df['simulation']=self.simulation_id

            if self.export_csv:
                market_data_path = self.p.joinpath("market_orders.csv")
                df.to_csv(market_data_path, mode="a", header=not market_data_path.exists())

            df.to_sql("market_orders_all", self.db.bind, if_exists="append")



    def write_units_defintion(self, unit_type, unit_params):

        if unit_type != 'demand':

            df = pd.DataFrame([unit_params])
            df['simulation']=self.simulation_id
            df=df[['technology','fuel_type','emission_factor','max_power','min_power','efficiency','unit_operator']]
        
            if self.export_csv:
                p = Path(self.export_csv_path)
                p.mkdir(parents=True, exist_ok=True)
                market_data_path = p.joinpath("unit_meta.csv")
                df.to_csv(market_data_path, mode="a", header=not market_data_path.exists())
            df.to_sql("unit_meta", self.db.bind, if_exists="append")

            print('I should have written demand')

        else:
            df = pd.DataFrame()    
            df['type']= unit_type
            df['volume']= unit_params['volume'].max()
            df['simulation']=self.simulation_id
            #df['volume']=df["volume"].max()
            
            if self.export_csv:
                p = Path(self.export_csv_path)
                p.mkdir(parents=True, exist_ok=True)
                market_data_path = p.joinpath("demand_meta.csv")
                df.to_csv(market_data_path, mode="a", header=not market_data_path.exists())
            df.to_sql("demand_meta", self.db.bind, if_exists="append")


    async def write_dispatch_plan(self, total_power_output, unit, unit_id):
        """
        Writes the planned dispatch of the units after the market clearing to a csv and db
        In the case that we have no portfolio optimisation this equals the bids. 
        """

        df = pd.DataFrame.from_dict(total_power_output)
        df.rename(columns={df.columns[0]:'power'}, inplace=True)
        df['unit']=unit
        #sql does not liek tuples, so conversion necessary
        df['unit_id']=unit_id
        df['simulation']=self.simulation_id

        
        if self.export_csv:
            p = Path(self.export_csv_path)
            p.mkdir(parents=True, exist_ok=True)
            data_path = p.joinpath("power_plant_dispatch.csv")
            df.to_csv(data_path, mode="a", header=not data_path.exists())
        
        df.to_sql("power_plant_dispatch", self.db.bind, if_exists="append")



