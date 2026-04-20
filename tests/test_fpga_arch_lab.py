import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from fpga_arch_lab import build_architecture_report, load_catalog, readiness_label, risk_score


def test_negative_slack_ip_is_highest_risk():
    catalog, blocks = load_catalog(PROJECT / "data" / "ip_catalog.json")
    report = build_architecture_report(catalog, blocks)

    highest = report["highest_risk_blocks"][0]

    assert highest["name"] in {"high_speed_serial_transceiver", "cxl_type3_endpoint"}
    assert highest["risk_score"] >= 70
    assert highest["readiness"] == "high risk"


def test_single_domain_esram_is_low_risk():
    _, blocks = load_catalog(PROJECT / "data" / "ip_catalog.json")
    esram = next(block for block in blocks if block.name == "esram_scratchpad")

    assert readiness_label(risk_score(esram)) == "ready"


def test_architecture_summary_counts_all_ip_blocks():
    catalog, blocks = load_catalog(PROJECT / "data" / "ip_catalog.json")
    report = build_architecture_report(catalog, blocks)

    assert report["ip_count"] == 8
    assert report["total_bandwidth_gbps"] > 600
    assert report["high_risk_count"] >= 1

