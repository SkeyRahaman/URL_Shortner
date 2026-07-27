import pytest

@pytest.mark.asyncio
async def test_full_link_lifecycle(async_client):
    # 1. Create a link
    res1 = await async_client.post(
        "/links",
        json={"original_url": "https://fullflow.com", "custom_slug": "my-flow"},
        headers={"X-User-Id": "1"}
    )
    assert res1.status_code == 201
    slug = res1.json()["slug"]
    assert slug == "my-flow"

    # 2. Get details
    res2 = await async_client.get(f"/links/{slug}/details")
    assert res2.status_code == 200

    # 3. Redirect
    res3 = await async_client.get(f"/links/{slug}", follow_redirects=False)
    assert res3.status_code == 302

    # 4. List user links
    res4 = await async_client.get("/links", headers={"X-User-Id": "1"})
    assert res4.status_code == 200
    links = res4.json()
    assert len([l for l in links if l["slug"] == slug]) == 1

    # 5. Delete link
    res5 = await async_client.delete(f"/links/{slug}", headers={"X-User-Id": "1"})
    assert res5.status_code == 200

    # 6. Verify deleted
    res6 = await async_client.get(f"/links/{slug}/details")
    assert res6.status_code == 404
