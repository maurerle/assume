#!/usr/bin/python3

# SPDX-FileCopyrightText: ASSUME Developers
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys

image_repo = "ghcr.io/assume-framework/assume:latest"
if len(sys.argv) != 2:
    print("Usage: generate_simulation.py <agent_count>")
    sys.exit(1)
agent_count = int(sys.argv[1])

output = []
output.append("services:")
MQTT = "mqtt-broker"
# MQTT = ""
TCP_HOST = "simulation_mgr"
TCP_PORT = "8089"


def agent_name(agent_nr):
    if MQTT:
        return f"agent{agent_nr}"
    else:
        return f"simulation_client{agent_nr}:{9000 + int(agent_nr)}"


agents = [agent_name(i) for i in range(agent_count)]

output.append("""
  assume_db:
    # smaller without postgis support:
    # image: timescale/timescaledb:latest-pg16
    image: timescale/timescaledb-ha:pg16-oss
    container_name: assume_db
    restart: always
    environment:
      - POSTGRES_USER=assume
      - POSTGRES_PASSWORD=assume
      - POSTGRES_DB=assume
      - TS_TUNE_MAX_CONNS=500
    volumes:
      # needed for normal image
      #- ./assume-db:/var/lib/postgresql/data
      # /home/postgres/data is path for timescaledb-ha image
      - ./assume-db:/home/postgres/pgdata
    ports:
      - 5432:5432
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]

  grafana:
    image: grafana/grafana-oss:latest
    container_name: assume_grafana
    user: "104"
    depends_on:
      - assume_db
    ports:
      - 3000:3000
    environment:
      GF_SECURITY_ALLOW_EMBEDDING: "true"
      GF_AUTH_ANONYMOUS_ENABLED: "true"
      GF_INSTALL_PLUGINS: "marcusolsson-dynamictext-panel,orchestracities-map-panel"
      GF_SECURITY_ADMIN_USER: assume
      GF_SECURITY_ADMIN_PASSWORD: "assume"
      GF_LOG_FILTERS: rendering:debug
    volumes:
      - ./docker_configs/grafana.ini:/etc/grafana/grafana.ini
      - ./docker_configs/datasources:/etc/grafana/provisioning/datasources
      - ./docker_configs/dashboards:/etc/grafana/provisioning/dashboards
      - ./docker_configs/dashboard-definitions:/etc/grafana/provisioning/dashboard-definitions
    restart: always
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
""")

if MQTT:
    # Add MQTT agent
    output.append("""
  mqtt-broker:
    container_name: mqtt-broker
    image: eclipse-mosquitto:2
    restart: always
    ports:
      - "1883:1883/tcp"
    volumes:
      - ./docker_configs/mqtt.conf:/mosquitto/config/mosquitto.conf
    healthcheck:
      test: "mosquitto_sub -t '$$SYS/#' -C 1 | grep -v Error || exit 1"
      interval: 45s
      timeout: 5s
      retries: 5
""")
# Add one management agent
output.append(f"""
  simulation_mgr:
    container_name: simulation_mgr
    image: {image_repo}
    depends_on:
      - assume_db
    environment:
      DB_URI: "postgresql://assume:assume@assume_db:5432/assume"
      MQTT_BROKER: "{MQTT}"
      TCP_HOST: "{TCP_HOST}"
      TCP_PORT: "{TCP_PORT}"
    volumes:
      - ./examples/distributed_simulation:/src/examples/distributed_simulation
    entrypoint: python3 -m examples.distributed_simulation.world_manager {" ".join(agents)}

""")

# Add Bidding Agents
for agent in range(agent_count):
    output.append(f"""
  simulation_client{agent}:
    image: {image_repo}
    environment:
      MQTT_BROKER: "{MQTT}"
      TCP_HOST: "{TCP_HOST}"
      TCP_PORT: "{TCP_PORT}"
    volumes:
      - ./examples/distributed_simulation:/src/examples/distributed_simulation
    entrypoint: python3 -m examples.distributed_simulation.world_agent {agent} {agent_count} {agent_name(agent)}
""")

with open("compose.yml", "w") as f:
    f.writelines(output)
