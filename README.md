# condoContaAPI
Para executar:

cd condoContaAPI

python -m venv .venv

source .venv/Scripts/activate

pip install -r requirements.txt

flask run

# Testes

em outro terminal:

cd condoContaAPI

source .venv/Scripts/activate

pytest .\test_api.py
