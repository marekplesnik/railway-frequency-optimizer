# Samples

## Random Network (Mixed Integer Programing)

```
python main.py --network random --solver mip --stations 30 --classification_yards 5 --capacity 500
```

## Random Network (Simulated Annealing)

```
python main.py --network random --solver sa --stations 50 --classification_yards 8 --capacity 400
```

## Custom Network

```
python main.py --network data/pid.txt --solver mip
```

## Visualization Mode

```
python main.py --network random --solver sa --visualize
```