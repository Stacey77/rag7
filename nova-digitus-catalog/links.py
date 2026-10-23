# Public "Try it" addresses. Only apps listed here get a Try it button on the site.
# Add an app's public URL (its exact catalog name as the key), then rebuild.
PUBLIC_URLS = {
    "Engineering Orchestrator": "https://nova-digitus-engineering-orchestrator.ai.studio",
    "Wealth in Health: Sound Healing": "https://brilliant-jelly-467122.netlify.app/",
    "Singular Companion": "https://stacey77.github.io/rag7/nova-digitus-site/try/singular-companion/",
    "Robot Fleet Interface": "https://stacey77.github.io/rag7/nova-digitus-site/try/robot-fleet-interface/",
    "AI Governance & Guardrails Platform": "https://stacey77.github.io/rag7/nova-digitus-site/try/ai-governance-guardrails-platform/",
    "Autonomous Quant Trading Desk": "https://stacey77.github.io/rag7/nova-digitus-site/try/autonomous-quant-trading-desk/",
    # "TerraFleet Autonomous Garden Robotics": "https://example.com/try/terrafleet/",
}

def public_try_url(name):
    return PUBLIC_URLS.get(name)
