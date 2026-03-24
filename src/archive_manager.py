import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class ArchiveManager:
    """
    Manages the evolutionary history of hyperagents using a SQLite database.
    
    Tracks versions, code changes, performance metrics, and lineage.
    """
    
    def __init__(self, db_path: str, config: Optional[Dict[str, Any]] = None):
        self.db_path = db_path
        self.config = config or {}
        self._initialize_db()
        
    def _initialize_db(self):
        """Create the hyperagents table if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hyperagents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hyperagents (
                version INTEGER PRIMARY KEY,
                parent_version INTEGER,
                timestamp TEXT,
                code TEXT,
                accuracy REAL,
                true_positive_rate REAL,
                false_positive_rate REAL,
                f1_score REAL,
                latency_ms REAL,
                metrics_json TEXT,
                modification_notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_variant(self, 
                    code: str, 
                    accuracy: float, 
                    metrics: Dict[str, Any], 
                    parent_version: Optional[int] = None,
                    modification_notes: str = "") -> int:
        """
        Add a new hyperagent variant to the archive.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get next version number
        cursor.execute("SELECT MAX(version) FROM hyperagents")
        max_v = cursor.fetchone()[0]
        next_v = (max_v + 1) if max_v is not None else 0
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO hyperagents (
                version, parent_version, timestamp, code, 
                accuracy, true_positive_rate, false_positive_rate, 
                f1_score, latency_ms, metrics_json, modification_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            next_v, 
            parent_version, 
            timestamp, 
            code,
            accuracy,
            metrics.get('true_positive_rate', 0.0),
            metrics.get('false_positive_rate', 0.0),
            metrics.get('f1_score', 0.0),
            metrics.get('latency_ms', 0.0),
            json.dumps(metrics),
            modification_notes
        ))
        
        conn.commit()
        conn.close()
        return next_v
        
    def get_variant(self, version: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific variant by version."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM hyperagents WHERE version = ?", (version,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            res = dict(row)
            res['metrics'] = json.loads(res['metrics_json'])
            return res
        return None
        
    def get_latest_variant(self) -> Optional[Dict[str, Any]]:
        """Retrieve the most recent variant."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM hyperagents ORDER BY version DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            res = dict(row)
            res['metrics'] = json.loads(res['metrics_json'])
            return res
        return None
        
    def get_best_variant(self, metric: str = 'accuracy') -> Optional[Dict[str, Any]]:
        """Retrieve the best performing variant based on a metric."""
        if metric not in ['accuracy', 'f1_score']:
            raise ValueError(f"Unsupported metric for best selection: {metric}")
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM hyperagents ORDER BY {metric} DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            res = dict(row)
            res['metrics'] = json.loads(res['metrics_json'])
            return res
        return None

    def get_recent_summary(self, limit: int = 5) -> Dict[str, Any]:
        """Get summary information for the last N variants."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM hyperagents")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(accuracy) FROM hyperagents")
        best_acc = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT version, accuracy, timestamp FROM hyperagents ORDER BY version DESC LIMIT ?", (limit,))
        recent = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_variants': total,
            'best_accuracy': best_acc,
            'recent_variants': recent
        }
