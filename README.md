# MARS crop-management RL

```powershell
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cpu
.\.venv\Scripts\python.exe scripts/smoke_ppo.py --device cuda
```

## docker build
git clone https://gitlab.inria.fr/rgautron/dssat-csm-os.git vendor/dssat-pdi-source
git clone https://gitlab.inria.fr/rgautron/gym_dssat_pdi.git vendor/gym_dssat_pdi
