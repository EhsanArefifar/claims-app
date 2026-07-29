def test_health(client_no_db):
    response = client_no_db.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok!"


def test_create_claim_missing_required_field_returns_422(client_no_db):
    # incident_date is required on ClaimCreate (no default), omitting it
    # is caught by Pydantic before the DB layer ever runs — no seeded_db needed
    payload = {
        "policy_id": "00000000-0000-0000-0000-000000000001",
        "description": "Broken windshield",
        # incident_date intentionally omitted
    }
    response = client_no_db.post("/claims/", json=payload)
    assert response.status_code == 422


def test_create_claim(client, seeded_db):
    policy = seeded_db["policy"]

    payload = {
        "policy_id": str(policy.id),
        "description": "Broken windshield",
        "incident_date": "2026-01-15"
    }

    response = client.post("/claims/", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["incident_date"] == "2026-01-15"
    assert body["policy_id"] == payload["policy_id"]
    assert body["description"] == "Broken windshield"
    assert body["status"] == "Submitted"
    assert body["reference_number"] is not None


def test_get_claim_exists(client, seeded_db):
    policy = seeded_db["policy"]

    # Create a claim first so we have a known ID to fetch
    payload = {
        "policy_id": str(policy.id),
        "description": "Cracked bumper",
        "incident_date": "2026-03-10",
    }
    post_response = client.post("/claims/", json=payload)
    assert post_response.status_code == 200, f"Setup POST failed: {post_response.text}"
    created = post_response.json()

    response = client.get(f"/claims/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["policy_id"] == str(policy.id)
    assert body["description"] == "Cracked bumper"
    assert body["incident_date"] == "2026-03-10"
    assert body["status"] == "Submitted"


def test_get_claim_not_found(client):
    random_id = "00000000-0000-0000-0000-000000000099"
    response = client.get(f"/claims/{random_id}")
    assert response.status_code == 404


def test_list_claims(client, seeded_db):
    policy = seeded_db["policy"]

    # Create two claims
    payloads = [
        {"policy_id": str(policy.id), "description": "Flat tyre",    "incident_date": "2026-04-01"},
        {"policy_id": str(policy.id), "description": "Stolen radio", "incident_date": "2026-04-02"},
    ]
    created_ids = set()
    for p in payloads:
        r = client.post("/claims/", json=p)
        assert r.status_code == 200, f"Setup POST failed: {r.text}"
        created_ids.add(r.json()["id"])

    response = client.get("/claims/")

    assert response.status_code == 200
    returned_ids = {c["id"] for c in response.json()}
    assert returned_ids == created_ids