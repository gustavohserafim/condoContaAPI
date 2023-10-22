import pytest, requests

api = "http://localhost:5000/api"

def test_get_balance():
    r = requests.get(api + "/account/1/balance")
    assert r.status_code == 200
    assert "balance" in r.json()


def test_get_fail_balance():
    r = requests.get(api + "/account/3/balance")
    assert r.status_code == 404


def test_get_statement():
    r = requests.get(api + "/account/1/statement")
    assert r.status_code == 200
    assert "transactions" in r.json()


def test_get_fail_statement():
    r = requests.get(api + "/account/3/statement")
    assert r.status_code == 200
    assert len(r.json()["transactions"]) == 0


def test_transfer():
    balance = requests.get(api + "/account/1/balance").json()["balance"]
    value = 1
    data = {"target_id": 2,  "value": value, "description": "1 real de pix"}
    r = requests.post(api + "/account/1/transfer", json=data)
    print(r.json())
    assert r.status_code == 200
    assert r.json()["balance"]


def test_fail_transfer():
    value = 99999
    data = {"target_id": 1,  "value": value, "description": "99999 reais de pix"}
    r = requests.post(api + "/account/1/transfer", json=data)
    assert r.status_code == 400

def test_transfer2():
    balance = requests.get(api + "/account/2/balance").json()["balance"]
    value = 1
    data = {"target_id": 1,  "value": value, "description": "1 real de pix"}
    r = requests.post(api + "/account/2/transfer", json=data)
    print(r.json())
    assert r.status_code == 200
    assert r.json()["balance"]


def test_fail_transfer2():
    value = 99999
    data = {"target_id": 1,  "value": value, "description": "99999 reais de pix"}
    r = requests.post(api + "/account/1/transfer", json=data)
    assert r.status_code == 400