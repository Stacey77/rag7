# Compliance Policy
package compliance.check

# SOC2 Compliance
soc2_compliant {
    input.resource.encrypted == true
    input.resource.tls_enabled == true
    input.resource.audit_enabled == true
}

# HIPAA Compliance
hipaa_compliant {
    input.resource.encrypted == true
    input.resource.access_policy
    input.resource.audit_enabled == true
}

# GDPR Compliance
gdpr_compliant {
    input.resource.data_privacy == true
    input.resource.consent_tracking == true
}

# Overall compliance
compliant {
    all_required_frameworks_compliant
}

all_required_frameworks_compliant {
    every framework in input.rules {
        framework_compliant(framework)
    }
}

framework_compliant("SOC2") { soc2_compliant }
framework_compliant("HIPAA") { hipaa_compliant }
framework_compliant("GDPR") { gdpr_compliant }
framework_compliant(framework) { 
    not framework in ["SOC2", "HIPAA", "GDPR"]
}
