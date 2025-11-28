"""
Flow management client for Ragamuffin SDK.
"""

from typing import TYPE_CHECKING, Union, Optional
from pathlib import Path
import json

if TYPE_CHECKING:
    from .client import RagamuffinClient


class FlowsClient:
    """
    Flow management operations for Ragamuffin API.
    
    Example:
        >>> # List flows
        >>> flows = client.flows.list()
        
        >>> # Save a flow
        >>> client.flows.save("my_flow", {"nodes": [], "edges": []})
        
        >>> # Run a flow
        >>> result = client.flows.run("my_flow", "Hello!")
    """

    def __init__(self, client: "RagamuffinClient"):
        self._client = client

    def list(self) -> dict:
        """
        List all saved flows.
        
        Returns:
            List of flow names and metadata
        """
        return self._client.request("GET", "/list_flows/")

    def get(self, name: str) -> dict:
        """
        Get a flow by name.
        
        Args:
            name: Flow name
        
        Returns:
            Flow content as dictionary
        """
        return self._client.request("GET", f"/get_flow/{name}")

    def save(
        self,
        name: str,
        content: Union[dict, str, Path],
    ) -> dict:
        """
        Save a flow.
        
        Args:
            name: Flow name
            content: Flow content as dict, JSON string, or file path
        
        Returns:
            Save confirmation
        """
        # Handle different content types
        if isinstance(content, Path):
            with open(content, "rb") as f:
                files = {"flow_file": (f"{name}.json", f, "application/json")}
                return self._client.request("POST", "/save_flow/", files=files)
        elif isinstance(content, str):
            if content.endswith(".json") and Path(content).exists():
                with open(content, "rb") as f:
                    files = {"flow_file": (f"{name}.json", f, "application/json")}
                    return self._client.request("POST", "/save_flow/", files=files)
            else:
                # Assume it's a JSON string
                flow_bytes = content.encode()
        else:
            # Dictionary
            flow_bytes = json.dumps(content).encode()
        
        files = {"flow_file": (f"{name}.json", flow_bytes, "application/json")}
        return self._client.request("POST", "/save_flow/", files=files)

    def run(
        self,
        flow: Union[str, dict, Path],
        user_input: str,
        tweaks: Optional[dict] = None,
    ) -> dict:
        """
        Execute a flow with user input.
        
        Args:
            flow: Flow name, content dict, or file path
            user_input: Input to pass to the flow
            tweaks: Optional flow parameter tweaks
        
        Returns:
            Flow execution result
        """
        data = {"user_input": user_input}
        if tweaks:
            data["tweaks"] = json.dumps(tweaks)
        
        # Handle different flow types
        if isinstance(flow, str) and not flow.endswith(".json"):
            # It's a flow name
            data["flow_name"] = flow
            return self._client.request("POST", "/run_flow/", data=data)
        elif isinstance(flow, Path):
            with open(flow, "rb") as f:
                files = {"flow_file": ("flow.json", f, "application/json")}
                return self._client.request("POST", "/run_flow/", files=files, data=data)
        elif isinstance(flow, str) and flow.endswith(".json"):
            with open(flow, "rb") as f:
                files = {"flow_file": ("flow.json", f, "application/json")}
                return self._client.request("POST", "/run_flow/", files=files, data=data)
        else:
            # Dictionary content
            flow_bytes = json.dumps(flow).encode()
            files = {"flow_file": ("flow.json", flow_bytes, "application/json")}
            return self._client.request("POST", "/run_flow/", files=files, data=data)

    def delete(self, name: str) -> dict:
        """
        Delete a flow.
        
        Args:
            name: Flow name to delete
        
        Returns:
            Deletion confirmation
        """
        return self._client.request("DELETE", f"/delete_flow/{name}")

    def export(self, name: str, path: Union[str, Path]) -> None:
        """
        Export a flow to a file.
        
        Args:
            name: Flow name
            path: Destination file path
        """
        flow = self.get(name)
        with open(path, "w") as f:
            json.dump(flow, f, indent=2)

    def import_flow(self, path: Union[str, Path], name: Optional[str] = None) -> dict:
        """
        Import a flow from a file.
        
        Args:
            path: Source file path
            name: Optional flow name (defaults to filename)
        
        Returns:
            Import confirmation
        """
        path = Path(path)
        if name is None:
            name = path.stem
        
        return self.save(name, path)
