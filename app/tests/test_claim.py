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
