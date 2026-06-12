"""Rule-based mitigation recommendations for supply chain risk events."""

from typing import List


RISK_TYPE_ACTIONS = {
    "Geopolitical": (
        "Map tier-1 and tier-2 dependencies in the affected country and activate "
        "an alternate-country sourcing review."
    ),
    "Natural Disaster": (
        "Confirm supplier business-continuity status, logistics access, and the "
        "earliest credible production recovery date."
    ),
    "Logistics": (
        "Compare alternate ports, routes, and premium-freight options against "
        "current inventory coverage."
    ),
    "Supplier Financial": (
        "Request updated liquidity and capacity evidence, then prepare a dual-source "
        "or supplier-support decision."
    ),
    "Quality": (
        "Contain suspect inventory, launch an 8D corrective-action review, and verify "
        "approved backup capacity."
    ),
    "Cybersecurity": (
        "Confirm order and shipment visibility through an alternate channel and "
        "require a supplier recovery and data-integrity plan."
    ),
    "Labor": (
        "Validate strike or staffing scenarios with the supplier and model inventory "
        "coverage for each expected disruption window."
    ),
    "Regulatory": (
        "Review compliance exposure with legal and engineering teams and identify "
        "approved materials or suppliers that meet the new requirement."
    ),
    "Capacity": (
        "Reconfirm firm capacity allocations, expedite tooling or line-rate options, "
        "and reserve qualified backup volume."
    ),
    "Commodity": (
        "Review indexed pricing, available inventory, and substitute-grade options "
        "before the next sourcing commitment."
    ),
}


COMPONENT_ACTIONS = {
    "Semiconductors": (
        "Check chip-level bills of material, broker controls, redesign options, and "
        "allocation agreements for the affected semiconductor."
    ),
    "Battery Cells": (
        "Review cell chemistry interchangeability, homologation lead time, and "
        "contracted capacity at alternate plants."
    ),
    "Wiring Harnesses": (
        "Assess manual transfer capacity, alternate harness plants, and vehicle-build "
        "sequencing options by configuration."
    ),
    "Electric Motors": (
        "Review alternate motor specifications, inverter compatibility, and tooling "
        "lead times before reallocating production."
    ),
    "Rare Earth Magnets": (
        "Secure near-term magnet inventory and evaluate approved motor designs with "
        "lower rare-earth dependency."
    ),
    "Aluminum Castings": (
        "Check tooling mobility, alternate foundry capacity, and machining validation "
        "requirements for the affected casting."
    ),
    "Steel": (
        "Confirm grade-level inventory and evaluate qualified mills or approved "
        "material substitutions."
    ),
    "Tires": (
        "Compare approved tire fitments, regional inventory, and vehicle-allocation "
        "changes that preserve regulatory compliance."
    ),
    "Seats": (
        "Review trim-level substitution, build sequencing, and alternate foam or frame "
        "capacity."
    ),
    "Brake Systems": (
        "Verify safety-stock coverage and begin engineering validation of approved "
        "brake-system alternatives."
    ),
    "Infotainment Modules": (
        "Evaluate software-compatible module variants and prioritize available units "
        "for higher-margin vehicle programs."
    ),
    "Power Electronics": (
        "Review inverter and converter interchangeability, thermal validation, and "
        "alternate semiconductor content."
    ),
    "Glass": (
        "Check homologated glass variants, mold availability, and alternate regional "
        "capacity."
    ),
    "Resins": (
        "Validate alternate resin grades with engineering and reserve qualified "
        "compounder capacity."
    ),
    "Fasteners": (
        "Identify specification-equivalent fasteners and place a controlled bridge "
        "order with an approved alternate supplier."
    ),
}


def generate_recommendations(
    risk_type: str,
    affected_component: str,
    risk_level: str = "Medium",
) -> List[str]:
    """Return prioritized actions using risk, component, and urgency rules."""
    actions = []

    risk_action = RISK_TYPE_ACTIONS.get(
        risk_type,
        "Validate the event with the supplier and identify the fastest qualified "
        "mitigation path.",
    )
    component_action = COMPONENT_ACTIONS.get(
        affected_component,
        "Review inventory coverage, alternate suppliers, and engineering substitution "
        "options for the affected component.",
    )

    actions.append(risk_action)
    actions.append(component_action)

    if risk_level == "Critical":
        actions.append(
            "Open a cross-functional response room today, assign an executive owner, "
            "and track actions against daily production exposure."
        )
    elif risk_level == "High":
        actions.append(
            "Assign an accountable owner within 24 hours and monitor inventory, "
            "supplier recovery, and production exposure daily."
        )
    else:
        actions.append(
            "Assign an owner, confirm the next review date, and monitor for a change "
            "in probability or production impact."
        )

    return actions
