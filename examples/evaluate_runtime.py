# SPDX-FileCopyrightText: ASSUME Developers
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import matplotlib.pyplot as plt
import pandas as pd

# plt.style.use("seaborn-v0_8")


def plot_df(df, title="Time vs. n"):
    df.columns = ["n", "type", "time"]
    distrib_data = df[df["type"] == "distrib"]
    sync_data = df[df["type"] == "sync"]
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(distrib_data["n"], distrib_data["time"], label="distrib")
    plt.plot(sync_data["n"], sync_data["time"], label="sync")
    plt.xlabel("n")
    plt.ylabel("time")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig("scalability.svg")
    plt.show()


if __name__ == "__main__":
    ### RESULTS ###
    # results = [(1, 'distrib', 10.555368423461914), (1, 'sync', 8.060883045196533), (2, 'distrib', 10.997570276260376), (2, 'sync', 11.374260663986206), (3, 'distrib', 11.478757619857788), (3, 'sync', 14.855780601501465), (4, 'distrib', 12.92294454574585), (4, 'sync', 18.389983415603638), (5, 'distrib', 18.909234523773193), (5, 'sync', 24.365375518798828), (10, 'distrib', 27.40151834487915), (10, 'sync', 40.98110389709473), (20, 'distrib', 60.09907078742981), (20, 'sync', 74.69065427780151), (30, 'distrib', 101.84901762008667), (30, 'sync', 110.01267266273499), (40, 'distrib', 149.119637966156), (40, 'sync', 145.8321897983551), (50, 'distrib', 188.8543348312378), (50, 'sync', 189.90265107154846)]
    #          [(1, 'distrib', 12.669503450393677), (1, 'sync', 6.627783536911011), (2, 'distrib', 12.189964771270752), (2, 'sync', 9.727921962738037), (3, 'distrib', 11.60510540008545), (3, 'sync', 12.869911670684814), (4, 'distrib', 14.952376127243042), (4, 'sync', 16.52760100364685), (5, 'distrib', 15.294515371322632), (5, 'sync', 19.758689403533936)]
    # with factorial: [(2, 'distrib', 101.847238779068), (2, 'sync', 137.1397886276245), (3, 'distrib', 133.3344464302063), (3, 'sync', 183.33061480522156)]
    results = [
        (1, "distrib", 86.70252919197083),
        (1, "sync", 85.57720613479614),
        (2, "distrib", 86.29700827598572),
        (2, "sync", 128.40219473838806),
        (3, "distrib", 86.98923349380493),
        (3, "sync", 171.3158664703369),
        (4, "distrib", 89.0415186882019),
        (4, "sync", 215.32295036315918),
        (5, "distrib", 88.34683990478516),
        (5, "sync", 256.6751756668091),
        (10, "distrib", 90.5095751285553),
        (10, "sync", 473.23365235328674),
        (20, "distrib", 90.68335509300232),
        (20, "sync", 902.449613571167),
    ]
    # with factorial3000
    # results = [(1, 'distrib', 19.7316312789917), (1, 'sync', 20.03235411643982), (2, 'distrib', 20.079488039016724), (2, 'sync', 30.039849758148193), (3, 'distrib', 19.912079095840454), (3, 'sync', 40.158170223236084), (4, 'distrib', 20.29887580871582), (4, 'sync', 50.28711271286011), (5, 'distrib', 20.173094987869263), (5, 'sync', 60.51260948181152), (10, 'distrib', 21.535311460494995), (10, 'sync', 111.26599168777466), (20, 'distrib', 22.484151601791382), (20, 'sync', 212.29513502120972)]

    # without sleep
    results = [
        (1, "distrib", 4.656896352767944),
        (1, "sync", 4.754611015319824),
        (2, "distrib", 4.97237229347229),
        (2, "sync", 7.18564510345459),
        (3, "distrib", 5.0078957080841064),
        (3, "sync", 9.687503099441528),
        (4, "distrib", 4.877830505371094),
        (4, "sync", 12.065383911132812),
        (5, "distrib", 4.925901651382446),
        (5, "sync", 14.451001405715942),
        (10, "distrib", 5.204180479049683),
        (10, "sync", 26.491638898849487),
        (20, "distrib", 6.39190673828125),
        (20, "sync", 51.88937783241272),
    ]
    df = pd.DataFrame(results)
    df.columns = ["n", "type", "time"]
    # df = df[df['type'] == 'distrib']
    plot_df(df, "distributed vs sync market simulation")

    # with sleep 0.1:
    results = [
        (1, "distrib", 16.063899278640747),
        (1, "sync", 16.43594765663147),
        (2, "distrib", 16.190110206604004),
        (2, "sync", 24.765042066574097),
        (3, "distrib", 16.319480180740356),
        (3, "sync", 33.15579319000244),
        (4, "distrib", 16.25517463684082),
        (4, "sync", 41.51949644088745),
        (5, "distrib", 16.428024530410767),
        (5, "sync", 49.85216522216797),
        (10, "distrib", 16.881711959838867),
        (10, "sync", 91.258465051651),
        (20, "distrib", 17.780423879623413),
        (20, "sync", 175.31689071655273),
    ]

    df = pd.DataFrame(results)
    df.columns = ["n", "type", "time"]
    # df = df[df["type"] == "distrib"]
    plot_df(df, "with sleep 0.1")

    # with small asyncio sleep
    results = [
        (1, "sync", 6.539939641952515),
        (2, "sync", 9.403020858764648),
        (3, "sync", 12.36292028427124),
        (4, "sync", 15.29703402519226),
        (5, "sync", 18.154977798461914),
        (10, "sync", 33.208897829055786),
        (20, "sync", 63.78745460510254),
        (1, "distrib", 6.288804292678833),
        (2, "distrib", 6.333474159240723),
        (3, "distrib", 6.424114465713501),
        (4, "distrib", 6.51146674156189),
        (5, "distrib", 6.629356145858765),
        (10, "distrib", 6.956280946731567),
        (20, "distrib", 7.821327209472656),
        (30, "distrib", 9.141918659210205),
        (40, "distrib", 10.433382272720337),
        (50, "distrib", 12.249194145202637),
        (60, "distrib", 14.284798383712769),
        (70, "distrib", 17.28959321975708),
        (80, "distrib", 18.698351860046387),
        (90, "distrib", 21.427669286727905),
        (100, "distrib", 23.74718403816223),
        (200, "distrib", 46.01329803466797),
        (300, "distrib", 69.93286800384521),
        (400, "distrib", 98.45339846611023),
    ]

    # results = [(1, 'distrib', 6.288804292678833), (2, 'distrib', 6.333474159240723), (3, 'distrib', 6.424114465713501), (4, 'distrib', 6.51146674156189), (5, 'distrib', 6.629356145858765), (10, 'distrib', 6.956280946731567), (20, 'distrib', 7.821327209472656)]
    results = [
        (1, "distrib", 16.220808029174805),
        (2, "distrib", 16.252318620681763),
        (3, "distrib", 16.365472555160522),
        (4, "distrib", 16.490203142166138),
        (5, "distrib", 16.646419286727905),
        (6, "distrib", 16.790594577789307),
        (7, "distrib", 16.89653444290161),
        (8, "distrib", 17.03147554397583),
        (9, "distrib", 17.23230290412903),
        (10, "distrib", 17.34104585647583),
        (11, "distrib", 17.52985119819641),
        (12, "distrib", 17.708966970443726),
        (13, "distrib", 17.919740438461304),
        (14, "distrib", 18.129363775253296),
        (15, "distrib", 18.346499919891357),
        (16, "distrib", 18.598717212677002),
        (17, "distrib", 18.69514012336731),
        (18, "distrib", 18.91413140296936),
        (19, "distrib", 19.189096927642822),
        (20, "distrib", 19.352171182632446),
        (21, "distrib", 19.73521637916565),
        (22, "distrib", 19.877938985824585),
        (23, "distrib", 20.194964170455933),
        (24, "distrib", 20.426095962524414),
        (25, "distrib", 20.883025407791138),
        (26, "distrib", 21.05681610107422),
        (27, "distrib", 21.39689874649048),
        (28, "distrib", 21.720005750656128),
        (29, "distrib", 22.01751470565796),
        (30, "distrib", 22.826749086380005),
        (31, "distrib", 22.85327386856079),
    ]

    results = [
        (1, 16, "distrib", 135.37044620513916),
        (1, 16, "sync", 2.384185791015625e-07),
        (2, 8, "distrib", 69.59016013145447),
        (2, 8, "sync", 2.384185791015625e-07),
        (4, 4, "distrib", 36.34075331687927),
        (4, 4, "sync", 4.76837158203125e-07),
        (8, 2, "distrib", 19.4949471950531),
        (8, 2, "sync", 0.0),
        (16, 1, "distrib", 18.047470808029175),
        (16, 1, "sync", 2.384185791015625e-07),
    ]

    [
        (1, 16, "distrib", 40.42783498764038),
        (1, 16, "sync", 2.384185791015625e-07),
        (2, 8, "distrib", 22.184062480926514),
        (2, 8, "sync", 2.384185791015625e-07),
        (4, 4, "distrib", 12.978170156478882),
        (4, 4, "sync", 2.384185791015625e-07),
        (8, 2, "distrib", 7.828178405761719),
        (8, 2, "sync", 0.0),
        (16, 1, "distrib", 6.24575400352478),
        (16, 1, "sync", 2.384185791015625e-07),
    ]

    df = pd.DataFrame(results)
    df.columns = ["n", "m", "type", "time"]
    df = df[df["type"] == "distrib"]
    df["speedup"] = df["time"].iloc[0] / df["time"]
    del df["m"]
    plot_df(df, "16 agents with n CPUs")

    import json

    with open("runtime_tests.json") as f:
        results = json.load(f)

    df = pd.read_json("runtime_tests.json")
    df.columns = ["n", "m", "type", "time"]
    df["speedup"] = df["time"].iloc[0] / df["time"]
    plt.figure(figsize=(10, 6))
    plt.plot(df["n"], df["time"], label="wall time")
    plt.xlabel("n Cores")
    plt.ylabel("wall time in seconds")
    plt.title("Speedup graph of simulation with 16 agents")
    plt.legend()
    plt.grid(True)
    plt.savefig("scalability.svg")
    plt.show()
