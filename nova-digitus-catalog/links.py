# Public "Try it" addresses. Only apps listed here get a Try it button on the site.
# Add an app's public URL (its exact catalog name as the key), then rebuild.
PUBLIC_URLS = {
    "Engineering Orchestrator": "https://nova-digitus-engineering-orchestrator.ai.studio",
    # "TerraFleet Autonomous Garden Robotics": "https://example.com/try/terrafleet/",
}

def public_try_url(name):
    return PUBLIC_URLS.get(name)
