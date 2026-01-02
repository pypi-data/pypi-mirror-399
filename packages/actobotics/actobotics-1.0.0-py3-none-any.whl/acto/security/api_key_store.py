from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import String, Integer, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from acto.errors import AccessError
from acto.registry.models import Base
from acto.registry.user_models import User
from acto.registry.db import make_engine, make_session_factory
from acto.config.settings import Settings


class ApiKeyGroup(Base):
    """Database model for API key groups."""

    __tablename__ = "api_key_groups"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class ApiKeyRecord(Base):
    """Database model for API keys."""

    __tablename__ = "api_keys"

    key_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    key_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    last_used_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    created_by: Mapped[str | None] = mapped_column(String(256), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    # Usage statistics
    request_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    endpoint_usage: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string with endpoint -> count mapping
    # Group and ordering
    group_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


def generate_api_key(prefix: str = "acto") -> str:
    """Generate a new API key."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def hash_api_key(key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


class ApiKeyStore:
    """Database-backed API key store."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = make_engine(settings)
        self.Session = make_session_factory(self.engine)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Ensure database tables exist and migrate schema if needed."""
        Base.metadata.create_all(self.engine)
        
        # Migration: Add user_id column if it doesn't exist
        try:
            with self.engine.begin() as conn:
                # First check if table exists
                table_exists = False
                if self.engine.url.drivername == "postgresql":
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_name='api_keys'
                    """))
                    table_exists = result.fetchone() is not None
                elif self.engine.url.drivername.startswith("sqlite"):
                    result = conn.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='api_keys'
                    """))
                    table_exists = result.fetchone() is not None
                else:
                    # For other databases, try to query the table
                    try:
                        conn.execute(text("SELECT 1 FROM api_keys LIMIT 1"))
                        table_exists = True
                    except Exception:
                        table_exists = False
                
                if not table_exists:
                    # Table doesn't exist, create_all should have created it
                    return
                
                # Check if user_id column exists
                column_exists = False
                if self.engine.url.drivername == "postgresql":
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='api_keys' AND column_name='user_id'
                    """))
                    column_exists = result.fetchone() is not None
                elif self.engine.url.drivername.startswith("sqlite"):
                    result = conn.execute(text("PRAGMA table_info(api_keys)"))
                    columns = [row[1] for row in result.fetchall()]
                    column_exists = "user_id" in columns
                else:
                    # For other databases, try to query the column
                    try:
                        conn.execute(text("SELECT user_id FROM api_keys LIMIT 1"))
                        column_exists = True
                    except Exception:
                        column_exists = False
                
                if not column_exists:
                    # Add user_id column
                    if self.engine.url.drivername == "postgresql":
                        conn.execute(text("ALTER TABLE api_keys ADD COLUMN user_id VARCHAR(64)"))
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_api_keys_user_id ON api_keys(user_id)"))
                    elif self.engine.url.drivername.startswith("sqlite"):
                        # SQLite supports ALTER TABLE ADD COLUMN since version 3.1.11
                        conn.execute(text("ALTER TABLE api_keys ADD COLUMN user_id VARCHAR(64)"))
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_api_keys_user_id ON api_keys(user_id)"))
                    else:
                        # For other databases, try ALTER TABLE
                        conn.execute(text("ALTER TABLE api_keys ADD COLUMN user_id VARCHAR(64)"))
                
                # Check if group_id and sort_order columns exist
                group_columns = ["group_id", "sort_order"]
                for col_name in group_columns:
                    col_exists = False
                    if self.engine.url.drivername == "postgresql":
                        result = conn.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='api_keys' AND column_name='{col_name}'
                        """))
                        col_exists = result.fetchone() is not None
                    elif self.engine.url.drivername.startswith("sqlite"):
                        result = conn.execute(text("PRAGMA table_info(api_keys)"))
                        columns = [row[1] for row in result.fetchall()]
                        col_exists = col_name in columns
                    else:
                        try:
                            conn.execute(text(f"SELECT {col_name} FROM api_keys LIMIT 1"))
                            col_exists = True
                        except Exception:
                            col_exists = False
                    
                    if not col_exists:
                        if col_name == "group_id":
                            conn.execute(text("ALTER TABLE api_keys ADD COLUMN group_id VARCHAR(64)"))
                            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_api_keys_group_id ON api_keys(group_id)"))
                        elif col_name == "sort_order":
                            conn.execute(text("ALTER TABLE api_keys ADD COLUMN sort_order INTEGER DEFAULT 0"))
                
                # Check if request_count column exists
                stats_columns = ["request_count", "endpoint_usage"]
                for col_name in stats_columns:
                    col_exists = False
                    if self.engine.url.drivername == "postgresql":
                        result = conn.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='api_keys' AND column_name='{col_name}'
                        """))
                        col_exists = result.fetchone() is not None
                    elif self.engine.url.drivername.startswith("sqlite"):
                        result = conn.execute(text("PRAGMA table_info(api_keys)"))
                        columns = [row[1] for row in result.fetchall()]
                        col_exists = col_name in columns
                    else:
                        try:
                            conn.execute(text(f"SELECT {col_name} FROM api_keys LIMIT 1"))
                            col_exists = True
                        except Exception:
                            col_exists = False
                    
                    if not col_exists:
                        if col_name == "request_count":
                            if self.engine.url.drivername == "postgresql":
                                conn.execute(text("ALTER TABLE api_keys ADD COLUMN request_count INTEGER DEFAULT 0"))
                                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_api_keys_request_count ON api_keys(request_count)"))
                            elif self.engine.url.drivername.startswith("sqlite"):
                                conn.execute(text("ALTER TABLE api_keys ADD COLUMN request_count INTEGER DEFAULT 0"))
                                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_api_keys_request_count ON api_keys(request_count)"))
                            else:
                                conn.execute(text("ALTER TABLE api_keys ADD COLUMN request_count INTEGER DEFAULT 0"))
                        elif col_name == "endpoint_usage":
                            if self.engine.url.drivername == "postgresql":
                                conn.execute(text("ALTER TABLE api_keys ADD COLUMN endpoint_usage TEXT"))
                            elif self.engine.url.drivername.startswith("sqlite"):
                                conn.execute(text("ALTER TABLE api_keys ADD COLUMN endpoint_usage TEXT"))
                            else:
                                conn.execute(text("ALTER TABLE api_keys ADD COLUMN endpoint_usage TEXT"))
        except Exception as e:
            # If migration fails, log but don't crash - table might already have the column
            # or the database might not support the operation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not migrate api_keys table: {e}")

    def create_key(self, name: str, user_id: str | None = None, created_by: str | None = None) -> dict[str, Any]:
        """Create a new API key and return both the key and its metadata."""
        key = generate_api_key()
        key_hash = hash_api_key(key)
        key_id = secrets.token_urlsafe(16)

        now = datetime.now(timezone.utc).isoformat()

        record = ApiKeyRecord(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            created_at=now,
            last_used_at=None,
            is_active=True,
            created_by=created_by,
            user_id=user_id,
            request_count=0,
            endpoint_usage=None,
        )

        with self.Session() as session:
            session.add(record)
            session.commit()

        return {
            "key_id": key_id,
            "key": key,  # Only returned once!
            "name": name,
            "created_at": now,
            "created_by": created_by,
            "user_id": user_id,
        }

    def is_valid(self, key: str) -> bool:
        """Check if an API key is valid and active."""
        key_hash = hash_api_key(key)
        with self.Session() as session:
            record = session.query(ApiKeyRecord).filter(
                ApiKeyRecord.key_hash == key_hash,
                ApiKeyRecord.is_active == True,  # noqa: E712
            ).first()
            if record:
                # Update last_used_at
                record.last_used_at = datetime.now(timezone.utc).isoformat()
                session.commit()
                return True
        return False
    
    def record_usage(self, key: str, endpoint: str) -> None:
        """Record API key usage for statistics."""
        key_hash = hash_api_key(key)
        with self.Session() as session:
            record = session.query(ApiKeyRecord).filter(
                ApiKeyRecord.key_hash == key_hash,
                ApiKeyRecord.is_active == True,  # noqa: E712
            ).first()
            if record:
                # Update request count
                record.request_count = (record.request_count or 0) + 1
                record.last_used_at = datetime.now(timezone.utc).isoformat()
                
                # Update endpoint usage statistics
                endpoint_usage = {}
                if record.endpoint_usage:
                    try:
                        endpoint_usage = json.loads(record.endpoint_usage)
                    except (json.JSONDecodeError, TypeError):
                        endpoint_usage = {}
                
                endpoint_usage[endpoint] = endpoint_usage.get(endpoint, 0) + 1
                record.endpoint_usage = json.dumps(endpoint_usage)
                
                session.commit()

    def require(self, key: str | None) -> dict[str, Any]:
        """
        Require a valid API key, raise AccessError if invalid.
        
        Returns:
            dict: API key data including user_id, key_id, name, etc.
        """
        if not key:
            raise AccessError("Invalid or missing API key. Please provide a valid Bearer token.")
        
        key_hash = hash_api_key(key)
        with self.Session() as session:
            record = session.query(ApiKeyRecord).filter(
                ApiKeyRecord.key_hash == key_hash,
                ApiKeyRecord.is_active == True,  # noqa: E712
            ).first()
            
            if not record:
                raise AccessError("Invalid or missing API key. Please provide a valid Bearer token.")
            
            return {
                "key_id": record.key_id,
                "name": record.name,
                "user_id": record.user_id,
                "created_by": record.created_by,
                "is_active": record.is_active,
            }

    def list_keys(self, user_id: str | None = None, include_inactive: bool = False) -> list[dict[str, Any]]:
        """List API keys (without the actual key values). Filter by user_id if provided."""
        with self.Session() as session:
            query = session.query(ApiKeyRecord)
            if user_id:
                query = query.filter(ApiKeyRecord.user_id == user_id)
            if not include_inactive:
                query = query.filter(ApiKeyRecord.is_active == True)  # noqa: E712
            records = query.order_by(ApiKeyRecord.sort_order, ApiKeyRecord.created_at.desc()).all()

            # Build group name lookup
            group_names = {}
            if user_id:
                groups = session.query(ApiKeyGroup).filter(
                    ApiKeyGroup.user_id == user_id
                ).all()
                group_names = {g.id: g.name for g in groups}

            return [
                {
                    "key_id": record.key_id,
                    "name": record.name,
                    "created_at": record.created_at,
                    "last_used_at": record.last_used_at,
                    "is_active": record.is_active,
                    "created_by": record.created_by,
                    "user_id": record.user_id,
                    "request_count": record.request_count or 0,
                    "endpoint_usage": json.loads(record.endpoint_usage) if record.endpoint_usage else {},
                    "group_id": getattr(record, 'group_id', None),
                    "group_name": group_names.get(getattr(record, 'group_id', None) or ''),
                    "sort_order": getattr(record, 'sort_order', 0) or 0,
                }
                for record in records
            ]

    def get_key(self, key_id: str, user_id: str | None = None) -> dict[str, Any] | None:
        """Get API key metadata by ID. Optionally filter by user_id."""
        with self.Session() as session:
            query = session.query(ApiKeyRecord).filter(ApiKeyRecord.key_id == key_id)
            if user_id:
                query = query.filter(ApiKeyRecord.user_id == user_id)
            record = query.first()
            if record:
                return {
                    "key_id": record.key_id,
                    "name": record.name,
                    "created_at": record.created_at,
                    "last_used_at": record.last_used_at,
                    "is_active": record.is_active,
                    "created_by": record.created_by,
                    "user_id": record.user_id,
                    "request_count": record.request_count or 0,
                    "endpoint_usage": json.loads(record.endpoint_usage) if record.endpoint_usage else {},
                }
        return None
    
    def delete_key(self, key_id: str, user_id: str | None = None) -> bool:
        """Permanently delete an API key from the database. Optionally filter by user_id."""
        with self.Session() as session:
            query = session.query(ApiKeyRecord).filter(ApiKeyRecord.key_id == key_id)
            if user_id:
                query = query.filter(ApiKeyRecord.user_id == user_id)
            record = query.first()
            if record:
                session.delete(record)
                session.commit()
                return True
        return False

    def update_key(self, key_id: str, name: str | None = None, user_id: str | None = None) -> dict[str, Any] | None:
        """Update an API key's metadata. Returns updated key data or None if not found."""
        with self.Session() as session:
            query = session.query(ApiKeyRecord).filter(ApiKeyRecord.key_id == key_id)
            if user_id:
                query = query.filter(ApiKeyRecord.user_id == user_id)
            record = query.first()
            if record:
                if name is not None:
                    record.name = name
                session.commit()
                return {
                    "key_id": record.key_id,
                    "name": record.name,
                    "is_active": record.is_active,
                    "created_at": record.created_at,
                    "last_used_at": record.last_used_at,
                }
        return None

    def toggle_key(self, key_id: str, user_id: str | None = None) -> dict[str, Any] | None:
        """Toggle an API key's active state. Returns updated key data or None if not found."""
        with self.Session() as session:
            query = session.query(ApiKeyRecord).filter(ApiKeyRecord.key_id == key_id)
            if user_id:
                query = query.filter(ApiKeyRecord.user_id == user_id)
            record = query.first()
            if record:
                record.is_active = not record.is_active
                session.commit()
                return {
                    "key_id": record.key_id,
                    "name": record.name,
                    "is_active": record.is_active,
                }
        return None

    # ============================================================
    # API Key Group Methods
    # ============================================================

    def create_group(self, name: str, user_id: str, description: str | None = None) -> dict[str, Any]:
        """Create a new API key group."""
        group_id = secrets.token_urlsafe(16)
        now = datetime.now(timezone.utc).isoformat()
        
        # Get max sort_order for this user's groups
        with self.Session() as session:
            max_order = session.query(ApiKeyGroup).filter(
                ApiKeyGroup.user_id == user_id
            ).count()
            
            record = ApiKeyGroup(
                id=group_id,
                user_id=user_id,
                name=name,
                description=description,
                created_at=now,
                sort_order=max_order,
            )
            session.add(record)
            session.commit()
        
        return {
            "id": group_id,
            "name": name,
            "description": description,
            "created_at": now,
            "sort_order": max_order,
            "key_ids": [],
        }

    def list_groups(self, user_id: str) -> list[dict[str, Any]]:
        """List all groups for a user with their associated key IDs."""
        with self.Session() as session:
            groups = session.query(ApiKeyGroup).filter(
                ApiKeyGroup.user_id == user_id
            ).order_by(ApiKeyGroup.sort_order).all()
            
            result = []
            for group in groups:
                # Get key IDs for this group
                keys = session.query(ApiKeyRecord.key_id).filter(
                    ApiKeyRecord.group_id == group.id,
                    ApiKeyRecord.user_id == user_id,
                ).all()
                key_ids = [k[0] for k in keys]
                
                result.append({
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "created_at": group.created_at,
                    "sort_order": group.sort_order,
                    "key_ids": key_ids,
                })
            
            return result

    def get_group(self, group_id: str, user_id: str) -> dict[str, Any] | None:
        """Get a specific group by ID."""
        with self.Session() as session:
            group = session.query(ApiKeyGroup).filter(
                ApiKeyGroup.id == group_id,
                ApiKeyGroup.user_id == user_id,
            ).first()
            
            if not group:
                return None
            
            # Get key IDs for this group
            keys = session.query(ApiKeyRecord.key_id).filter(
                ApiKeyRecord.group_id == group_id,
                ApiKeyRecord.user_id == user_id,
            ).all()
            key_ids = [k[0] for k in keys]
            
            return {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at,
                "sort_order": group.sort_order,
                "key_ids": key_ids,
            }

    def update_group(
        self, 
        group_id: str, 
        user_id: str, 
        name: str | None = None, 
        description: str | None = None
    ) -> dict[str, Any] | None:
        """Update a group's name or description."""
        with self.Session() as session:
            group = session.query(ApiKeyGroup).filter(
                ApiKeyGroup.id == group_id,
                ApiKeyGroup.user_id == user_id,
            ).first()
            
            if not group:
                return None
            
            if name is not None:
                group.name = name
            if description is not None:
                group.description = description
            
            session.commit()
            
            # Get key IDs for this group
            keys = session.query(ApiKeyRecord.key_id).filter(
                ApiKeyRecord.group_id == group_id,
                ApiKeyRecord.user_id == user_id,
            ).all()
            key_ids = [k[0] for k in keys]
            
            return {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at,
                "sort_order": group.sort_order,
                "key_ids": key_ids,
            }

    def delete_group(self, group_id: str, user_id: str) -> bool:
        """Delete a group and unassign all keys from it."""
        with self.Session() as session:
            group = session.query(ApiKeyGroup).filter(
                ApiKeyGroup.id == group_id,
                ApiKeyGroup.user_id == user_id,
            ).first()
            
            if not group:
                return False
            
            # Unassign all keys from this group
            session.query(ApiKeyRecord).filter(
                ApiKeyRecord.group_id == group_id,
                ApiKeyRecord.user_id == user_id,
            ).update({"group_id": None})
            
            session.delete(group)
            session.commit()
            return True

    def assign_keys_to_group(self, group_id: str | None, key_ids: list[str], user_id: str) -> bool:
        """Assign multiple keys to a group. If group_id is None, unassign from any group."""
        with self.Session() as session:
            # Verify group exists if group_id is provided
            if group_id:
                group = session.query(ApiKeyGroup).filter(
                    ApiKeyGroup.id == group_id,
                    ApiKeyGroup.user_id == user_id,
                ).first()
                if not group:
                    return False
            
            # Update keys
            session.query(ApiKeyRecord).filter(
                ApiKeyRecord.key_id.in_(key_ids),
                ApiKeyRecord.user_id == user_id,
            ).update({"group_id": group_id}, synchronize_session="fetch")
            
            session.commit()
            return True

    def unassign_keys_from_group(self, group_id: str, key_ids: list[str], user_id: str) -> bool:
        """Unassign keys from a specific group."""
        with self.Session() as session:
            session.query(ApiKeyRecord).filter(
                ApiKeyRecord.key_id.in_(key_ids),
                ApiKeyRecord.group_id == group_id,
                ApiKeyRecord.user_id == user_id,
            ).update({"group_id": None}, synchronize_session="fetch")
            
            session.commit()
            return True

    def update_key_order(self, key_orders: list[dict[str, Any]], user_id: str) -> bool:
        """Update the sort order for multiple keys."""
        with self.Session() as session:
            for item in key_orders:
                key_id = item.get("key_id")
                sort_order = item.get("sort_order", 0)
                
                session.query(ApiKeyRecord).filter(
                    ApiKeyRecord.key_id == key_id,
                    ApiKeyRecord.user_id == user_id,
                ).update({"sort_order": sort_order})
            
            session.commit()
            return True

    def update_group_order(self, group_orders: list[dict[str, Any]], user_id: str) -> bool:
        """Update the sort order for multiple groups."""
        with self.Session() as session:
            for item in group_orders:
                group_id = item.get("group_id")
                sort_order = item.get("sort_order", 0)
                
                session.query(ApiKeyGroup).filter(
                    ApiKeyGroup.id == group_id,
                    ApiKeyGroup.user_id == user_id,
                ).update({"sort_order": sort_order})
            
            session.commit()
            return True

