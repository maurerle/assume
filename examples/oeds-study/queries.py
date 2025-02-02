# SPDX-FileCopyrightText: Florian Maurer
#
# SPDX-License-Identifier: Apache-2.0

import os
from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine, text

db_uri = "postgresql://assume:assume@rdp.nowum.fh-aachen.de:5432/assume"

entsoe_uri = os.getenv(
    "INFRASTRUCTURE_URI",
    "postgresql://readonly:readonly@timescale.nowum.fh-aachen.de:5432/opendata?options=--search_path=entsoe",
)

###########################

simulation = "world_mastr_nuts3_entsoe_random_2019"
from_date = "2019-01-01"
to_date = "2019-12-31"


@lru_cache(maxsize=32)
def query_data(simulation: str, from_date: str, to_date: str):
    entsoe_engine = create_engine(entsoe_uri)
    engine = create_engine(db_uri)

    VALID_COUNTRY = "('DE_LU', 'DE_AT_LU')"
    if "austria" in simulation:
        VALID_COUNTRY = "('AT')"
    print(simulation)
    # assume_dispatch
    data = {}
    sql = f"""
    SELECT
        "datetime" as "time",
        sum(power) AS "market_dispatch",
    market_id,
    um.technology
    FROM market_dispatch md
    join power_plant_meta um on um."index" = md.unit_id and um.simulation = md.simulation
    WHERE
    "datetime" BETWEEN '{from_date}' AND '{to_date}' AND
    md.simulation = '{simulation}'
    GROUP BY 1, market_id, technology
    ORDER BY technology, market_id desc, 1
    """

    assume_dispatch = pd.read_sql(sql, engine, index_col="time", parse_dates="time")

    series = []
    for label, sub_df in assume_dispatch.groupby(["market_id", "technology"]):
        lab = "-".join(label)
        lab = lab.replace("EOM-", "")

        # if "lignite" not in lab and "nuclear" not in lab:
        #    continue
        group_sum = sub_df.market_dispatch.groupby("time").sum()
        group_sum.name = lab
        series.append(group_sum.resample("1h").ffill())

    ddf = pd.DataFrame(series)
    ddf = ddf.T

    ddf = ddf[sorted(ddf.columns, reverse=True)]
    ddf = ddf.fillna(0)
    data["assume_dispatch"] = ddf * 1e3  # MW to kWh

    # entsoe dispatch

    query = f"""
    SELECT
    public.time_bucket('3600.000s',index) AS "time",
    avg(nuclear*1e3) as nuclear,
    avg("fossil_hard_coal"*1e3) as coal,
    avg(("hydro_run-of-river_and_poundage"+hydro_water_reservoir)*1e3) as hydro,
    avg(biomass*1e3) as bio,
    avg(("fossil_coal-derived_gas"+"fossil_gas")*1e3) as "natural gas",
    avg("fossil_brown_coal/lignite" *1e3) as lignite,
    avg((fossil_oil+coalesce(fossil_oil_shale,0)+coalesce(fossil_peat,0))*1e3) as oil,
    avg(("fossil_hard_coal")*1e3) as "hard coal",
    avg(("wind_offshore")*1e3) as wind_offshore,
    avg(("wind_onshore")*1e3) as wind_onshore,
    avg(solar*1e3) as solar,
    avg((hydro_pumped_storage*1e3)) as "storage",
    avg((geothermal+other+waste)*1e3) as others
    FROM query_generation
    WHERE
    index BETWEEN '{from_date}' AND '{to_date}' AND
    country in {VALID_COUNTRY}
    GROUP BY 1
    ORDER BY 1
    """
    data["dispatch_entsoe"] = pd.read_sql(
        query, entsoe_engine, index_col="time", parse_dates="time"
    )

    query = f"""
    SELECT
    public.time_bucket('3600.000s',index) AS "time",
    avg(actual_load) AS "demand"
    FROM query_load
    WHERE
    index BETWEEN '{from_date}' AND '{to_date}' AND
    country in {VALID_COUNTRY}
    GROUP BY 1
    ORDER BY 1
    """
    data["load_entsoe"] = pd.read_sql(
        query, entsoe_engine, index_col="time", parse_dates="time"
    ).tz_localize(None)

    query = f"""
    SELECT public.time_bucket('3600.000s',index) AS "time",
    avg("0") AS "entsoe_price"
    FROM query_day_ahead_prices
    WHERE
    index BETWEEN '{from_date}' AND '{to_date}' AND
    country in {VALID_COUNTRY}
    GROUP BY 1
    ORDER BY 1
    """
    entsoe_price = pd.read_sql(
        query, entsoe_engine, index_col="time", parse_dates="time"
    )
    data["preis_entsoe"] = entsoe_price["entsoe_price"]
    data["preis_entsoe"].index = data["preis_entsoe"].index.tz_localize(None)
    data["preislinie_entsoe"] = entsoe_price.sort_values(
        by="entsoe_price", ascending=False
    ).reset_index()["entsoe_price"]

    query = f"""SELECT public.time_bucket('3600.000s',"product_start") AS "time",
    avg(price) AS "assume_price"
    FROM market_meta
    WHERE ("simulation" LIKE '{simulation}') AND 
    product_start BETWEEN '{from_date}' AND '{to_date}'
    GROUP BY market_id, simulation, product_start
    ORDER BY 1;
    """

    assume_price = pd.read_sql(query, engine, index_col="time", parse_dates="time")
    data["preis_assume"] = assume_price["assume_price"]
    data["preislinie_assume"] = assume_price.sort_values(
        by="assume_price", ascending=False
    ).reset_index()["assume_price"]

    return data
