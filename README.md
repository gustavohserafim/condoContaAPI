# condoContaAPI
Para executar:

Criar e ativar venv
```
cd condoContaAPI
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
flask run
```

## Testes

em outro terminal:
```
cd condoContaAPI
source .venv/Scripts/activate
pytest .\test_api.py
```

## Tecnologias
```
Python 3.11
Flask
SQLite
SQLAlchemy
pytest
```
## Endpoints
GET - `/api/account/<id_da_conta>/balance` - Pega o saldo da conta

GET - `/api/account/<id_da_conta>/statement` - Pega o extrato da conta

POST - `/api/account/<id_da_conta_origem>/transfer` - Realiza transfêrencia entre contas, necessario envio do body em JSON:
```
{
    "target_id": 1, // id da conta destion
    "value": 1, // valor da transfêrencia
    "description": "1 real de pix" // Descrição da transferência
}
```
