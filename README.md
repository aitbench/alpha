# AITB

AI Trader Bench Alpha. Currently just downloads the data and nuggets it to visualize it. Build path is now active.

## Requirements
```pip
pip install -r requirements.txt
```

## Run
```bash
python app.py
```
Then go to http://localhost:5000/register
Then sign in http://localhost:5000/login

## Diagrams
```mermaid
graph LR
    A>Connection] --> B[(Data 1m)]-->C[Samples]
    D([TimeFrame])-->C
    C-->E[Nuggets]
    F([Riches])-->G(Enrichments X)-->E
    H([Dependant y])-->E
    E-->I((Observatorium))
    E-->J((AI))
    I-->K[View]
    I-->L[Correlate]
    I-->M[Feature Selection]
```
