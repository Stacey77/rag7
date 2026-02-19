"""Data catalog and metadata store."""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DataAsset:
    asset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    asset_type: str = "dataset"   # dataset | table | model | pipeline | report | api
    description: str = ""
    owner: str = ""
    location: str = ""
    format: str = ""
    schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    quality_score: Optional[float] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None


@dataclass
class ColumnMetadata:
    name: str = ""
    dtype: str = ""
    description: str = ""
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    sample_values: List[Any] = field(default_factory=list)
    statistics: Dict[str, float] = field(default_factory=dict)


@dataclass
class SearchResult:
    total: int = 0
    assets: List[DataAsset] = field(default_factory=list)
    query: Dict[str, Any] = field(default_factory=dict)


class MetadataStore:
    """
    Central data catalog for registering, discovering, and managing metadata
    about data assets across the platform.
    """

    def __init__(self) -> None:
        self._assets: Dict[str, DataAsset] = {}
        self._name_index: Dict[str, str] = {}         # name -> asset_id
        self._tag_index: Dict[str, List[str]] = {}    # tag -> [asset_ids]
        self._type_index: Dict[str, List[str]] = {}   # type -> [asset_ids]
        self._column_metadata: Dict[str, List[ColumnMetadata]] = {}  # asset_id -> columns
        logger.info("MetadataStore initialized")

    def register(self, asset: DataAsset) -> DataAsset:
        self._assets[asset.asset_id] = asset
        self._name_index[asset.name.lower()] = asset.asset_id
        for tag in asset.tags:
            self._tag_index.setdefault(tag, []).append(asset.asset_id)
        self._type_index.setdefault(asset.asset_type, []).append(asset.asset_id)
        logger.debug("Registered asset '%s' (%s)", asset.name, asset.asset_type)
        return asset

    def create(self, name: str, asset_type: str = "dataset",
               description: str = "", owner: str = "",
               location: str = "", tags: Optional[List[str]] = None,
               **kwargs: Any) -> DataAsset:
        asset = DataAsset(name=name, asset_type=asset_type, description=description,
                          owner=owner, location=location, tags=tags or [], **kwargs)
        return self.register(asset)

    def get(self, asset_id: str) -> Optional[DataAsset]:
        return self._assets.get(asset_id)

    def get_by_name(self, name: str) -> Optional[DataAsset]:
        aid = self._name_index.get(name.lower())
        return self._assets.get(aid) if aid else None

    def update(self, asset_id: str, **kwargs: Any) -> bool:
        asset = self._assets.get(asset_id)
        if not asset:
            return False
        for key, value in kwargs.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        asset.updated_at = datetime.utcnow()
        return True

    def delete(self, asset_id: str) -> bool:
        asset = self._assets.pop(asset_id, None)
        if not asset:
            return False
        self._name_index.pop(asset.name.lower(), None)
        for tag in asset.tags:
            self._tag_index.get(tag, []).remove(asset_id)
        self._type_index.get(asset.asset_type, []).remove(asset_id)
        return True

    def add_columns(self, asset_id: str, columns: List[ColumnMetadata]) -> bool:
        if asset_id not in self._assets:
            return False
        self._column_metadata[asset_id] = columns
        return True

    def get_columns(self, asset_id: str) -> List[ColumnMetadata]:
        return self._column_metadata.get(asset_id, [])

    def search(self, query: Optional[str] = None,
               asset_type: Optional[str] = None,
               tags: Optional[List[str]] = None,
               owner: Optional[str] = None,
               limit: int = 50) -> SearchResult:
        results = list(self._assets.values())

        if asset_type:
            results = [a for a in results if a.asset_type == asset_type]
        if owner:
            results = [a for a in results if a.owner == owner]
        if tags:
            results = [a for a in results if any(t in a.tags for t in tags)]
        if query:
            q = query.lower()
            results = [a for a in results
                       if q in a.name.lower() or q in a.description.lower()
                       or any(q in str(v).lower() for v in a.properties.values())]

        return SearchResult(total=len(results), assets=results[:limit],
                            query={"query": query, "type": asset_type, "tags": tags})

    def list_by_type(self, asset_type: str) -> List[DataAsset]:
        ids = self._type_index.get(asset_type, [])
        return [self._assets[aid] for aid in ids if aid in self._assets]

    def list_by_tag(self, tag: str) -> List[DataAsset]:
        ids = self._tag_index.get(tag, [])
        return [self._assets[aid] for aid in ids if aid in self._assets]

    def record_access(self, asset_id: str) -> None:
        asset = self._assets.get(asset_id)
        if asset:
            asset.last_accessed = datetime.utcnow()

    def export_catalog(self) -> Dict[str, Any]:
        return {
            "assets": [
                {
                    "id": a.asset_id, "name": a.name, "type": a.asset_type,
                    "description": a.description, "owner": a.owner,
                    "tags": a.tags, "quality_score": a.quality_score,
                }
                for a in self._assets.values()
            ],
            "total": len(self._assets),
            "exported_at": datetime.utcnow().isoformat(),
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "total_assets": len(self._assets),
            "by_type": {t: len(ids) for t, ids in self._type_index.items()},
            "total_tags": len(self._tag_index),
        }
