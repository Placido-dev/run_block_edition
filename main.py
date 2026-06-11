import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('URL')
EMAIL = os.getenv('MYEMAIL')
PASSWORD = os.getenv('PASS')
ORG_ID = 9418

PRESENCIAL_CLUSTERS = [
    136020, 137561, 136704, 137988, 136755, 136435, 137465, 138221,
    136793, 136950, 136910, 136571, 138288, 138286, 137304, 138816,
    136784, 136355, 136800, 136294, 137964, 138775, 138774, 147984,
    138284, 138283, 138285, 140716, 140814,
]

EAD_CLUSTERS = [
    135508, 135747, 136487, 135509, 135770, 136386, 135497, 136787, 138796,
]

PRESENCIAL_DATE = "2026-06-27 02:59:00"
EAD_DATE        = "2026-06-15 02:59:00" 


def authenticate():
    resp = requests.post(
        f"{BASE_URL}/auth/legacy",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("data", {}).get("jwt")
    if not token:
        raise ValueError(f"Token não encontrado na resposta: {data}")
    return token


def block_cluster(token: str, cluster_id: int, closing_date: str) -> bool:
    resp = requests.patch(
        f"{BASE_URL}/organizations/{ORG_ID}/clusters/{cluster_id}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "definitions": {
                "block_project_edition": {
                    "key": "block_project_edition",
                    "type": "boolean",
                    "value": "true",
                },
                "block_project_edition_closing_date": {
                    "key": "block_project_edition_closing_date",
                    "type": "datetime",
                    "value": closing_date,
                },
            }
        },
        timeout=40,
    )
    return resp.status_code in (200, 204)


def run_group(token: str, label: str, cluster_ids: list, closing_date: str):
    print(f"\n--- {label} ({len(cluster_ids)} clusters, bloqueio: {closing_date}) ---")
    ok, fail = [], []
    for cluster_id in cluster_ids:
        success = block_cluster(token, cluster_id, closing_date)
        if success:
            ok.append(cluster_id)
            print(f"  OK   {cluster_id}")
        else:
            fail.append(cluster_id)
            print(f"  FAIL {cluster_id}")
    print(f"  Resultado: {len(ok)} OK, {len(fail)} falhas.")
    if fail:
        print(f"  Falhas: {fail}")


def main():
    print("Autenticando...")
    token = authenticate()
    print("Token obtido.")

    run_group(token, "PRESENCIAL", PRESENCIAL_CLUSTERS, PRESENCIAL_DATE)
    run_group(token, "EAD",        EAD_CLUSTERS,        EAD_DATE)

    print("\nConcluído.")


if __name__ == "__main__":
    main()
