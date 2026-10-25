from fastapi.testclient import TestClient

from rgb_website.main import create_app


def test_start_page_and_static_assets_are_available() -> None:
    client = TestClient(create_app())

    page = client.get("/")
    stylesheet = client.get("/styles.css")
    script = client.get("/app.js")
    impressum = client.get("/impressum")
    privacy = client.get("/datenschutz")

    assert page.status_code == 200
    assert page.headers["cache-control"] == "no-store"
    assert "Farb-Emotions-Studie" in page.text
    assert impressum.status_code == 200
    assert privacy.status_code == 200
    assert "age-confirmed" in page.text
    assert "information-acknowledged" in page.text
    assert "participation-consent" in page.text
    assert '<script src="/app.js" defer></script>' in page.text
    assert stylesheet.status_code == 200
    assert "emotion-grid" in stylesheet.text
    assert script.status_code == 200
    assert script.headers["cache-control"] == "no-store"
    assert '"/api/experiments"' in script.text
    assert "/api/experiments/${encodeURIComponent(state.sessionId)}/responses" in (
        script.text
    )
    assert "/api/experiments/${encodeURIComponent(state.sessionId)}/abandon" in (
        script.text
    )
    assert "function resetStudyState()" in script.text
    assert "resetStudyState();" in script.text
    assert "startButton.disabled = false;" in script.text
    assert 'abandonButton.addEventListener("click", abandonStudy)' in script.text
    assert 'button.addEventListener("click", () => submitEmotion(emotion))' in (
        script.text
    )
    assert "localStorage" not in script.text
    assert "sessionStorage" not in script.text
    assert script.text.count('"Wut"') == 1
    assert script.text.count('"Angst"') == 1
    assert script.text.count('"Freude"') == 1
    assert script.text.count('"Traurigkeit"') == 1
    assert '"Trauer"' not in script.text
    assert script.text.count('"Überraschung"') == 1
    assert script.text.count('"Verachtung"') == 1
    assert script.text.count('"Ekel"') == 1
    assert '"Vertrauen"' not in script.text
    assert 'name="gender"' in page.text
