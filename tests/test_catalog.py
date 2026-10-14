from app.scanner.catalog import CATALOG


def test_catalog_has_the_eight_initial_rules():
    assert [spec.code for spec in CATALOG] == [f"CRYPTO-{n:03d}" for n in range(1, 9)]


def test_catalog_codes_are_unique():
    assert len({spec.code for spec in CATALOG}) == len(CATALOG)


def test_every_rule_has_description_recommendation_and_reference():
    # Sección 10: cada hallazgo debe poder mostrar recomendación y referencia técnica.
    for spec in CATALOG:
        assert spec.description.strip(), spec.code
        assert spec.recommendation.strip(), spec.code
        assert spec.reference.strip(), spec.code