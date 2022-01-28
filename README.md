# blueprint-py

## Steps to run:
* Install and setup a local MongoDB instance. See https://docs.mongodb.com/manual/installation/
* Install Python 3.9+
    ```bash
      $ git clone https://github.com/IOverflow/blueprint-py.git
    ```
    ```bash
      $ cd blueprint-py
    ```

* Create a virtual environment for the project
    ```bash
    $ python -m venv .
    ```

* Install dependencies
    ```bash
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    ```
  
* Run backend

    ```bash
  $ uvicorn src.main:api --reload
    ```
  
## Run with docker
```bash
  $ docker build -t  blueprint-image .
  $ docker run -d --name blueprint-container -p 8000:8000 blueprint-image
```