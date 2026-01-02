from __future__ import annotations

import base64
import decimal
import hashlib
import hmac
import json
import math
import re
import secrets
import sqlite3
import threading
import time
from datetime import date, datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import boto3
import mysql.connector
import psycopg2
from psycopg2 import extras
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as crypto_padding
from cryptography.hazmat.backends import default_backend

class _Database_AuditLog:
    def __init__(self, max_entries: int = 10000):
        self.entries: List[Dict[str, Any]] = []
        self.max_entries = max_entries
        self._lock = threading.Lock()

    def log(
        self,
        profile_name: str,
        operation: str,
        sql: str,
        success: bool,
        error: Optional[str] = None,
        rows_affected: Optional[int] = None,
        execution_time_ms: Optional[float] = None,
        db_type: Optional[str] = None
    ):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "profile": profile_name,
            "operation": operation,
            "sql_hash": hashlib.sha256(sql.encode()).hexdigest()[:16],
            "sql_preview": sql[:100] + "..." if len(sql) > 100 else sql,
            "success": success,
            "error": error,
            "rows_affected": rows_affected,
            "execution_time_ms": execution_time_ms,
            "db_type": db_type
        }

        with self._lock:
            self.entries.append(entry)
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries:]

    def get_entries(
        self,
        profile: Optional[str] = None,
        success_only: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        with self._lock:
            filtered = self.entries.copy()

        if profile:
            filtered = [e for e in filtered if e["profile"] == profile]

        if success_only is not None:
            filtered = [e for e in filtered if e["success"] == success_only]

        return filtered[-limit:]

    def clear(self):
        with self._lock:
            self.entries.clear()


class Database:
    DEFAULT_DB_TYPE = "sqlite"
    DEFAULT_TIMEOUT = 30
    
    CONFIGURED_CONNECTIONS = {}
    CONFIGURED_PROFILES: Dict[str, _Database_Profile] = {}

    ENABLE_AUDIT_LOG = True
    ENABLE_SQL_INJECTION_PROTECTION = True
    ENABLE_QUERY_VALIDATION = True

    _active_profile: Optional[_Database_Profile] = None
    _audit_log = _Database_AuditLog()

    SQL_INJECTION_PATTERNS = [
        r";\s*DROP\s+",
        r";\s*DELETE\s+",
        r";\s*TRUNCATE\s+",
        r";\s*UPDATE\s+.*\s+SET\s+",
        r"--\s*$",
        r"/\*.*\*/",
        r"'\s*OR\s+'?1'?\s*=\s*'?1",
        r"'\s*OR\s+''='",
        r"UNION\s+SELECT\s+",
        r";\s*INSERT\s+INTO\s+",
        r"'\s*;\s*--",
        r"EXEC\s*\(",
        r"xp_cmdshell",
        r"LOAD_FILE\s*\(",
        r"INTO\s+OUTFILE",
        r"INTO\s+DUMPFILE",
    ]

    @classmethod
    def load_config(cls, config: dict):
        if "Database" in config.keys():
            tool_config = config["Database"]
            cls.DEFAULT_DB_TYPE = tool_config.get("DEFAULT_DB_TYPE", cls.DEFAULT_DB_TYPE)
            cls.DEFAULT_TIMEOUT = tool_config.get("DEFAULT_TIMEOUT", cls.DEFAULT_TIMEOUT)
            cls.CONFIGURED_CONNECTIONS = tool_config.get("CONNECTIONS", cls.CONFIGURED_CONNECTIONS)

            cls.ENABLE_AUDIT_LOG = tool_config.get("ENABLE_AUDIT_LOG", cls.ENABLE_AUDIT_LOG)
            cls.ENABLE_SQL_INJECTION_PROTECTION = tool_config.get("ENABLE_SQL_INJECTION_PROTECTION", cls.ENABLE_SQL_INJECTION_PROTECTION)
            cls.ENABLE_QUERY_VALIDATION = tool_config.get("ENABLE_QUERY_VALIDATION", cls.ENABLE_QUERY_VALIDATION)

            profiles_config = tool_config.get("PROFILES", {})
            for name, profile_data in profiles_config.items():
                profile_data["name"] = name
                cls.CONFIGURED_PROFILES[name] = _Database_Profile.from_dict(profile_data)

            default_profile = tool_config.get("DEFAULT_PROFILE")
            if default_profile:
                cls.use_profile(default_profile)

    @classmethod
    def use_database(cls, file_path: str) -> str:
        try:
            conn = sqlite3.connect(file_path, timeout=cls.DEFAULT_TIMEOUT)
            conn.close()
            cls.CONFIGURED_CONNECTIONS["sqlite"] = {"database": file_path}
            cls.DEFAULT_DB_TYPE = "sqlite"
            return json.dumps({"status": "success", "database": file_path})
        except Exception as e:
            return json.dumps({"error": str(e)})


    @classmethod
    def create_profile(
        cls,
        name: str,
        permissions: List[str],
        allowed_tables: Optional[List[str]] = None,
        denied_tables: Optional[List[str]] = None,
        max_rows_per_query: Optional[int] = None,
        rate_limit_per_minute: Optional[int] = None,
        require_where_clause: bool = False,
        log_queries: bool = True
    ) -> str:
        try:
            perm_set = set()
            for p in permissions:
                try:
                    perm_set.add(_Database_Permission[p.upper()])
                except KeyError:
                    return json.dumps({"error": f"Invalid permission: {p}"})

            profile = _Database_Profile(
                name=name,
                permissions=perm_set,
                allowed_tables=set(allowed_tables) if allowed_tables else None,
                denied_tables=set(denied_tables) if denied_tables else set(),
                max_rows_per_query=max_rows_per_query,
                rate_limit_per_minute=rate_limit_per_minute,
                require_where_clause=require_where_clause,
                log_queries=log_queries
            )

            cls.CONFIGURED_PROFILES[name] = profile
            return json.dumps({"status": "success", "profile": name, "config": profile.to_dict()})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def use_profile(cls, profile_name: str) -> str:
        if profile_name.lower() == 'none':
            cls._active_profile = None
            return json.dumps({"status": "success", "profile": None, "message": "Profile restrictions disabled"})

        if profile_name in cls.CONFIGURED_PROFILES:
            cls._active_profile = cls.CONFIGURED_PROFILES[profile_name]
            return json.dumps({"status": "success", "profile": profile_name, "config": cls._active_profile.to_dict()})

        if profile_name in _Database_Profile.BUILTIN_PROFILES:
            cls._active_profile = _Database_Profile.BUILTIN_PROFILES[profile_name]
            return json.dumps({"status": "success", "profile": profile_name, "config": cls._active_profile.to_dict()})

        return json.dumps({"error": f"Profile not found: {profile_name}"})

    @classmethod
    def get_profile(cls) -> str:
        if cls._active_profile is None:
            return json.dumps({"profile": None, "message": "No profile restrictions active"})
        return json.dumps({"profile": cls._active_profile.name, "config": cls._active_profile.to_dict()})

    @classmethod
    def list_profiles(cls) -> str:
        profiles = {}

        for name, profile in _Database_Profile.BUILTIN_PROFILES.items():
            profiles[name] = {"type": "builtin", "config": profile.to_dict()}

        for name, profile in cls.CONFIGURED_PROFILES.items():
            profiles[name] = {"type": "custom", "config": profile.to_dict()}

        return json.dumps({"profiles": profiles})

    @classmethod
    def delete_profile(cls, profile_name: str) -> str:
        if profile_name in _Database_Profile.BUILTIN_PROFILES:
            return json.dumps({"error": "Cannot delete built-in profiles"})

        if profile_name in cls.CONFIGURED_PROFILES:
            del cls.CONFIGURED_PROFILES[profile_name]

            if cls._active_profile and cls._active_profile.name == profile_name:
                cls._active_profile = None

            return json.dumps({"status": "success", "deleted": profile_name})

        return json.dumps({"error": f"Profile not found: {profile_name}"})

    ### SECURITY UTILITIES START
    @classmethod
    def _check_sql_injection(cls, sql: str) -> Tuple[bool, str]:
        if not cls.ENABLE_SQL_INJECTION_PROTECTION:
            return True, ""

        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return False, f"Potential SQL injection detected: pattern '{pattern}'"

        return True, ""

    @classmethod
    def _validate_and_log(cls, sql: str, db_type: str) -> Tuple[bool, str]:
        is_safe, injection_error = cls._check_sql_injection(sql)
        if not is_safe:
            if cls.ENABLE_AUDIT_LOG:
                cls._audit_log.log(
                    profile_name=cls._active_profile.name if cls._active_profile else "none",
                    operation="BLOCKED",
                    sql=sql,
                    success=False,
                    error=injection_error,
                    db_type=db_type
                )
            return False, injection_error

        if cls.ENABLE_QUERY_VALIDATION and cls._active_profile:
            is_valid, validation_error = cls._active_profile.validate_query(sql)
            if not is_valid:
                if cls.ENABLE_AUDIT_LOG and cls._active_profile.log_queries:
                    cls._audit_log.log(
                        profile_name=cls._active_profile.name,
                        operation="DENIED",
                        sql=sql,
                        success=False,
                        error=validation_error,
                        db_type=db_type
                    )
                return False, validation_error

        return True, ""
    ### SECURITY UTILITIES END

    @classmethod
    def get_audit_log(cls, profile: Optional[str] = None, success_only: Optional[bool] = None, limit: int = 100) -> str:
        entries = cls._audit_log.get_entries(profile=profile, success_only=success_only, limit=limit)
        return json.dumps({"entries": entries, "count": len(entries)})

    @classmethod
    def clear_audit_log(cls) -> str:
        cls._audit_log.clear()
        return json.dumps({"status": "success", "message": "Audit log cleared"})

    ### PARAMETERIZED QUERIES START
    @classmethod
    def query_safe(
        cls,
        sql: str,
        params: Optional[Union[tuple, dict]] = None,
        db_type: Optional[str] = None,
        connection_params: Optional[dict] = None
    ) -> str:
        target_type = db_type or cls.DEFAULT_DB_TYPE
        params_dict = connection_params or cls.CONFIGURED_CONNECTIONS.get(target_type, {})

        is_valid, error = cls._validate_and_log(sql, target_type)
        if not is_valid:
            return json.dumps({"error": error})

        start_time = time.time()

        if target_type == "sqlite":
            result = cls._query_sqlite_safe(sql, params, params_dict)
        elif target_type == "postgres":
            result = cls._query_postgres_safe(sql, params, params_dict)
        elif target_type == "mysql":
            result = cls._query_mysql_safe(sql, params, params_dict)
        else:
            return json.dumps({"error": f"Parameterized queries not supported for: {target_type}"})

        execution_time = (time.time() - start_time) * 1000

        if cls.ENABLE_AUDIT_LOG and (not cls._active_profile or cls._active_profile.log_queries):
            result_parsed = json.loads(result)
            is_error = isinstance(result_parsed, dict) and "error" in result_parsed
            cls._audit_log.log(
                profile_name=cls._active_profile.name if cls._active_profile else "none",
                operation=cls._get_operation_name(sql),
                sql=sql,
                success=not is_error,
                error=result_parsed.get("error") if isinstance(result_parsed, dict) else None,
                rows_affected=result_parsed.get("rows_affected") if isinstance(result_parsed, dict) else len(result_parsed) if isinstance(result_parsed, list) else None,
                execution_time_ms=execution_time,
                db_type=target_type
            )

        return result
    ### PARAMETERIZED QUERIES END

    @classmethod
    def _get_operation_name(cls, sql: str) -> str:
        sql_upper = sql.strip().upper()
        for op in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE']:
            if sql_upper.startswith(op):
                return op
        return "UNKNOWN"

    @classmethod
    def query(cls, sql: str, db_type: Optional[str] = None, connection_params: Optional[dict] = None) -> str:
        target_type = db_type or cls.DEFAULT_DB_TYPE
        params = connection_params or cls.CONFIGURED_CONNECTIONS.get(target_type, {})

        is_valid, error = cls._validate_and_log(sql, target_type)
        if not is_valid:
            return json.dumps({"error": error})

        start_time = time.time()

        if target_type == "sqlite":
            result = cls._query_sqlite(sql, params)
        elif target_type == "postgres":
            result = cls._query_postgres(sql, params)
        elif target_type == "mysql":
            result = cls._query_mysql(sql, params)
        elif target_type == "dynamodb":
            result = cls._query_dynamodb(sql, params)
        else:
            return json.dumps({"error": f"Unsupported database type: {target_type}"})

        execution_time = (time.time() - start_time) * 1000

        if cls.ENABLE_AUDIT_LOG and (not cls._active_profile or cls._active_profile.log_queries):
            result_parsed = json.loads(result)
            is_error = isinstance(result_parsed, dict) and "error" in result_parsed
            cls._audit_log.log(
                profile_name=cls._active_profile.name if cls._active_profile else "none",
                operation=cls._get_operation_name(sql),
                sql=sql,
                success=not is_error,
                error=result_parsed.get("error") if isinstance(result_parsed, dict) else None,
                rows_affected=result_parsed.get("rows_affected") if isinstance(result_parsed, dict) else len(result_parsed) if isinstance(result_parsed, list) else None,
                execution_time_ms=execution_time,
                db_type=target_type
            )

        return result

    ### PRIVATE UTILITIES START
    @classmethod
    def _apply_row_limit(cls, rows: List, sql: str) -> List:
        if cls._active_profile and cls._active_profile.max_rows_per_query:
            return rows[:cls._active_profile.max_rows_per_query]
        return rows

    @classmethod
    def _query_sqlite(cls, sql: str, params: dict) -> str:
        db_path = params.get("database", ":memory:")
        conn = None
        try:
            conn = sqlite3.connect(db_path, timeout=cls.DEFAULT_TIMEOUT)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)
            if sql.strip().upper().startswith("SELECT"):
                rows = [dict(row) for row in cursor.fetchall()]
                rows = cls._apply_row_limit(rows, sql)
                return json.dumps(rows, default=cls._json_serializer)
            else:
                conn.commit()
                rows_affected = cursor.rowcount
                if cls._active_profile and cls._active_profile.max_rows_per_query:
                    if rows_affected > cls._active_profile.max_rows_per_query:
                        conn.rollback()
                        return json.dumps({"error": f"Query would affect {rows_affected} rows, max allowed: {cls._active_profile.max_rows_per_query}"})
                return json.dumps({"status": "success", "rows_affected": rows_affected})
        except Exception as e:
            return json.dumps({"error": str(e)})
        finally:
            if conn:
                conn.close()

    @classmethod
    def _query_sqlite_safe(cls, sql: str, query_params: Optional[Union[tuple, dict]], conn_params: dict) -> str:
        db_path = conn_params.get("database", ":memory:")
        conn = None
        try:
            conn = sqlite3.connect(db_path, timeout=cls.DEFAULT_TIMEOUT)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if query_params:
                cursor.execute(sql, query_params)
            else:
                cursor.execute(sql)

            if sql.strip().upper().startswith("SELECT"):
                rows = [dict(row) for row in cursor.fetchall()]
                rows = cls._apply_row_limit(rows, sql)
                return json.dumps(rows, default=cls._json_serializer)
            else:
                conn.commit()
                rows_affected = cursor.rowcount
                if cls._active_profile and cls._active_profile.max_rows_per_query:
                    if rows_affected > cls._active_profile.max_rows_per_query:
                        conn.rollback()
                        return json.dumps({"error": f"Query would affect {rows_affected} rows, max allowed: {cls._active_profile.max_rows_per_query}"})
                return json.dumps({"status": "success", "rows_affected": rows_affected})
        except Exception as e:
            return json.dumps({"error": str(e)})
        finally:
            if conn:
                conn.close()

    @classmethod
    def _query_postgres(cls, sql: str, params: dict) -> str:
        if psycopg2 is None:
            return json.dumps({"error": "psycopg2 module not installed"})
        conn = None
        try:
            conn = psycopg2.connect(**params)
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(sql)
                if sql.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    rows = cls._apply_row_limit(rows, sql)
                    return json.dumps(rows, default=cls._json_serializer)
                else:
                    conn.commit()
                    rows_affected = cursor.rowcount
                    if cls._active_profile and cls._active_profile.max_rows_per_query:
                        if rows_affected > cls._active_profile.max_rows_per_query:
                            conn.rollback()
                            return json.dumps({"error": f"Query would affect {rows_affected} rows, max allowed: {cls._active_profile.max_rows_per_query}"})
                    return json.dumps({"status": "success", "rows_affected": rows_affected})
        except Exception as e:
            return json.dumps({"error": str(e)})
        finally:
            if conn:
                conn.close()

    @classmethod
    def _query_postgres_safe(cls, sql: str, query_params: Optional[Union[tuple, dict]], conn_params: dict) -> str:
        if psycopg2 is None:
            return json.dumps({"error": "psycopg2 module not installed"})
        conn = None
        try:
            conn = psycopg2.connect(**conn_params)
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                if query_params:
                    cursor.execute(sql, query_params)
                else:
                    cursor.execute(sql)

                if sql.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    rows = cls._apply_row_limit(rows, sql)
                    return json.dumps(rows, default=cls._json_serializer)
                else:
                    conn.commit()
                    rows_affected = cursor.rowcount
                    if cls._active_profile and cls._active_profile.max_rows_per_query:
                        if rows_affected > cls._active_profile.max_rows_per_query:
                            conn.rollback()
                            return json.dumps({"error": f"Query would affect {rows_affected} rows, max allowed: {cls._active_profile.max_rows_per_query}"})
                    return json.dumps({"status": "success", "rows_affected": rows_affected})
        except Exception as e:
            return json.dumps({"error": str(e)})
        finally:
            if conn:
                conn.close()

    @classmethod
    def _query_mysql(cls, sql: str, params: dict) -> str:
        if mysql.connector is None:
            return json.dumps({"error": "mysql-connector-python module not installed"})
        conn = None
        try:
            conn = mysql.connector.connect(**params)
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                if sql.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    rows = cls._apply_row_limit(rows, sql)
                    return json.dumps(rows, default=cls._json_serializer)
                else:
                    conn.commit()
                    rows_affected = cursor.rowcount
                    if cls._active_profile and cls._active_profile.max_rows_per_query:
                        if rows_affected > cls._active_profile.max_rows_per_query:
                            conn.rollback()
                            return json.dumps({"error": f"Query would affect {rows_affected} rows, max allowed: {cls._active_profile.max_rows_per_query}"})
                    return json.dumps({"status": "success", "rows_affected": rows_affected})
        except Exception as e:
            return json.dumps({"error": str(e)})
        finally:
            if conn:
                conn.close()

    @classmethod
    def _query_mysql_safe(cls, sql: str, query_params: Optional[Union[tuple, dict]], conn_params: dict) -> str:
        if mysql.connector is None:
            return json.dumps({"error": "mysql-connector-python module not installed"})
        conn = None
        try:
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cursor:
                if query_params:
                    cursor.execute(sql, query_params)
                else:
                    cursor.execute(sql)

                if sql.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    rows = cls._apply_row_limit(rows, sql)
                    return json.dumps(rows, default=cls._json_serializer)
                else:
                    conn.commit()
                    rows_affected = cursor.rowcount
                    if cls._active_profile and cls._active_profile.max_rows_per_query:
                        if rows_affected > cls._active_profile.max_rows_per_query:
                            conn.rollback()
                            return json.dumps({"error": f"Query would affect {rows_affected} rows, max allowed: {cls._active_profile.max_rows_per_query}"})
                    return json.dumps({"status": "success", "rows_affected": rows_affected})
        except Exception as e:
            return json.dumps({"error": str(e)})
        finally:
            if conn:
                conn.close()

    @classmethod
    def _query_dynamodb(cls, sql: str, params: dict) -> str:
        if boto3 is None:
            return json.dumps({"error": "boto3 module not installed"})
        try:
            session_kwargs = {}
            if "region_name" in params:
                session_kwargs["region_name"] = params["region_name"]
            if "aws_access_key_id" in params:
                session_kwargs["aws_access_key_id"] = params["aws_access_key_id"]
            if "aws_secret_access_key" in params:
                session_kwargs["aws_secret_access_key"] = params["aws_secret_access_key"]
            dynamodb = boto3.client('dynamodb', **session_kwargs)
            response = dynamodb.execute_statement(Statement=sql)
            items = response.get('Items', [])
            parsed_items = [cls._deserialize_dynamodb_item(item) for item in items]
            
            return json.dumps(parsed_items, default=cls._json_serializer)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def _deserialize_dynamodb_item(cls, item: dict) -> dict:
        from boto3.dynamodb.types import TypeDeserializer
        deserializer = TypeDeserializer()
        return {k: deserializer.deserialize(v) for k, v in item.items()}

    @classmethod
    def _json_serializer(cls, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")
    ### PRIVATE UTILITIES END

    _encryption_key: Optional[bytes] = None

    _CHAR_TO_GROUP: Dict[str, str] = {}

    @classmethod
    def _build_group_mapping(cls) -> Dict[str, str]:
        """
        Build character to group mapping:
        - Letters: ceil(position/3) → A-I (a-c=A, d-f=B, g-i=C, j-l=D, m-o=E, p-r=F, s-u=G, v-x=H, y-z=I)
        - Numbers: J
        - Symbols (._-+@): K
        """
        if cls._CHAR_TO_GROUP:
            return cls._CHAR_TO_GROUP

        groups = {}

        for i, letter in enumerate('abcdefghijklmnopqrstuvwxyz', 1):
            group_num = math.ceil(i / 3)
            group_letter = chr(ord('A') + group_num - 1)
            groups[letter] = group_letter

        for digit in '0123456789':
            groups[digit] = 'J'

        for sym in '._-+@':
            groups[sym] = 'K'

        cls._CHAR_TO_GROUP = groups
        return groups

    @classmethod
    def set_encryption_key(cls, key: Union[str, bytes]) -> str:
        try:
            if isinstance(key, str):
                try:
                    key_bytes = base64.b64decode(key)
                except:
                    try:
                        key_bytes = bytes.fromhex(key)
                    except:
                        key_bytes = hashlib.sha256(key.encode('utf-8')).digest()
            else:
                key_bytes = key

            if len(key_bytes) != 32:
                return json.dumps({"error": f"Key must be 32 bytes for AES-256, got {len(key_bytes)}"})

            cls._encryption_key = key_bytes
            return json.dumps({"status": "success", "message": "Encryption key set"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def generate_encryption_key(cls, set_as_current: bool = True) -> str:
        key = secrets.token_bytes(32)
        key_b64 = base64.b64encode(key).decode('utf-8')

        if set_as_current:
            cls._encryption_key = key

        return json.dumps({
            "status": "success",
            "key_base64": key_b64,
            "key_hex": key.hex(),
            "set_as_current": set_as_current
        })

    @classmethod
    def encrypt(cls, plaintext: str, key: Optional[Union[str, bytes]] = None) -> str:
        try:
            if key:
                if isinstance(key, str):
                    enc_key = hashlib.sha256(key.encode('utf-8')).digest()
                else:
                    enc_key = key
            elif cls._encryption_key:
                enc_key = cls._encryption_key
            else:
                return json.dumps({"error": "No encryption key set. Call set_encryption_key() or generate_encryption_key() first"})

            iv = secrets.token_bytes(16)

            padder = crypto_padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

            cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()

            result = base64.b64encode(iv + ciphertext).decode('utf-8')

            return json.dumps({"status": "success", "ciphertext": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def decrypt(cls, ciphertext: str, key: Optional[Union[str, bytes]] = None) -> str:
        try:
            if key:
                if isinstance(key, str):
                    enc_key = hashlib.sha256(key.encode('utf-8')).digest()
                else:
                    enc_key = key
            elif cls._encryption_key:
                enc_key = cls._encryption_key
            else:
                return json.dumps({"error": "No encryption key set. Call set_encryption_key() or generate_encryption_key() first"})

            data = base64.b64decode(ciphertext)
            iv = data[:16]
            encrypted = data[16:]

            cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted) + decryptor.finalize()

            unpadder = crypto_padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()

            return json.dumps({"status": "success", "plaintext": plaintext.decode('utf-8')})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def hash(cls, text: str, algorithm: str = "sha256") -> str:
        try:
            if algorithm.lower() in ('blake2b', 'blake2s'):
                h = hashlib.new(algorithm.lower())
            else:
                h = hashlib.new(algorithm.lower())
            h.update(text.encode('utf-8'))
            return json.dumps({
                "status": "success",
                "hash": h.hexdigest(),
                "algorithm": algorithm.lower()
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def verify_hash(cls, text: str, hash_value: str, algorithm: str = "sha256") -> str:
        try:
            result = json.loads(cls.hash(text, algorithm))
            if "error" in result:
                return json.dumps(result)

            computed = result["hash"].lower()
            expected = hash_value.lower()

            matches = hmac.compare_digest(computed, expected)

            return json.dumps({
                "status": "success",
                "matches": matches
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def hash_password(cls, password: str, salt: Optional[str] = None) -> str:
        try:
            if salt:
                salt_bytes = base64.b64decode(salt)
            else:
                salt_bytes = secrets.token_bytes(16)

            hash_bytes = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt_bytes,
                100000
            )

            return json.dumps({
                "status": "success",
                "hash": base64.b64encode(hash_bytes).decode('utf-8'),
                "salt": base64.b64encode(salt_bytes).decode('utf-8')
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def verify_password(cls, password: str, hash_value: str, salt: str) -> str:
        try:
            result = json.loads(cls.hash_password(password, salt))
            if "error" in result:
                return json.dumps(result)

            matches = hmac.compare_digest(result["hash"], hash_value)

            return json.dumps({
                "status": "success",
                "matches": matches
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    ### FIND FLAG SYSTEM START
    @classmethod
    def generate_find_flag(cls, text: str) -> str:
        try:
            char_to_group = cls._build_group_mapping()
            text = text.lower().strip()

            groups_sequence = []
            for char in text:
                group = char_to_group.get(char)
                if group:
                    groups_sequence.append(group)

            group_set = ''.join(sorted(set(groups_sequence)))

            bigrams_set = set()
            for i in range(len(groups_sequence) - 1):
                bigram = groups_sequence[i] + groups_sequence[i + 1]
                bigrams_set.add(bigram)

            bigrams = ''.join(sorted(bigrams_set))

            fingerprint = f"{group_set}.{bigrams}"

            return json.dumps({
                "status": "success",
                "input": text,
                "group_set": group_set,
                "bigrams": bigrams,
                "fingerprint": fingerprint,
                "groups_sequence": ''.join(groups_sequence)
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def matches_find_flag(cls, stored_fingerprint: str, search_fingerprint: str) -> str:
        try:
            stored_parts = stored_fingerprint.split('.')
            search_parts = search_fingerprint.split('.')

            stored_groups = set(stored_parts[0]) if len(stored_parts) > 0 else set()
            stored_bigrams = set()
            if len(stored_parts) > 1:
                bg = stored_parts[1]
                stored_bigrams = {bg[i:i+2] for i in range(0, len(bg), 2)}

            search_groups = set(search_parts[0]) if len(search_parts) > 0 else set()
            search_bigrams = set()
            if len(search_parts) > 1:
                bg = search_parts[1]
                search_bigrams = {bg[i:i+2] for i in range(0, len(bg), 2)}

            groups_match = search_groups.issubset(stored_groups)

            bigrams_match = search_bigrams.issubset(stored_bigrams)

            matches = groups_match and bigrams_match

            return json.dumps({
                "status": "success",
                "matches": matches,
                "groups_match": groups_match,
                "bigrams_match": bigrams_match,
                "stored_groups": ''.join(sorted(stored_groups)),
                "search_groups": ''.join(sorted(search_groups)),
                "missing_groups": ''.join(sorted(search_groups - stored_groups)),
                "missing_bigrams": list(search_bigrams - stored_bigrams)
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def generate_sql_where(cls, search_text: str, group_col: str = 'group_set',
                           bigram_col: str = 'group_bigrams') -> str:
        try:
            fp_result = json.loads(cls.generate_find_flag(search_text))
            if "error" in fp_result:
                return json.dumps(fp_result)

            conditions = []

            for group in fp_result['group_set']:
                conditions.append(f"{group_col} LIKE '%{group}%'")

            bigrams = fp_result['bigrams']
            for i in range(0, len(bigrams), 2):
                bigram = bigrams[i:i+2]
                if len(bigram) == 2:
                    conditions.append(f"{bigram_col} LIKE '%{bigram}%'")

            where_clause = ' AND '.join(conditions) if conditions else '1=1'

            return json.dumps({
                "status": "success",
                "where_clause": where_clause,
                "search_text": search_text,
                "group_set": fp_result['group_set'],
                "bigrams": fp_result['bigrams']
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def search_find_flag(cls, search_terms: List[str], match_all: bool = True,
                         fingerprint_col: str = 'fingerprint') -> str:
        try:
            all_conditions = []

            for term in search_terms:
                term = term.strip()
                if not term:
                    continue

                fp_result = json.loads(cls.generate_find_flag(term))
                if "error" in fp_result:
                    continue

                term_conditions = []

                for group in fp_result['group_set']:
                    term_conditions.append(f"{fingerprint_col} LIKE '%{group}%'")

                bigrams = fp_result['bigrams']
                for i in range(0, len(bigrams), 2):
                    bigram = bigrams[i:i+2]
                    if len(bigram) == 2:
                        term_conditions.append(f"{fingerprint_col} LIKE '%{bigram}%'")

                if term_conditions:
                    if len(term_conditions) == 1:
                        all_conditions.append(term_conditions[0])
                    else:
                        all_conditions.append(f"({' AND '.join(term_conditions)})")

            if match_all:
                outer_operator = " AND "
            else:
                outer_operator = " OR "

            if all_conditions:
                where_clause = f"({outer_operator.join(all_conditions)})"
            else:
                where_clause = "1=1"

            return json.dumps({
                "status": "success",
                "where_clause": where_clause,
                "operator": "AND" if match_all else "OR",
                "term_count": len(all_conditions)
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def verify_find_flag(cls, fingerprint: str, search_term: str) -> str:
        try:
            search_fp_result = json.loads(cls.generate_find_flag(search_term))
            if "error" in search_fp_result:
                return json.dumps(search_fp_result)

            search_fingerprint = search_fp_result['fingerprint']

            return cls.matches_find_flag(fingerprint, search_fingerprint)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @classmethod
    def get_group_mapping(cls) -> str:
        try:
            char_to_group = cls._build_group_mapping()

            groups_to_chars: Dict[str, List[str]] = {}
            for char, group in char_to_group.items():
                if group not in groups_to_chars:
                    groups_to_chars[group] = []
                groups_to_chars[group].append(char)

            return json.dumps({
                "status": "success",
                "char_to_group": char_to_group,
                "groups_to_chars": {k: ''.join(sorted(v)) for k, v in sorted(groups_to_chars.items())},
                "description": {
                    "A": "a, b, c",
                    "B": "d, e, f",
                    "C": "g, h, i",
                    "D": "j, k, l",
                    "E": "m, n, o",
                    "F": "p, q, r",
                    "G": "s, t, u",
                    "H": "v, w, x",
                    "I": "y, z",
                    "J": "0-9",
                    "K": ". _ - + @"
                }
            })
        except Exception as e:
            return json.dumps({"error": str(e)})


    ### FIND FLAG SYSTEM END

class _Database_Permission(Enum):
    SELECT = auto()
    INSERT = auto()
    UPDATE = auto()
    DELETE = auto()
    CREATE = auto()
    DROP = auto()
    ALTER = auto()
    TRUNCATE = auto()
    EXECUTE = auto()
    GRANT = auto()
    ALL = auto()

class _Database_Profile:
    BUILTIN_PROFILES: Dict[str, '_Database_Profile'] = {}

    def __init__(
        self,
        name: str,
        permissions: Set[_Database_Permission],
        allowed_tables: Optional[Set[str]] = None,
        denied_tables: Optional[Set[str]] = None,
        max_rows_per_query: Optional[int] = None,
        rate_limit_per_minute: Optional[int] = None,
        allowed_columns: Optional[Dict[str, Set[str]]] = None,
        denied_columns: Optional[Dict[str, Set[str]]] = None,
        require_where_clause: bool = False,
        log_queries: bool = True,
        custom_validators: Optional[List[Callable[[str], Tuple[bool, str]]]] = None
    ):
        self.name = name
        self.permissions = permissions
        self.allowed_tables = allowed_tables
        self.denied_tables = denied_tables or set()
        self.max_rows_per_query = max_rows_per_query
        self.rate_limit_per_minute = rate_limit_per_minute
        self.allowed_columns = allowed_columns or {}
        self.denied_columns = denied_columns or {}
        self.require_where_clause = require_where_clause
        self.log_queries = log_queries
        self.custom_validators = custom_validators or []

        self._query_timestamps: List[float] = []
        self._rate_lock = threading.Lock()

    def has_permission(self, permission: _Database_Permission) -> bool:
        if _Database_Permission.ALL in self.permissions:
            return True
        return permission in self.permissions

    def check_rate_limit(self) -> Tuple[bool, str]:
        if self.rate_limit_per_minute is None:
            return True, ""

        with self._rate_lock:
            now = time.time()
            self._query_timestamps = [t for t in self._query_timestamps if now - t < 60]

            if len(self._query_timestamps) >= self.rate_limit_per_minute:
                return False, f"Rate limit exceeded: {self.rate_limit_per_minute} queries/minute"

            self._query_timestamps.append(now)
            return True, ""

    def validate_query(self, sql: str) -> Tuple[bool, str]:
        sql_upper = sql.strip().upper()
        sql_normalized = ' '.join(sql.split())

        operation = self._get_operation_type(sql_upper)
        if operation is None:
            return False, "Unable to determine SQL operation type"

        if not self.has_permission(operation):
            return False, f"Permission denied: {operation.name} not allowed for profile '{self.name}'"

        rate_ok, rate_msg = self.check_rate_limit()
        if not rate_ok:
            return False, rate_msg

        tables = self._extract_tables(sql_normalized)

        for table in tables:
            table_lower = table.lower()

            if table_lower in {t.lower() for t in self.denied_tables}:
                return False, f"Access denied: table '{table}' is restricted"

            if self.allowed_tables is not None:
                if table_lower not in {t.lower() for t in self.allowed_tables}:
                    return False, f"Access denied: table '{table}' is not in allowed list"

        columns = self._extract_columns(sql_normalized)
        for table, cols in columns.items():
            table_lower = table.lower()

            if table_lower in self.denied_columns:
                denied = {c.lower() for c in self.denied_columns[table_lower]}
                for col in cols:
                    if col.lower() in denied:
                        return False, f"Access denied: column '{col}' in table '{table}' is restricted"

            if table_lower in self.allowed_columns:
                allowed = {c.lower() for c in self.allowed_columns[table_lower]}
                for col in cols:
                    if col.lower() not in allowed and col != '*':
                        return False, f"Access denied: column '{col}' not allowed for table '{table}'"

        if self.require_where_clause:
            if operation in (_Database_Permission.UPDATE, _Database_Permission.DELETE):
                if 'WHERE' not in sql_upper:
                    return False, f"{operation.name} requires WHERE clause for profile '{self.name}'"

        for validator in self.custom_validators:
            is_valid, error = validator(sql)
            if not is_valid:
                return False, error

        return True, ""

    def _get_operation_type(self, sql_upper: str) -> Optional[_Database_Permission]:
        sql_upper = sql_upper.strip()

        if sql_upper.startswith('SELECT'):
            return _Database_Permission.SELECT
        elif sql_upper.startswith('INSERT'):
            return _Database_Permission.INSERT
        elif sql_upper.startswith('UPDATE'):
            return _Database_Permission.UPDATE
        elif sql_upper.startswith('DELETE'):
            return _Database_Permission.DELETE
        elif sql_upper.startswith('CREATE'):
            return _Database_Permission.CREATE
        elif sql_upper.startswith('DROP'):
            return _Database_Permission.DROP
        elif sql_upper.startswith('ALTER'):
            return _Database_Permission.ALTER
        elif sql_upper.startswith('TRUNCATE'):
            return _Database_Permission.TRUNCATE
        elif sql_upper.startswith(('EXEC', 'CALL')):
            return _Database_Permission.EXECUTE
        elif sql_upper.startswith('GRANT'):
            return _Database_Permission.GRANT
        return None

    def _extract_tables(self, sql: str) -> Set[str]:
        tables = set()
        sql_upper = sql.upper()

        from_match = re.search(r'\bFROM\s+([^\s,;()]+)', sql, re.IGNORECASE)
        if from_match:
            tables.add(from_match.group(1).strip('`"[]'))

        join_matches = re.findall(r'\bJOIN\s+([^\s,;()]+)', sql, re.IGNORECASE)
        for match in join_matches:
            tables.add(match.strip('`"[]'))

        insert_match = re.search(r'\bINSERT\s+INTO\s+([^\s(]+)', sql, re.IGNORECASE)
        if insert_match:
            tables.add(insert_match.group(1).strip('`"[]'))

        update_match = re.search(r'\bUPDATE\s+([^\s,]+)', sql, re.IGNORECASE)
        if update_match:
            tables.add(update_match.group(1).strip('`"[]'))

        delete_match = re.search(r'\bDELETE\s+FROM\s+([^\s,]+)', sql, re.IGNORECASE)
        if delete_match:
            tables.add(delete_match.group(1).strip('`"[]'))

        ddl_match = re.search(r'\b(?:CREATE|DROP|ALTER|TRUNCATE)\s+TABLE\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?([^\s(]+)', sql, re.IGNORECASE)
        if ddl_match:
            tables.add(ddl_match.group(1).strip('`"[]'))

        return tables

    def _extract_columns(self, sql: str) -> Dict[str, Set[str]]:
        columns: Dict[str, Set[str]] = {}

        select_match = re.search(r'\bSELECT\s+(.*?)\s+FROM\s+(\S+)', sql, re.IGNORECASE | re.DOTALL)
        if select_match:
            cols_str = select_match.group(1)
            table = select_match.group(2).strip('`"[]')

            if '*' in cols_str:
                columns[table] = {'*'}
            else:
                cols = [c.strip().split('.')[-1].strip('`"[]') for c in cols_str.split(',')]
                columns[table] = set(cols)

        return columns

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "permissions": [p.name for p in self.permissions],
            "allowed_tables": list(self.allowed_tables) if self.allowed_tables else None,
            "denied_tables": list(self.denied_tables),
            "max_rows_per_query": self.max_rows_per_query,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "require_where_clause": self.require_where_clause,
            "log_queries": self.log_queries
        }

    @classmethod
    def from_dict(cls, data: dict) -> '_Database_Profile':
        permissions = {_Database_Permission[p] for p in data.get("permissions", [])}

        return cls(
            name=data["name"],
            permissions=permissions,
            allowed_tables=set(data["allowed_tables"]) if data.get("allowed_tables") else None,
            denied_tables=set(data.get("denied_tables", [])),
            max_rows_per_query=data.get("max_rows_per_query"),
            rate_limit_per_minute=data.get("rate_limit_per_minute"),
            require_where_clause=data.get("require_where_clause", False),
            log_queries=data.get("log_queries", True)
        )


_Database_Profile.BUILTIN_PROFILES = {
    "read_only": _Database_Profile(
        name="read_only",
        permissions={_Database_Permission.SELECT},
        log_queries=True
    ),
    "writer": _Database_Profile(
        name="writer",
        permissions={_Database_Permission.SELECT, _Database_Permission.INSERT, _Database_Permission.UPDATE},
        require_where_clause=True,
        log_queries=True
    ),
    "editor": _Database_Profile(
        name="editor",
        permissions={_Database_Permission.SELECT, _Database_Permission.INSERT, _Database_Permission.UPDATE, _Database_Permission.DELETE},
        require_where_clause=True,
        log_queries=True
    ),
    "admin": _Database_Profile(
        name="admin",
        permissions={_Database_Permission.ALL},
        log_queries=True
    ),
    "schema_viewer": _Database_Profile(
        name="schema_viewer",
        permissions={_Database_Permission.SELECT},
        allowed_tables={"sqlite_master", "information_schema", "pg_catalog"},
        log_queries=True
    )
}