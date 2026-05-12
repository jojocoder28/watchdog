import pytest


@pytest.mark.asyncio
async def test_upload_log_file(auth_client, tmp_path):
    # Log format: [timestamp] LEVEL Service host env - message
    log_content = '[2023-10-01T12:00:00Z] INFO AuthService localhost test - User logged in\n'
    log_file = tmp_path / "test.log"
    log_file.write_text(log_content)

    with open(log_file, "rb") as f:
        response = await auth_client.post(
            "/logs/upload",
            files={"file": ("test.log", f, "text/plain")}
        )
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_upload_unsupported_format(auth_client, tmp_path):
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Hello world")

    with open(txt_file, "rb") as f:
        response = await auth_client.post(
            "/logs/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_generate_synthetic_logs(auth_client):
    # Route triggers a background task; response is immediate with a message
    response = await auth_client.post("/logs/generate?count=10")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_get_logs_paginated(auth_client):
    response = await auth_client.get("/logs/?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


@pytest.mark.asyncio
async def test_get_log_stats(auth_client):
    response = await auth_client.get("/logs/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_logs" in data
    assert "error_rate" in data
    assert "counts_by_level" in data
