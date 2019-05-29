## Installing a Virtual Environment
#### Reference : https://virtualenv.pypa.io/en/stable/installation/

#### Prerequisites:

Installing PiP

```console
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`

python get-pip.py --user
```

### Install virtualenv  
```console
pip install --user virtualenv
```

Create a folder in tesseract/parsers to house the virtual environment (env). Also, specify this project is using python3  
```console
virtualenv -p python3 env
```

Freezing dependencies
```console
pip freeze > requirements.txt
```

Activate environment  
```console
. env/bin/activate
```

Installing dependencies
```console
pip install -r requirements.txt
```

Running the code
```console
python3 run.py --device /dev/path_to_device --baud 115200
```



To stop the virtual session  
```console
deactivate
```