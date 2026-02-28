"""Ansible playbook generation and execution adapter."""
from __future__ import annotations
import logging
import uuid
import yaml as _yaml_module
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class AnsibleTask:
    name: str = ""
    module: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    when: Optional[str] = None
    register: Optional[str] = None
    notify: Optional[str] = None
    ignore_errors: bool = False

@dataclass
class AnsiblePlay:
    name: str = ""
    hosts: str = "all"
    become: bool = False
    vars: Dict[str, Any] = field(default_factory=dict)
    tasks: List[AnsibleTask] = field(default_factory=list)
    handlers: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PlaybookResult:
    playbook_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "success"
    hosts_ok: int = 0
    hosts_changed: int = 0
    hosts_failed: int = 0
    tasks_executed: int = 0
    output: str = ""
    executed_at: datetime = field(default_factory=datetime.utcnow)

def _task_to_dict(task: AnsibleTask) -> Dict[str, Any]:
    d: Dict[str, Any] = {"name": task.name, task.module: task.args}
    if task.when:
        d["when"] = task.when
    if task.register:
        d["register"] = task.register
    if task.notify:
        d["notify"] = task.notify
    if task.ignore_errors:
        d["ignore_errors"] = True
    return d

class AnsibleAdapter:
    def __init__(self) -> None:
        self._plays: List[AnsiblePlay] = []
        self._inventory: Dict[str, List[str]] = {"all": ["localhost"]}
        logger.info("AnsibleAdapter initialized")

    def add_play(self, play: AnsiblePlay) -> "AnsibleAdapter":
        self._plays.append(play)
        return self

    def add_host(self, group: str, host: str) -> None:
        self._inventory.setdefault(group, []).append(host)

    def install_packages(self, hosts: str, packages: List[str],
                          state: str = "present") -> "AnsibleAdapter":
        play = AnsiblePlay(name=f"Install packages on {hosts}", hosts=hosts, become=True)
        play.tasks.append(AnsibleTask("Install required packages", "apt",
            {"name": packages, "state": state, "update_cache": True}))
        return self.add_play(play)

    def copy_file(self, hosts: str, src: str, dest: str, mode: str = "0644") -> "AnsibleAdapter":
        play = AnsiblePlay(name=f"Copy {src} to {hosts}", hosts=hosts, become=True)
        play.tasks.append(AnsibleTask(f"Copy {src}", "copy", {"src": src, "dest": dest, "mode": mode}))
        return self.add_play(play)

    def run_command(self, hosts: str, command: str) -> "AnsibleAdapter":
        play = AnsiblePlay(name=f"Run command on {hosts}", hosts=hosts)
        play.tasks.append(AnsibleTask(f"Execute: {command[:40]}", "command", {"cmd": command}))
        return self.add_play(play)

    def deploy_service(self, hosts: str, service_name: str, image: str) -> "AnsibleAdapter":
        play = AnsiblePlay(name=f"Deploy {service_name}", hosts=hosts, become=True,
                           vars={"service_name": service_name, "image": image})
        play.tasks.extend([
            AnsibleTask("Pull Docker image", "community.docker.docker_image",
                {"name": "{{image}}", "source": "pull"}),
            AnsibleTask("Run container", "community.docker.docker_container",
                {"name": "{{service_name}}", "image": "{{image}}", "state": "started"}),
        ])
        return self.add_play(play)

    def generate_playbook(self) -> str:
        playbook = []
        for play in self._plays:
            play_dict: Dict[str, Any] = {
                "name": play.name, "hosts": play.hosts, "become": play.become,
            }
            if play.vars:
                play_dict["vars"] = play.vars
            if play.tasks:
                play_dict["tasks"] = [_task_to_dict(t) for t in play.tasks]
            if play.handlers:
                play_dict["handlers"] = play.handlers
            playbook.append(play_dict)
        try:
            import yaml
            return yaml.dump(playbook, default_flow_style=False, sort_keys=False)
        except ImportError:
            import json
            return json.dumps(playbook, indent=2, default=str)

    def simulate_run(self, hosts: Optional[List[str]] = None) -> PlaybookResult:
        hosts = hosts or self._inventory.get("all", ["localhost"])
        tasks_count = sum(len(p.tasks) for p in self._plays)
        result = PlaybookResult(
            hosts_ok=len(hosts),
            hosts_changed=min(len(hosts), tasks_count),
            tasks_executed=tasks_count * len(hosts),
            output=f"Playbook executed: {len(self._plays)} plays, {tasks_count} tasks on {len(hosts)} hosts",
        )
        logger.info("Ansible simulation: %d plays, %d tasks, %d hosts",
                    len(self._plays), tasks_count, len(hosts))
        return result
