"""Terraform infrastructure-as-code integration."""
from __future__ import annotations
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class TerraformResource:
    resource_type: str = ""
    resource_name: str = ""
    provider: str = "aws"
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)

@dataclass
class TerraformPlan:
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resources_to_add: List[TerraformResource] = field(default_factory=list)
    resources_to_change: List[TerraformResource] = field(default_factory=list)
    resources_to_destroy: List[TerraformResource] = field(default_factory=list)
    estimated_cost: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TerraformApplyResult:
    apply_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "success"
    resources_added: int = 0
    resources_changed: int = 0
    resources_destroyed: int = 0
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    applied_at: datetime = field(default_factory=datetime.utcnow)

def _hcl_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(f'"{x}"' if isinstance(x, str) else str(x) for x in v) + "]"
    if isinstance(v, dict):
        inner = "\n    ".join(f'{k} = {_hcl_value(val)}' for k, val in v.items())
        return "{\n    " + inner + "\n  }"
    return f'"{v}"'

class TerraformAdapter:
    def __init__(self) -> None:
        self._resources: List[TerraformResource] = []
        self._state: Dict[str, Any] = {}
        self._outputs: Dict[str, str] = {}
        logger.info("TerraformAdapter initialized")

    def add_resource(self, resource: TerraformResource) -> "TerraformAdapter":
        self._resources.append(resource)
        return self

    def aws_instance(self, name: str, instance_type: str = "t3.medium",
                      ami: str = "ami-0abcdef1234567890", **kwargs: Any) -> "TerraformAdapter":
        return self.add_resource(TerraformResource("aws_instance", name, "aws",
            {"instance_type": instance_type, "ami": ami, **kwargs}))

    def aws_s3_bucket(self, name: str, bucket_name: str, **kwargs: Any) -> "TerraformAdapter":
        return self.add_resource(TerraformResource("aws_s3_bucket", name, "aws",
            {"bucket": bucket_name, "acl": "private", **kwargs}))

    def aws_rds_instance(self, name: str, engine: str = "postgres",
                          instance_class: str = "db.t3.micro", **kwargs: Any) -> "TerraformAdapter":
        return self.add_resource(TerraformResource("aws_db_instance", name, "aws",
            {"engine": engine, "instance_class": instance_class, "allocated_storage": 20, **kwargs}))

    def generate_hcl(self) -> str:
        lines = ['terraform {\n  required_providers {\n    aws = { source = "hashicorp/aws" }\n  }\n}\n']
        for res in self._resources:
            lines.append(f'resource "{res.resource_type}" "{res.resource_name}" {{')
            for k, v in res.config.items():
                lines.append(f"  {k} = {_hcl_value(v)}")
            if res.depends_on:
                lines.append(f"  depends_on = [{', '.join(res.depends_on)}]")
            lines.append("}\n")
        for name, expr in self._outputs.items():
            lines.append(f'output "{name}" {{\n  value = {expr}\n}}\n')
        return "\n".join(lines)

    def add_output(self, name: str, value_expr: str) -> "TerraformAdapter":
        self._outputs[name] = value_expr
        return self

    def plan(self) -> TerraformPlan:
        to_add = [r for r in self._resources if r.resource_name not in self._state]
        to_change = [r for r in self._resources if r.resource_name in self._state]
        plan = TerraformPlan(resources_to_add=to_add, resources_to_change=to_change)
        logger.info("Terraform plan: +%d ~%d", len(to_add), len(to_change))
        return plan

    def apply(self, plan: Optional[TerraformPlan] = None) -> TerraformApplyResult:
        if plan is None:
            plan = self.plan()
        for res in plan.resources_to_add:
            self._state[res.resource_name] = {"type": res.resource_type, "config": res.config}
        result = TerraformApplyResult(
            resources_added=len(plan.resources_to_add),
            resources_changed=len(plan.resources_to_change),
            resources_destroyed=len(plan.resources_to_destroy),
            outputs={name: f"[computed:{expr}]" for name, expr in self._outputs.items()},
        )
        logger.info("Terraform apply: +%d ~%d", result.resources_added, result.resources_changed)
        return result

    def destroy(self, resource_name: str) -> bool:
        if resource_name in self._state:
            del self._state[resource_name]
            return True
        return False

    @property
    def state_resources(self) -> List[str]:
        return list(self._state.keys())
