# mangal standalone, local database

This package will let you run a local, offline, standalone `mangal` database and
API. It *should* be the default when trying to upload data. This version uses
`sqlite` to store the data in a local file.

## Installation

```
sudo make requirements
make mangal
```

## Start the server

```
./manage.py runserver
```

Then simply point your browser to `http://localhost:8000`.
