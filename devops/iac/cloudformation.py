"""AWS CloudFormation infrastructure adapter."""
from __future__ import annotations
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class CFResource:
    logical_id: str = ""
    resource_type: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    deletion_policy: str = "Delete"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CFTemplate:
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stack_name: str = ""
    description: str = ""
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    resources: Dict[str, CFResource] = field(default_factory=dict)
    outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StackEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    logical_id: str = ""
    status: str = ""
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class StackResult:
    stack_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stack_name: str = ""
    status: str = "CREATE_COMPLETE"
    events: List[StackEvent] = field(default_factory=list)
    outputs: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

class CloudFormation:
    """CloudFormation template builder and deployment simulator."""

    def __init__(self) -> None:
        self._stacks: Dict[str, StackResult] = {}
        logger.info("CloudFormation adapter initialized")

    def template(self, stack_name: str, description: str = "") -> CFTemplate:
        return CFTemplate(stack_name=stack_name, description=description)

    def add_parameter(self, template: CFTemplate, name: str, param_type: str = "String",
                       default: Any = None, description: str = "") -> None:
        p: Dict[str, Any] = {"Type": param_type}
        if default is not None:
            p["Default"] = default
        if description:
            p["Description"] = description
        template.parameters[name] = p

    def add_resource(self, template: CFTemplate, logical_id: str,
                      resource_type: str, properties: Dict[str, Any],
                      depends_on: Optional[List[str]] = None) -> CFResource:
        res = CFResource(logical_id=logical_id, resource_type=resource_type,
                         properties=properties, depends_on=depends_on or [])
        template.resources[logical_id] = res
        return res

    def add_output(self, template: CFTemplate, name: str, value: Any,
                    description: str = "", export_name: Optional[str] = None) -> None:
        out: Dict[str, Any] = {"Value": value}
        if description:
            out["Description"] = description
        if export_name:
            out["Export"] = {"Name": export_name}
        template.outputs[name] = out

    # --- High-level resource helpers ---

    def ec2_instance(self, template: CFTemplate, logical_id: str,
                      instance_type: str = "t3.medium",
                      image_id: str = "ami-0abcdef1234567890") -> CFResource:
        return self.add_resource(template, logical_id, "AWS::EC2::Instance", {
            "InstanceType": instance_type, "ImageId": image_id,
            "Tags": [{"Key": "Name", "Value": logical_id}],
        })

    def s3_bucket(self, template: CFTemplate, logical_id: str,
                   versioning: bool = True) -> CFResource:
        props: Dict[str, Any] = {}
        if versioning:
            props["VersioningConfiguration"] = {"Status": "Enabled"}
        return self.add_resource(template, logical_id, "AWS::S3::Bucket", props)

    def rds_instance(self, template: CFTemplate, logical_id: str,
                      engine: str = "postgres", db_class: str = "db.t3.micro") -> CFResource:
        return self.add_resource(template, logical_id, "AWS::RDS::DBInstance", {
            "DBInstanceClass": db_class, "Engine": engine,
            "AllocatedStorage": "20", "MasterUsername": "admin",
            "MasterUserPassword": {"Ref": "DBPassword"},
        })

    def lambda_function(self, template: CFTemplate, logical_id: str,
                         handler: str, runtime: str = "python3.11",
                         memory_mb: int = 256, timeout: int = 30) -> CFResource:
        return self.add_resource(template, logical_id, "AWS::Lambda::Function", {
            "Handler": handler, "Runtime": runtime,
            "MemorySize": memory_mb, "Timeout": timeout,
            "Role": {"Fn::GetAtt": ["LambdaRole", "Arn"]},
            "Code": {"ZipFile": "def handler(event, context): return {}"},
        })

    def render_json(self, template: CFTemplate) -> str:
        doc: Dict[str, Any] = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": template.description,
        }
        if template.parameters:
            doc["Parameters"] = template.parameters
        if template.conditions:
            doc["Conditions"] = template.conditions
        doc["Resources"] = {}
        for lid, res in template.resources.items():
            r: Dict[str, Any] = {"Type": res.resource_type, "Properties": res.properties}
            if res.depends_on:
                r["DependsOn"] = res.depends_on
            if res.deletion_policy != "Delete":
                r["DeletionPolicy"] = res.deletion_policy
            doc["Resources"][lid] = r
        if template.outputs:
            doc["Outputs"] = template.outputs
        return json.dumps(doc, indent=2, default=str)

    def deploy(self, template: CFTemplate) -> StackResult:
        events = [
            StackEvent(logical_id=template.stack_name, status="CREATE_IN_PROGRESS"),
            *[StackEvent(logical_id=lid, status="CREATE_COMPLETE")
              for lid in template.resources],
            StackEvent(logical_id=template.stack_name, status="CREATE_COMPLETE"),
        ]
        outputs = {
            name: str(out.get("Value", "")) for name, out in template.outputs.items()
        }
        result = StackResult(stack_name=template.stack_name,
                             events=events, outputs=outputs)
        self._stacks[template.stack_name] = result
        logger.info("Stack '%s' deployed: %d resources", template.stack_name, len(template.resources))
        return result

    def describe_stack(self, stack_name: str) -> Optional[StackResult]:
        return self._stacks.get(stack_name)

    def delete_stack(self, stack_name: str) -> bool:
        return bool(self._stacks.pop(stack_name, None))
