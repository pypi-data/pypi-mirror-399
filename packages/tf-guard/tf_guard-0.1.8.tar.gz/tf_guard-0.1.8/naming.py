# naming.py

def check_resource_group_naming(changes):
    """
    Enforces CAF naming for Azure Resource Groups.
    Required abbreviation: 'rg'
    """
    findings = []

    for change in changes:
        if change["type"] != "azurerm_resource_group":
            continue

        name = (
            change.get("change", {})
            .get("after", {})
            .get("name")
        )

        if not name:
            continue

        if not name.lower().startswith("rg-"):
            findings.append({
                "resource": change["address"],
                "name": name,
                "issue": "Resource Group name does not start with required 'rg-' prefix",
                "severity": "MEDIUM"
            })

    return findings
