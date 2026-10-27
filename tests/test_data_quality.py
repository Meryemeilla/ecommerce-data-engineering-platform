
import ast
from pathlib import Path


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
