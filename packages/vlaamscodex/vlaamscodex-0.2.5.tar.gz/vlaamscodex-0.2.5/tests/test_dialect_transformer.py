from __future__ import annotations

from vlaamscodex.dialects.transformer import available_packs, transform


def test_available_packs_has_80_plus_and_base() -> None:
    packs = available_packs()
    ids = {p.id for p in packs}
    assert len(packs) >= 80
    assert "nl/standard" in ids
    assert "vlaams/basis" in ids


def test_protected_terms_unchanged() -> None:
    text = (
        "Het is verplicht en verboden. "
        "Je mag niet roken. "
        "Je kan dit doen, maar je kan het ook laten. "
        "Je moet dit doen tenzij er een uitzondering is. "
        "Enkel en alleen dit, behalve in die uitzondering. "
        "Bij overtreding volgt een boete en een straf. "
        "Datum: 1 januari 2026. Bedrag: 10 euro."
    )
    out = transform(text, "vlaams/antwerps")
    out_lower = out.lower()

    for term in [
        "verplicht",
        "verboden",
        "mag",
        "niet",
        "moet",
        "kan",
        "tenzij",
        "enkel",
        "alleen",
        "behalve",
        "uitzondering",
        "boete",
        "straf",
        "1 januari 2026",
        "10",
    ]:
        assert term in out_lower

    # Extra guard: "mag niet" must remain intact.
    assert "mag niet" in out_lower


def test_idempotent_vlaams_basis() -> None:
    text = "Dat is wat jij zegt. Wat wil jij even kijken?"
    once = transform(text, "vlaams/basis")
    twice = transform(once, "vlaams/basis")
    assert once == twice


def test_idempotent_three_dialects() -> None:
    text = "Dat is wat jij zegt. Wat wil jij even kijken? Dat is goed en snel."
    for dialect_id in ["vlaams/antwerps", "vlaams/west-vlaams", "vlaams/limburgs"]:
        once = transform(text, dialect_id)
        twice = transform(once, dialect_id)
        assert once == twice


def test_snapshot_vlaams_basis() -> None:
    text = "Dat is wat jij zegt. Wat wil jij?"
    assert transform(text, "vlaams/basis") == "Da’s wat ge zegt. Wa wil ge?"


def test_snapshot_antwerps() -> None:
    text = "Dat is wat jij zegt. Wat wil jij even kijken?"
    assert transform(text, "vlaams/antwerps") == "Da’s wat ge zegt. Wa wil ge efkes kieke?"


def test_snapshot_west_vlaams() -> None:
    text = "Dat is goed. Wat wil jij even doen? Dat is snel."
    assert transform(text, "vlaams/west-vlaams") == "Da’s goe. Wa wil ge effen doen? Da’s rap."
