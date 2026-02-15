"""
Compliance Markers
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ComplianceMarkers:
    """Manages compliance markers for resources"""
    
    def __init__(self):
        self.logger = logging.getLogger("compliance_markers")
        self.markers: Dict[str, List[str]] = {}
    
    def add_marker(
        self,
        resource_id: str,
        marker: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add compliance marker to resource"""
        
        if resource_id not in self.markers:
            self.markers[resource_id] = []
        
        marker_entry = {
            "marker": marker,
            "metadata": metadata or {}
        }
        
        self.markers[resource_id].append(marker_entry)
        
        self.logger.info(f"Added marker '{marker}' to {resource_id}")
    
    def remove_marker(
        self,
        resource_id: str,
        marker: str
    ):
        """Remove compliance marker from resource"""
        
        if resource_id in self.markers:
            self.markers[resource_id] = [
                m for m in self.markers[resource_id]
                if m.get("marker") != marker
            ]
            
            self.logger.info(f"Removed marker '{marker}' from {resource_id}")
    
    def get_markers(
        self,
        resource_id: str
    ) -> List[Dict[str, Any]]:
        """Get all markers for a resource"""
        
        return self.markers.get(resource_id, [])
    
    def has_marker(
        self,
        resource_id: str,
        marker: str
    ) -> bool:
        """Check if resource has specific marker"""
        
        resource_markers = self.markers.get(resource_id, [])
        return any(m.get("marker") == marker for m in resource_markers)
    
    def get_resources_with_marker(
        self,
        marker: str
    ) -> List[str]:
        """Get all resources with specific marker"""
        
        return [
            resource_id
            for resource_id, markers in self.markers.items()
            if any(m.get("marker") == marker for m in markers)
        ]
    
    def validate_markers(
        self,
        resource_id: str,
        required_markers: List[str]
    ) -> Dict[str, Any]:
        """Validate that resource has required markers"""
        
        resource_markers = [
            m.get("marker")
            for m in self.markers.get(resource_id, [])
        ]
        
        missing_markers = [
            marker for marker in required_markers
            if marker not in resource_markers
        ]
        
        return {
            "valid": len(missing_markers) == 0,
            "missing_markers": missing_markers,
            "resource_id": resource_id
        }
