
import ast
from pathlib import Path
import importlib.util
import sys
from unittest.mock import MagicMock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUALITY_SCRIPT = PROJECT_ROOT / "src" / "database" / "data_quality.py"


def load_checks():
    """Récupère le dictionnaire CHECKS sans exécuter le script."""
    source = QUALITY_SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == "CHECKS"
                for target in node.targets
            ):
                return ast.literal_eval(node.value)

    raise AssertionError("Le dictionnaire CHECKS est introuvable.")


def test_quality_checks_are_defined():
    checks = load_checks()

    assert len(checks) == 11


def test_each_quality_check_contains_a_select_count():
    checks = load_checks()

    for check_name, query in checks.items():
        assert "SELECT COUNT(*)" in query.upper(), check_name


def test_expected_business_rules_are_present():
    checks = load_checks()

    expected_rules = [
        "Clients sans email",
        "Produits sans nom",
        "Produits avec prix négatif",
        "Commandes sans client valide",
        "Lignes de commande sans produit valide",
    ]

    for rule in expected_rules:
        assert rule in checks


def load_quality_module():
    spec = importlib.util.spec_from_file_location(
        "data_quality",
        QUALITY_SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_succeeds_when_no_anomalies(monkeypatch):
    module = load_quality_module()

    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_connection.cursor.return_value.__enter__.return_value = fake_cursor

    fake_cursor.fetchone.return_value = (0,)

    monkeypatch.setattr(module, "get_connection", lambda: fake_connection)

    module.main()

    fake_connection.close.assert_called_once()


def test_main_exits_with_error_when_anomalies_exist(monkeypatch):
    module = load_quality_module()

    fake_connection = MagicMock()
    fake_cursor = MagicMock()
    fake_connection.cursor.return_value.__enter__.return_value = fake_cursor

    fake_cursor.fetchone.side_effect = [(1,)] + [(0,)] * 10

    monkeypatch.setattr(module, "get_connection", lambda: fake_connection)

    with pytest.raises(SystemExit) as error:
        module.main()

    assert error.value.code == 1
    fake_connection.close.assert_called_once()


def test_get_connection_uses_environment_variables(monkeypatch):
    module = load_quality_module()

    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "ecommerce")
    monkeypatch.setenv("DB_USER", "ecommerce_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    fake_connection = MagicMock()
    monkeypatch.setattr(
        module.psycopg2,
        "connect",
        MagicMock(return_value=fake_connection),
    )

    result = module.get_connection()

    assert result is fake_connection
    module.psycopg2.connect.assert_called_once_with(
        host="localhost",
        port="5433",
        database="ecommerce",
        user="ecommerce_user",
        password="test_password",
    )


def test_main_exits_when_database_error_occurs(monkeypatch, capsys):
    module = load_quality_module()

    monkeypatch.setattr(
        module,
        "get_connection",
        MagicMock(side_effect=module.psycopg2.Error("Erreur simulée")),
    )

    with pytest.raises(SystemExit) as error:
        module.main()

    assert error.value.code == 1

    captured = capsys.readouterr()
    assert "ERREUR BASE DE DONNÉES" in captured.err
