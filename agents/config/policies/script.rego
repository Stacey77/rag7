# Script Validation Policy
package script.validate

default allow = true

# Block dangerous commands
deny[msg] {
    contains(input.script, "rm -rf /")
    msg := "Dangerous command detected: rm -rf /"
}

deny[msg] {
    contains(input.script, "dd if=/dev/zero")
    msg := "Dangerous command detected: dd if=/dev/zero"
}

deny[msg] {
    contains(input.script, "mkfs")
    msg := "Dangerous command detected: mkfs"
}

# Require error handling
violations[msg] {
    not contains(input.script, "set -e")
    msg := "Script should include error handling (set -e)"
}

# Check for production safety
violations[msg] {
    input.context.environment == "production"
    not contains(input.script, "backup")
    contains(input.script, "delete")
    msg := "Production deletions should include backup"
}

allow {
    count(deny) == 0
}
