import json

def parse_tf_plan(json_input):
    plan = json.loads(json_input)
    changes = []
    for rc in plan.get("resource_changes", []):
        action = rc.get("change", {}).get("actions", [])
        if "no-op" in action or not action:
            continue
        changes.append({
            "address": rc["address"],
            "type": rc["type"],
            "actions": action,
            "change_summary": {
                "before": rc["change"].get("before"),
                "after": rc["change"].get("after")
            }
        })
    return changes