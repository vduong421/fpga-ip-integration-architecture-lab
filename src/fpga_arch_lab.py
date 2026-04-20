from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


@dataclass(frozen=True)
class IpBlock:
    name: str
    category: str
    bandwidth_gbps: float
    latency_ns: float
    area_kle: float
    power_mw: float
    clock_domains: list[str]
    reset_domains: list[str]
    timing_slack_ns: float
    constraint_ready: bool
    integration_notes: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> "IpBlock":
        return cls(
            name=data["name"],
            category=data["category"],
            bandwidth_gbps=float(data["bandwidth_gbps"]),
            latency_ns=float(data["latency_ns"]),
            area_kle=float(data["area_kle"]),
            power_mw=float(data["power_mw"]),
            clock_domains=list(data["clock_domains"]),
            reset_domains=list(data["reset_domains"]),
            timing_slack_ns=float(data["timing_slack_ns"]),
            constraint_ready=bool(data["constraint_ready"]),
            integration_notes=list(data["integration_notes"]),
        )


def risk_score(block: IpBlock) -> int:
    score = 0
    if block.timing_slack_ns < 0:
        score += 35
    elif block.timing_slack_ns < 0.05:
        score += 20
    elif block.timing_slack_ns < 0.15:
        score += 10

    score += max(0, len(block.clock_domains) - 1) * 8
    score += max(0, len(block.reset_domains) - 1) * 5

    if not block.constraint_ready:
        score += 25
    if block.power_mw > 900:
        score += 10
    if block.area_kle > 130:
        score += 8

    return min(score, 100)


def readiness_label(score: int) -> str:
    if score >= 70:
        return "high risk"
    if score >= 40:
        return "needs review"
    return "ready"


def analyze_block(block: IpBlock) -> dict:
    score = risk_score(block)
    return {
        "name": block.name,
        "category": block.category,
        "risk_score": score,
        "readiness": readiness_label(score),
        "bandwidth_gbps": block.bandwidth_gbps,
        "latency_ns": block.latency_ns,
        "area_kle": block.area_kle,
        "power_mw": block.power_mw,
        "clock_domain_count": len(block.clock_domains),
        "reset_domain_count": len(block.reset_domains),
        "timing_slack_ns": block.timing_slack_ns,
        "constraint_ready": block.constraint_ready,
        "review_actions": review_actions(block, score),
    }


def review_actions(block: IpBlock, score: int) -> list[str]:
    actions: list[str] = []
    if block.timing_slack_ns < 0:
        actions.append("open timing-closure review before integration freeze")
    elif block.timing_slack_ns < 0.05:
        actions.append("watch near-zero timing slack during place and route")
    if len(block.clock_domains) > 2:
        actions.append("run CDC review for multi-clock integration")
    if len(block.reset_domains) > 2:
        actions.append("run RDC review for reset sequencing")
    if not block.constraint_ready:
        actions.append("complete generated-clock and IO constraint package")
    if block.power_mw > 900:
        actions.append("include power and thermal budget review")
    if score >= 70:
        actions.append("track as architecture-level integration risk")
    return actions or ["ready for normal integration checklist"]


def load_catalog(path: Path) -> tuple[dict, list[IpBlock]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, [IpBlock.from_dict(item) for item in data["ip_blocks"]]


def build_architecture_report(catalog: dict, blocks: list[IpBlock]) -> dict:
    analyzed = [analyze_block(block) for block in blocks]
    high_risk = [item for item in analyzed if item["readiness"] == "high risk"]
    needs_review = [item for item in analyzed if item["readiness"] == "needs review"]

    return {
        "target_device": catalog["target_device"],
        "architecture_goal": catalog["architecture_goal"],
        "ip_count": len(blocks),
        "total_bandwidth_gbps": round(sum(block.bandwidth_gbps for block in blocks), 2),
        "average_latency_ns": round(mean(block.latency_ns for block in blocks), 2),
        "total_area_kle": round(sum(block.area_kle for block in blocks), 2),
        "total_power_mw": round(sum(block.power_mw for block in blocks), 2),
        "high_risk_count": len(high_risk),
        "needs_review_count": len(needs_review),
        "highest_risk_blocks": sorted(analyzed, key=lambda item: item["risk_score"], reverse=True)[:3],
        "blocks": analyzed,
    }


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# FPGA IP Integration Architecture Report",
        "",
        f"Target device: `{report['target_device']}`",
        f"Architecture goal: {report['architecture_goal']}",
        "",
        "## Summary",
        "",
        f"- IP blocks reviewed: {report['ip_count']}",
        f"- Total modeled bandwidth: {report['total_bandwidth_gbps']} Gbps",
        f"- Average modeled latency: {report['average_latency_ns']} ns",
        f"- Total modeled area: {report['total_area_kle']} KLE",
        f"- Total modeled power: {report['total_power_mw']} mW",
        f"- High-risk blocks: {report['high_risk_count']}",
        f"- Blocks needing review: {report['needs_review_count']}",
        "",
        "## Highest Risk Blocks",
        "",
    ]
    for item in report["highest_risk_blocks"]:
        lines += [
            f"### {item['name']} ({item['category']})",
            "",
            f"- Risk score: {item['risk_score']} ({item['readiness']})",
            f"- Timing slack: {item['timing_slack_ns']} ns",
            f"- Clock domains: {item['clock_domain_count']}",
            f"- Reset domains: {item['reset_domain_count']}",
            f"- Constraint ready: {item['constraint_ready']}",
            "- Review actions:",
        ]
        lines += [f"  - {action}" for action in item["review_actions"]]
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze FPGA IP integration architecture risk.")
    parser.add_argument("--catalog", type=Path, default=Path("data/ip_catalog.json"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()

    catalog, blocks = load_catalog(args.catalog)
    report = build_architecture_report(catalog, blocks)
    args.output.mkdir(parents=True, exist_ok=True)

    json_path = args.output / "fpga_architecture_report.json"
    md_path = args.output / "fpga_architecture_report.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, md_path)

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()

