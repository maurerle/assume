# SPDX-FileCopyrightText: ASSUME Developers
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import time
from pathlib import Path

import pandas as pd
from amirispy.scripts import amiris_cli
from sqlalchemy import create_engine, text

db_uri = "postgresql://assume:assume@localhost:5432/assume"
engine = create_engine(db_uri)

scenario = "Germany2019"  # "Simple", "Germany2019", "Austria2019"
run_amiris = True
run_assume = True

scenario_path = f"../amiris-examples/{scenario}"

if run_amiris:
    amiris_path = Path("./amiris-core_*-jar-with-dependencies.jar")
    amiris_paths = list(Path(amiris_path.parent).glob(amiris_path.name))

    if not amiris_paths:
        amiris_cli(["install", "-m", "model"])
        amiris_paths = list(Path(amiris_path.parent).glob(amiris_path.name))
    if not amiris_paths or not amiris_paths[0].is_file():
        print("could not download amiris")

    print(f"running {scenario}")
    start = time.time()
    executable = amiris_paths[0].name
    amiris_cli(
        f"run --jar ./{executable} -s {scenario_path}/scenario.yaml --output {scenario}".split(
            " "
        )
    )
    duration = time.time() - start
    print(f"took {duration} seconds")

    schema_name = f"amiris_{scenario.lower()}"
    query = text(f"create schema if not exists {schema_name}")
    with engine.begin() as conn:
        conn.execute(query)

    for output_file in Path(scenario).glob("*.csv"):
        with engine.begin() as conn:
            with open(output_file) as f:
                df = pd.read_csv(
                    f, sep=";", index_col="TimeStep", parse_dates=["TimeStep"]
                )
                table_name = output_file.stem.lower()
                table_name = table_name[:63]
                df.to_sql(table_name, conn, if_exists="replace", schema=schema_name)
    print("successfully wrote to sql")

import logging

logging.disable(logging.NOTSET)
from importlib import reload

reload(logging)
# this kills the logging config from amiris

if run_assume:
    from assume import World
    from assume.scenario.loader_amiris import load_amiris_async

    print(f"running {scenario}")
    start = time.time()

    world = World(database_uri=db_uri)
    world.loop.run_until_complete(
        load_amiris_async(
            world,
            "amiris",
            scenario.lower(),
            scenario_path,
        )
    )
    world.run()
    duration = time.time() - start
    print(f"took {duration} seconds")
