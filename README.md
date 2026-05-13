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

## Notes

> - Optimized for Python 3.11.9
> - MIP mode requires a working installation of **Gurobi**
> - Simulated Annealing algorithm was developed in a practical class and is only reformulated for this problem