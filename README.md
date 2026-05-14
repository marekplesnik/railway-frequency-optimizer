# railway-frequency-optimizer

> A CLI tool to maximize direct travelers in a railway network (or other public transport systems) by optimizing train frequencies using either **Mixed Integer Programming (MIP)** or **Simulated Annealing (SA)**.

## Dependencies

> - Python 3.11.9  
> - numpy  
> - networkx  
> - scipy  
> - matplotlib  
> - gurobipy (required for MIP solver)

## Usage

> python main.py [arguments]

## Arguments

> --network (str, default -> random)  
> Path to a network file or `random` to generate one

> --solver (str, default -> mip)  
> `mip` (Gurobi) or `sa` (Simulated Annealing)

> --stations (int, default -> 30)  
> Number of stations

> --classification_yards (int, default -> 5)  
> Number of hub stations

> --capacity (int, default -> 500)  
> Passenger capacity per train

> --demand_probability (float, default -> 0.2)  
> Probability that demand exists between any pair of stations

> --min_demand (int, default -> 10)  
> Minimum demand value for generated OD pairs

> --max_demand (int, default -> 20)  
> Maximum demand value for generated OD pairs

> --visualize (flag, default -> False)  
> If set, displays the network graph and active lines

> --seed (int, default -> 42)  
> Random seed

## Network File Format

> If loading a network from a file, the structure should include (as seen in `data/pid.txt`):

> Capacity  
> Single integer defining train capacity

> Stations  
> List of station IDs

> Classification Yards  
> List of hub station IDs

> Connections  
> station_a station_b weight  
> station_a station_b weight  
> ...

> Demands  
> station_a station_b amount  
> station_a station_b amount  
> ...

## References

> Bussieck, M. R., Kreuzer, P., & Zimmermann, U. T. (1996).  
> *Optimal lines for railway systems*.  
> European Journal of Operational Research, 96(1), 54--63.

## Notes

> - Optimized for Python 3.11.9  
> - MIP mode requires a working installation of **Gurobi**  
> - Simulated Annealing algorithm was developed in a practical class and is only reformulated for this problem