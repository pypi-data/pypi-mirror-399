from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from .entities import Edge, Entity


@dataclass(slots=True)
class WorkbookGraph:
    """In-memory normalized graph of workbook artifacts.

    - Nodes are de-duped by (kind, key).
    - Edges are free-form but should use stable 'kind' values.
    """

    nodes: dict[str, Entity] = field(default_factory=dict)  # id -> entity
    edges: list[Edge] = field(default_factory=list)

    # (kind, key) -> id
    _index: dict[tuple[str, str], str] = field(default_factory=dict)

    # ---------- Node ops ----------
    def upsert(self, entity: Entity) -> Entity:
        """Insert entity if (kind, key) not present; otherwise return existing.

        If same (kind, key) exists but with different id, keeps the original id.
        """

        idx_key = (entity.kind, entity.key)
        existing_id = self._index.get(idx_key)
        if existing_id:
            return self.nodes[existing_id]

        self._index[idx_key] = entity.id
        self.nodes[entity.id] = entity
        return entity

    def get(self, entity_id: str) -> Entity | None:
        return self.nodes.get(entity_id)

    def get_by_key(self, kind: str, key: str) -> Entity | None:
        entity_id = self._index.get((kind, key))
        return self.nodes.get(entity_id) if entity_id else None

    def get_or_create(self, kind: str, key: str, factory: Callable[[], Entity]) -> Entity:
        existing = self.get_by_key(kind, key)
        if existing:
            return existing
        return self.upsert(factory())

    # ---------- Edge ops ----------
    def add_edge(self, src: str, dst: str, kind: str, **attrs: Any) -> Edge:
        if src not in self.nodes:
            raise KeyError(f"edge src node not found: {src}")
        if dst not in self.nodes:
            raise KeyError(f"edge dst node not found: {dst}")
        e = Edge(src=src, dst=dst, kind=kind, attrs=dict(attrs))
        self.edges.append(e)
        return e

    def add_edges(self, edges: Iterable[Edge]) -> None:
        for e in edges:
            if e.src not in self.nodes:
                raise KeyError(f"edge src node not found: {e.src}")
            if e.dst not in self.nodes:
                raise KeyError(f"edge dst node not found: {e.dst}")
            self.edges.append(e)

    def __len__(self) -> int:
        return len(self.nodes)

    def __contains__(self, entity_id: str) -> bool:
        return entity_id in self.nodes

    def _sorted_nodes(self) -> list[Entity]:
        # Stable output for JSON serialization and diffs.
        return sorted(self.nodes.values(), key=lambda n: (n.kind, n.key, n.id))

    def _sorted_edges(self) -> list[Edge]:
        return sorted(self.edges, key=lambda e: (e.kind, e.src, e.dst))

    # ---------- Serialization ----------
    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self._sorted_nodes()],
            "edges": [e.to_dict() for e in self._sorted_edges()],
            "stats": self.stats(),
        }

    # ---------- Convenience ----------
    def stats(self) -> dict[str, int]:
        by_kind: dict[str, int] = {}
        for n in self.nodes.values():
            by_kind[n.kind] = by_kind.get(n.kind, 0) + 1
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            **{f"nodes_{k}": v for k, v in by_kind.items()},
        }
