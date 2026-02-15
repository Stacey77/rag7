# Default Deployment Policy
package deployment.validate

default allow = false

# Allow deployment with proper approvals
allow {
    input.approver
    input.environment
    valid_environment(input.environment)
}

# Validate environment
valid_environment(env) {
    env == "development"
}

valid_environment(env) {
    env == "staging"
}

valid_environment(env) {
    env == "production"
    input.approved_by_manager
}

# Violations tracking
violations[msg] {
    not input.approver
    msg := "Deployment requires an approver"
}

violations[msg] {
    not valid_environment(input.environment)
    msg := sprintf("Invalid environment: %v", [input.environment])
}

violations[msg] {
    input.environment == "production"
    not input.approved_by_manager
    msg := "Production deployments require manager approval"
}
