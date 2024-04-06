# Backend

## To start:
Install requirements:
```
pip install -r requirements.txt
```

Set shell script to executable
```
chmod +x ./qblaunch.sh
```

Run:
```
./qblaunch.sh
```
The shell script sets up some environment variables, then launches the python program.

Once launched, you can see the apis on http://localhost:5501/docs (OpenAPI / Swagger)

Note: this has been run in Python 3.11.3. No guarantees for older versions of python. Recommend to setup `pyenv` on your system to keep newer version.


## Docker compose way of deploying

```
mkdir -p data/logs data/database data/uploads data/exports
docker compose up -d --build
```

