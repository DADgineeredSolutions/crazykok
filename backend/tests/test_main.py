from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_list_events_and_create_event():
    response = client.get('/events')
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)

    create_response = client.post(
        '/events',
        json={
            'name': 'Winter Market',
            'description': 'A short test event',
            'location': 'Assen',
            'event_date': '2026-12-01',
            'application_deadline': '2026-10-15',
            'organizer': 'Test Organizer',
            'category': 'Market',
            'application_status': 'watchlist',
            'source_url': 'https://example.com/winter-market',
            'notes': 'Follow up with organizer.',
            'expected_revenue': 500,
            'expected_attendance': 80,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created['name'] == 'Winter Market'
    assert created['location'] == 'Assen'
    assert created['application_status'] == 'watchlist'

    update_response = client.patch(
        f"/events/{created['id']}",
        json={
            'application_status': 'applied',
            'expected_revenue': 750,
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['application_status'] == 'applied'
    assert updated['expected_revenue'] == 750

    filtered_response = client.get('/events?status=applied&q=Assen')
    assert filtered_response.status_code == 200
    filtered = filtered_response.json()
    assert any(event['id'] == created['id'] for event in filtered)

    archive_response = client.post(f"/events/{created['id']}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()['is_active'] is False

    active_response = client.get('/events')
    assert all(event['id'] != created['id'] for event in active_response.json())

    archived_response = client.get('/events?active=false')
    assert any(event['id'] == created['id'] for event in archived_response.json())

    restore_response = client.post(f"/events/{created['id']}/restore")
    assert restore_response.status_code == 200
    assert restore_response.json()['is_active'] is True

    delete_response = client.delete(f"/events/{created['id']}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/events/{created['id']}")
    assert missing_response.status_code == 404
