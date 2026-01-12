from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activities from initial data
    assert "Basketball" in data
    assert "Programming Class" in data


def test_signup_and_unregister_flow():
    activity = "Basketball"
    email = "testuser@example.com"

    # Ensure the test email is not already registered
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        # If somehow already present, unregister first
        client.delete(f"/activities/{activity}/unregister?email={email}")

    # Sign up the test user
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify user now present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Signing up again should return 400 (already signed up)
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Unregister the user
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Unregistering again should return 404
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 404


def test_signup_unsubscribe_invalid_activity():
    resp = client.post("/activities/NoSuch/signup?email=foo@example.com")
    assert resp.status_code == 404

    resp = client.delete("/activities/NoSuch/unregister?email=foo@example.com")
    assert resp.status_code == 404
