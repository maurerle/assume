# SPDX-FileCopyrightText: Florian Maurer
#
# SPDX-License-Identifier: Apache-2.0

# now we can evaluate the runs

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from queries import query_data

plt.style.use("seaborn-v0_8")


def plot_all_plots(
    simulation: str,
    from_date: str,
    to_date: str,
    results,
    latex_table: bool = False,
):

    simulation = "world_mastr_nuts1_entsoe_random_2019"
    simulation = "world_mastr_nuts1_entsoe_random_2024"
    data = results[simulation]
    data_nuts2 = results[simulation.replace("nuts1", "nuts2")]
    data_nuts3 = results[simulation.replace("nuts1", "nuts3")]

    data["assume_dispatch"]["natural gas"] = data["assume_dispatch"]["gas"]
    data_nuts2["assume_dispatch"]["natural gas"] = data_nuts2["assume_dispatch"]["gas"]
    data_nuts3["assume_dispatch"]["natural gas"] = data_nuts3["assume_dispatch"]["gas"]

    base_path = Path("output", simulation)
    # set plot to true here to see plots inline
    def savefig(path: str, plot=False, *args, **kwargs):
        output_path = Path(base_path, f"{path}.svg")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            output_path, *args, transparent=False, bbox_inches="tight", **kwargs
        )
        if plot:
            plt.show()
        plt.close()

    
    renewables = data["dispatch_entsoe"][["solar", "wind_onshore", "wind_onshore"]].sum(axis=1)
    total_generation = data["dispatch_entsoe"].sum(axis=1)
    total_load = data["load_entsoe"]*1e3

    renewables_assume = data["assume_dispatch"][["solar", "wind_onshore", "wind_onshore"]].sum(axis=1)
    total_generation_assume = data["assume_dispatch"].sum(axis=1)

    total_generation_assume[3400:3800].plot()
    

    plt.scatter(total_load, data["preis_entsoe"], s=2)
    plt.scatter(total_generation_assume, data["preis_assume"][:8665], s=2)
    plt.legend(["entsoe", "assume"])

    renewables_factor = renewables/total_generation
    plt.scatter(renewables_factor, data["preis_entsoe"].clip(0), s=2)
    
    # anteil erneuerbare korreliert mit einem Preis
    
    plt.scatter(renewables, data["preis_entsoe"], s=2, label="entsoe")
    plt.scatter(renewables_assume, data["preis_assume"][:8665], s=2, label="simulation")
    # similar for other nuts
    # plt.scatter(renewables_assume, data_nuts2["preis_assume"][:8665], s=2, label="simulation2")
    # plt.scatter(renewables_assume, data_nuts3["preis_assume"][:8665], s=2, label="simulation3")
    plt.legend()

    total_generation.plot()
    data["load_entsoe"].plot()

    ### price duration curve
    plt.figure(figsize=(10, 5))
    data["preislinie_assume"].plot()
    data_nuts2["preislinie_assume"].plot()
    data_nuts3["preislinie_assume"].plot()
    data["preislinie_entsoe"].plot()
    plt.xlabel("hours")
    plt.ylabel("price in [€/MW]")
    plt.legend(["NUTS1", "NUTS2", "NUTS3", "ENTSO-E"])
    savefig("price_duration_curve")

    ### dispatch duration curve

    techs = [
        "nuclear",
        "wind_offshore",
        "wind_onshore",
        "solar",
        "lignite",
        "natural gas",
        "hard coal",
        "oil",
        "hydro",
    ]
    tech = "hard coal"
    data["ddcs"] = {}
    for tech in techs:
        if tech not in data["dispatch_entsoe"]:
            continue
        if tech not in data["assume_dispatch"].keys():
            continue
        data["ddcs"][f"{tech}_entsoe"] = (
            data["dispatch_entsoe"][tech]
            .sort_values(ascending=False)
            .reset_index(drop=True)
        )

        data["ddcs"][f"{tech}_assume"] = (
            data["assume_dispatch"][tech]
            .sort_values(ascending=False)
            .reset_index(drop=True)
            * 1e3
        )

        data["ddcs"][f"{tech}_assume2"] = (
            data_nuts2["assume_dispatch"][tech]
            .sort_values(ascending=False)
            .reset_index(drop=True)
            * 1e3
        )

        data["ddcs"][f"{tech}_assume3"] = (
            data_nuts3["assume_dispatch"][tech]
            .sort_values(ascending=False)
            .reset_index(drop=True)
            * 1e3
        )

        plt.figure(figsize=(10, 5))
        (data["ddcs"][f"{tech}_entsoe"] / 1e3).plot()
        (data["ddcs"][f"{tech}_assume"] / 1e6).plot()
        (data["ddcs"][f"{tech}_assume2"] / 1e6).plot()
        (data["ddcs"][f"{tech}_assume3"] / 1e6).plot()
        plt.title(tech)
        plt.xlabel("hour")
        plt.ylabel("energy in GW")
        plt.legend([f"ENTSO-E {tech}", f"simulation {tech} NUTS1", f"simulation {tech} NUTS2", f"simulation {tech} NUTS3"])
        savefig(f"dispatch_duration_curve_{tech}")


    if False:
        data["assume_dispatch"]["wind_onshore"][100:400].plot()
        data["dispatch_entsoe"]["wind_onshore"][100:400].plot()

        data["dispatch_entsoe"]["wind_offshore"][100:1000].plot()
        (data["assume_dispatch"]["wind_offshore"][100:1000]).plot()

        (data["assume_dispatch"]["lignite"][100:400] * 1e0).plot()
        data["dispatch_entsoe"]["lignite"][100:400].plot()

        savefig("dispatch_wind_lignite")
    # price scatter plot
    preis_entsoe = data["preis_entsoe"][from_date:to_date]
    preis_assume = data["preis_assume"][from_date:to_date]
    preis_assume_nuts2 = data_nuts2["preis_assume"][from_date:to_date]
    preis_assume_nuts3 = data_nuts3["preis_assume"][from_date:to_date]
    # preis_assume = preis_assume[preis_entsoe>=0]
    # preis_entsoe = preis_entsoe[preis_entsoe>=0]

    # Pearson correlation coefficient
    preis_entsoe = preis_entsoe.reindex(preis_assume.index, fill_value=0)
    corref_assume = np.corrcoef(preis_entsoe, preis_assume)[0, 1]
    corref_assume2 = np.corrcoef(preis_entsoe, preis_assume_nuts2)[0, 1]
    #corref_assume3 = np.corrcoef(preis_entsoe, preis_assume_nuts3)[0, 1]
    print(f"CORR COEFF Simulation {simulation}  {corref_assume:.4f}")
    print(f"CORR COEFF Simulation NUTS2 {simulation}  {corref_assume2:.4f}")
    #print(f"CORR COEFF Simulation NUTS3 {simulation}  {corref_assume3:.4f}")

    max_entsoe = preis_entsoe.max()
    min_entsoe = preis_entsoe.min()
    plt.figure(figsize=(8, 8))

    plt.scatter(preis_entsoe, preis_assume, s=8, label="NUTS1")
    plt.scatter(preis_entsoe, preis_assume_nuts2, s=8, label="NUTS2")
    #plt.scatter(preis_entsoe, preis_assume_nuts3, s=8, label="NUTS3")
    plt.plot([min_entsoe, max_entsoe], [min_entsoe, max_entsoe], "k--", linewidth=1)
    plt.xlabel("historic price of ENTSO-E [€/MWh]")
    plt.ylabel("simulation price at respective hour [€/MWh]")
    plt.gca().axis("equal")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.legend(
        [
            f"Simulation\t corr coef: {corref_assume:.4f}".expandtabs(),
        ]
    )
    plt.yticks(np.arange(min_entsoe // 20 * 20, max_entsoe + 1 // 20 * 20, 20))
    plt.xticks(np.arange(preis_entsoe.min() // 20 * 20, max_entsoe + 1 // 20 * 20, 20))
    # plt.title("scatter plot of the simulation prices")
    savefig("price_scatter_curve")
    res_assume = preis_entsoe - preis_assume
    # res_assume = res_assume - res_assume.mean()
    res_assume.mean()
    mae_assume = abs(res_assume)
    mae_assume = mae_assume.fillna(0)
    print("MAE Simulation", simulation, mae_assume.mean())

    print(f"mean Simulation {simulation}  {preis_assume.mean():.2f}")
    print(f"mean ENTSO-E {simulation}  {preis_entsoe.mean():.2f}")

    rmse_assume = np.sqrt(((res_assume) ** 2).fillna(0).mean())

    print("RMSE Simulation", simulation, rmse_assume.mean())

    plt.figure(figsize=(10, 5))
    preis_assume.resample("7d").mean().plot()
    preis_entsoe.resample("7d").mean().plot()
    plt.legend(["Simulation", "ENTSO-E"])
    plt.title("7d average of price")

    ddf = data["assume_dispatch"][4000:4500]
    ddf = ddf.reindex(
        [
            "biomass",
            "nuclear",
            "oil",
            "hydro",
            "lignite",
            "hard coal",
            "other",
            "wind_offshore",
            "wind_onshore",
            "solar",
        ],
        axis=1,
    )
    ddf.dropna(axis=1, how="all", inplace=True)
    base = ddf[ddf.columns[0]] * 0
    plt.figure(figsize=(10, 5))
    for col in ddf.columns:
        line = base + ddf[col]
        alpha = 0.6
        plt.fill_between(line.index, line, base, alpha=alpha, label=col)
        base += ddf[col]
    plt.ylabel("Hourly dispatch power [$GW$]")
    plt.xlabel("Datetime")
    plt.xticks(rotation=25)
    plt.legend()
    savefig("overview-dispatch-assume")

    if "2019" in simulation:
        start = "2019-06-17"
        end = "2019-07-10"

        #start = "2023-06-17"
        #end = "2023-07-10"

        techs = ["nuclear", "hard coal", "lignite", "natural gas", "oil", "hydro"]
        for tech in techs:
            plt.figure(figsize=(10, 5))
            dispatch_entsoe = (data["dispatch_entsoe"][tech])[start:end].dropna()
            if len(dispatch_entsoe) > 0:
                data["assume_dispatch"][tech][start:end].plot()
                dispatch_entsoe.plot()
                plt.legend(["Simulation", "ENTSO-E"])
                plt.xlabel("time")
                plt.ylabel("power in MW")
                savefig(f"sample-dispatch-{tech}")

        start = "2019-01-19"
        end = "2019-02-04"
        plt.figure(figsize=(10, 5))
        plt.step(preis_assume[start:end].index, preis_assume[start:end], linewidth=1)
        plt.step(preis_entsoe[start:end].index, preis_entsoe[start:end], linewidth=1)
        plt.legend(["Simulation", "ENTSO-E"])
        plt.xlabel("time")
        plt.xticks(rotation=25)
        plt.ylabel("price in €/MW")
        savefig("sample-price")

        start = "2019-04-29"
        end = "2019-05-13"
        plt.figure(figsize=(10, 5))
        plt.step(preis_assume[start:end].index, preis_assume[start:end], linewidth=1)
        plt.step(preis_entsoe[start:end].index, preis_entsoe[start:end], linewidth=1)
        plt.xticks(rotation=25)
        plt.legend(["Simulation", "ENTSO-E"])
        plt.xlabel("time")
        plt.ylabel("price in €/MW")
        savefig("sample-price2")


def results_to_csv(results: dict[str, dict[str, pd.DataFrame]]):
    for key, value in results.items():
        path = Path("output/csv", key)
        path.mkdir(parents=True, exist_ok=True)
        for val_key, val_value in value.items():
            val_path = Path(path, val_key + ".csv")
            if isinstance(val_value, dict):
                return_value = pd.DataFrame(val_value)
            else:
                return_value = val_value
            return_value.to_csv(val_path)

def table_from_results(results: dict = None):
    simulations = [
        "world_mastr_nuts1_entsoe_random_2019",
        "world_mastr_nuts2_entsoe_random_2019",
        "world_mastr_nuts3_entsoe_random_2019",
        "world_mastr_nuts1_entsoe_random_2020",
        "world_mastr_nuts2_entsoe_random_2020",
        "world_mastr_nuts3_entsoe_random_2020",
        "world_mastr_nuts1_entsoe_random_2021",
        "world_mastr_nuts2_entsoe_random_2021",
        "world_mastr_nuts3_entsoe_random_2021",
        "world_mastr_nuts1_entsoe_random_2023",
        "world_mastr_nuts2_entsoe_random_2023",
        "world_mastr_nuts3_entsoe_random_2023",
        "world_mastr_nuts1_entsoe_random_2024",
        "world_mastr_nuts2_entsoe_random_2024",
        "world_mastr_nuts3_entsoe_random_2024_flexable",
        "world_mastr_nuts1_entsoe_random_2018_flexable",
        "world_mastr_nuts2_entsoe_random_2018_flexable",
        "world_mastr_nuts3_entsoe_random_2018_flexable",
    ]
    if not results:
        results = {}

    for simulation in simulations:
        year = simulation.replace("_flexable", "")[-4:]

        from_date = f"{year}-01-02"
        to_date = f"{year}-12-30"
        if not results.get(simulation):
            print(f"querying data for {simulation}")
            data = query_data(simulation, from_date, to_date)
            results[simulation] = data

    base_path = Path("output", simulation)
    # set plot to true here to see plots inline
    def savefig(path: str, plot=False, *args, **kwargs):
        output_path = Path(base_path, f"{path}.svg")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            output_path, *args, transparent=False, bbox_inches="tight", **kwargs
        )
        if plot:
            plt.show()
        plt.close()

    calculation  = []
    for simulation in simulations:
        year = simulation.replace("_flexable", "")[-4:]

        from_date = f"{year}-01-02"
        to_date = f"{year}-12-30"

        data = results[simulation]

        preis_entsoe = data["preis_entsoe"][from_date:to_date]
        preis_assume = data["preis_assume"][from_date:to_date]
        if len(preis_assume)<1:
            continue

        # Pearson correlation coefficient
        preis_assume = preis_assume[preis_entsoe.dropna().index]
        preis_entsoe = preis_entsoe.reindex(preis_assume.index, fill_value=0)
        corref_assume = np.corrcoef(preis_entsoe, preis_assume)[0, 1]
        print(f"CORR COEFF Simulation {simulation}  {corref_assume:.4f}")

        res_assume = preis_entsoe - preis_assume
        # res_assume = res_assume - res_assume.mean()
        res_assume.mean()
        res_entsoe = preis_entsoe - preis_entsoe.mean()
        mae_entsoe = abs(res_entsoe).fillna(0)
        mae_assume = abs(res_assume).fillna(0)
        print("MAE Simulation", simulation, mae_assume.mean())

        print(f"mean Simulation {simulation}  {preis_assume.mean():.2f}")
        print(f"mean ENTSO-E {simulation}  {preis_entsoe.mean():.2f}")

        rmse_assume = np.sqrt(((res_assume) ** 2).fillna(0).mean())

        print("RMSE Simulation", simulation, rmse_assume.mean())
        calculation.append(
        {
        "simulation": simulation,
        "entsoe_mean": preis_entsoe.mean(),
        "preis_mean": preis_assume.mean(), 
        "preis_max": preis_assume.max(),
        "preis_min": preis_assume.min(),
        "corref": corref_assume, 
        "mae": mae_assume.mean(),
        "mae_entsoe": mae_entsoe.mean(),
        "rmse": rmse_assume.mean(),
        "year": year,
        "nuts": simulation[12:17],
        })

    results_df = pd.DataFrame(calculation).set_index("simulation")
    results_df = results_df.sort_values("year")
    (results_df["entsoe_mean"]-results_df["entsoe_mean"].mean()).abs()
    results_df["preis_mean"].mean()

    results_df["mae"]/results_df["entsoe_mean"]

    plt.figure(figsize=(10,5))
    for name, group in results_df.groupby("nuts"):
        
        plt.plot(group["year"], group["corref"], label=name)
        plt.legend()
        plt.ylabel("correlation coefficient")
        plt.xlabel("year")
    savefig("correlation_plot")

    table_str = [r"~ & mean & MAE & RMSE & correlation \\ \hline"]
    for year, group in results_df.groupby("year"):
        e = group.iloc[0]
        table_str.append(fr"Historical {year} & {e.entsoe_mean:.2f} & ~ & ~ & ~\\")
        
        
        for idx, entry in group.sort_values("nuts").iterrows():
            
            table_str.append(fr"{entry.year} {entry.nuts} & {entry.preis_mean:.2f} & {entry.mae:.2f} & {entry.rmse:.2f} & {entry.corref:.2f} \\")
        table_str.append(r"\hline")
    #print("\n".join(table_str))
    
    table_new = (
        r"""
    \begin{table}[!ht]
        \centering
        \begin{tabular}{l|l|l|l|l}%s   \end{tabular}
        \caption{Resulting simulation characteristics in comparison to historic price series for different aggregations}
        \label{tab:quantitative results}
    \end{table}
        """  # noqa: UP031
            % "\n".join(table_str)
        )
    print(table_new)
    output_path = Path(base_path, "table.tex")
    with open(output_path, "w") as f:
        f.write(table_new)


if __name__ == "__main__":
    simulations = [
        "world_mastr_nuts1_entsoe_random_2019",
        "world_mastr_nuts1_entsoe_random_2023",
        "world_mastr_nuts1_entsoe_random_2024",
        "world_mastr_nuts1_entsoe_static_2023",
    ]

    simulation = "world_mastr_nuts1_entsoe_random_2024"
    # from_date = "2019-01-02"
    # to_date = "2019-12-31"
    # data = query_data(simulation, from_date, to_date)
    # plot_all_plots(simulation, from_date, to_date, data)
    results_pickle_path = Path("results.pkl")
    if results_pickle_path.is_file():
        with open(results_pickle_path, "rb") as f:
            results = pickle.load(f)
    else:
        results = {}


    for simulation in simulations:
        year = simulation.replace("_flexable", "")[-4:]

        from_date = f"{year}-01-02"
        to_date = f"{year}-12-30"
        if not results.get(simulation):
            print(f"querying data for {simulation}")
            data = query_data(simulation, from_date, to_date)
            results[simulation] = data

            nuts2_simulation = simulation.replace("nuts1", "nuts2")
            data = query_data(nuts2_simulation, from_date, to_date)
            results[nuts2_simulation] = data

            nuts3_simulation = simulation.replace("nuts1", "nuts3")
            data = query_data(nuts3_simulation, from_date, to_date)
            results[nuts3_simulation] = data
        plot_all_plots(simulation, from_date, to_date, results)

    with open(results_pickle_path, "wb") as f:
        pickle.dump(results, f)

    results_to_csv(results)

