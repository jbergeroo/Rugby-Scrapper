# Rugby-Scrapper

### Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements
```

### Use

Run 

```bash
python rugby-scrapper.py
```

The machine must be connected to a vpn in France in order to work. You will need to create an account via IFTTT. The notification will have a parameter **value1** that is passed so you can use it in IFTTT. In the main file, you can specify the matches you want to retreive along with all the persons that you want to send the notifications via IFTTT (simply add their code).