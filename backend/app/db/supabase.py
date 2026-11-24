import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

IN_MEMORY_DB: Dict[str, List[Dict[str, Any]]] = {
    "health_profiles": [],
    "food_diary": [],
    "symptom_assessments": [],
    "blood_test_results": [],
    "prediction_history": []
}

class InMemoryResponse:
    def __init__(self, data: Any):
        self.data = data

class ResilientQueryBuilder:
    def __init__(self, real_builder, table_name: str):
        self.real_builder = real_builder
        self.table_name = table_name
        self.filters = []
        self.order_by = None
        self.action = 'select'
        self.action_data = None

    def select(self, columns="*"):
        self.action = 'select'
        if self.real_builder:
            try:
                self.real_builder = self.real_builder.select(columns)
            except Exception:
                pass
        return self

    def eq(self, column: str, value: Any):
        self.filters.append(('eq', column, value))
        if self.real_builder:
            try:
                self.real_builder = self.real_builder.eq(column, value)
            except Exception:
                pass
        return self

    def gte(self, column: str, value: Any):
        self.filters.append(('gte', column, value))
        if self.real_builder:
            try:
                self.real_builder = self.real_builder.gte(column, value)
            except Exception:
                pass
        return self

    def order(self, column: str, desc: bool = False):
        self.order_by = (column, desc)
        if self.real_builder:
            try:
                self.real_builder = self.real_builder.order(column, desc=desc)
            except Exception:
                pass
        return self

    def insert(self, json: Any):
        self.action = 'insert'
        self.action_data = json
        if self.real_builder:
            try:
                self.real_builder = self.real_builder.insert(json)
            except Exception:
                pass
        return self

    def update(self, json: Any):
        self.action = 'update'
        self.action_data = json
        if self.real_builder:
            try:
                self.real_builder = self.real_builder.update(json)
            except Exception:
                pass
        return self

    def delete(self):
        self.action = 'delete'
        if self.real_builder:
            try:
                self.real_builder = self.real_builder.delete()
            except Exception:
                pass
        return self

    def execute(self):
        if self.real_builder:
            try:
                return self.real_builder.execute()
            except Exception as exc:
                logger.warning("Supabase query failed (%s). Using in-memory fallback for '%s'.", str(exc), self.table_name)
        return self._execute_in_memory()

    def _execute_in_memory(self):
        if self.table_name not in IN_MEMORY_DB:
            IN_MEMORY_DB[self.table_name] = []

        table = IN_MEMORY_DB[self.table_name]

        if self.action == 'insert':
            items = self.action_data if isinstance(self.action_data, list) else [self.action_data]
            inserted = []
            for item in items:
                record = dict(item)
                now_iso = datetime.now(timezone.utc).isoformat()
                if "id" not in record or not record["id"]:
                    record["id"] = str(uuid.uuid4())
                if "created_at" not in record:
                    record["created_at"] = now_iso
                if "updated_at" not in record:
                    record["updated_at"] = now_iso
                table.append(record)
                inserted.append(record)
            return InMemoryResponse(inserted)

        matched_indices = []
        for idx, item in enumerate(table):
            match = True
            for op, col, val in self.filters:
                item_val = item.get(col)
                if op == 'eq':
                    if str(item_val) != str(val):
                        match = False
                        break
                elif op == 'gte':
                    if item_val is None or str(item_val) < str(val):
                        match = False
                        break
            if match:
                matched_indices.append(idx)

        if self.action == 'delete':
            deleted = [table[idx] for idx in matched_indices]
            for idx in reversed(matched_indices):
                table.pop(idx)
            return InMemoryResponse(deleted)

        if self.action == 'update':
            updated = []
            update_payload = dict(self.action_data) if isinstance(self.action_data, dict) else {}
            update_payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            for idx in matched_indices:
                table[idx].update(update_payload)
                updated.append(table[idx])
            return InMemoryResponse(updated)

        # Action == 'select'
        results = [dict(table[idx]) for idx in matched_indices]

        if self.order_by:
            col, desc = self.order_by
            results.sort(key=lambda x: str(x.get(col, '')), reverse=desc)

        return InMemoryResponse(results)


class ResilientSupabaseClient:
    def __init__(self, real_client: Optional[Client]):
        self.real_client = real_client

    def table(self, name: str):
        real_builder = None
        if self.real_client:
            try:
                real_builder = self.real_client.table(name)
            except Exception:
                real_builder = None
        return ResilientQueryBuilder(real_builder, name)


def get_supabase_admin_client() -> ResilientSupabaseClient:
    """
    Returns a ResilientSupabaseClient with automatic in-memory fallback on database failure.
    """
    try:
        real_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    except Exception:
        real_client = None
    return ResilientSupabaseClient(real_client)


def get_supabase_client() -> ResilientSupabaseClient:
    """
    Returns a standard ResilientSupabaseClient with anon key and in-memory fallback.
    """
    try:
        real_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    except Exception:
        real_client = None
    return ResilientSupabaseClient(real_client)

