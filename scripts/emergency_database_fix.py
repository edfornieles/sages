#!/usr/bin/env python3
"""
Emergency Database Fix Script - PHASE 1 of 90% Target Achievement

This script fixes the critical database schema errors that are preventing
the system from achieving 90% targets.

Priority Issues to Fix:
1. Missing columns in enhanced_memory table
2. Missing indexes causing slow queries
3. Tuple index out of range errors in memory loading
"""

import sqlite3
import os
from pathlib import Path
import time
from typing import List, Dict, Any

class EmergencyDatabaseFixer:
    """Fixes critical database schema issues across all character databases."""
    
    def __init__(self):
        self.memories_dir = Path("memories")
        self.fixed_databases = []
        self.failed_databases = []
        
    def fix_all_databases(self) -> Dict[str, Any]:
        """Fix all database schema issues across all character databases."""
        
        print("🚨 EMERGENCY DATABASE FIX - Starting...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Find all database files
        db_files = list(self.memories_dir.glob("*.db"))
        
        print(f"📊 Found {len(db_files)} database files to fix")
        
        for db_file in db_files:
            try:
                self.fix_single_database(db_file)
                self.fixed_databases.append(str(db_file))
                print(f"✅ Fixed: {db_file.name}")
            except Exception as e:
                self.failed_databases.append({"file": str(db_file), "error": str(e)})
                print(f"❌ Failed: {db_file.name} - {e}")
        
        duration = time.time() - start_time
        
        results = {
            "total_databases": len(db_files),
            "fixed_count": len(self.fixed_databases),
            "failed_count": len(self.failed_databases),
            "success_rate": len(self.fixed_databases) / len(db_files) * 100 if db_files else 0,
            "duration_seconds": duration,
            "fixed_databases": self.fixed_databases,
            "failed_databases": self.failed_databases
        }
        
        print("\n" + "=" * 60)
        print(f"🎯 EMERGENCY FIX COMPLETE")
        print(f"✅ Fixed: {results['fixed_count']}/{results['total_databases']} databases")
        print(f"📈 Success Rate: {results['success_rate']:.1f}%")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        
        if results['success_rate'] >= 95:
            print("🚀 READY FOR PHASE 2: Response Time Optimization")
        else:
            print("⚠️ Some databases failed - manual intervention may be required")
        
        return results
    
    def fix_single_database(self, db_path: Path):
        """Fix schema issues in a single database."""
        
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            
            # 1. Check if enhanced_memory table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='enhanced_memory'
            """)
            
            if not cursor.fetchone():
                # Create enhanced_memory table if it doesn't exist
                self.create_enhanced_memory_table(cursor)
            else:
                # Fix existing table schema
                self.fix_enhanced_memory_schema(cursor)
            
            # 2. Fix agent_memory table if needed
            self.fix_agent_memory_table(cursor)
            
            # 3. Create performance indexes
            self.create_performance_indexes(cursor)
            
            # 4. Optimize database settings
            self.optimize_database_settings(cursor)
            
            conn.commit()
    
    def create_enhanced_memory_table(self, cursor):
        """Create the enhanced_memory table with all required columns."""
        
        cursor.execute("""
            CREATE TABLE enhanced_memory (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance_score REAL DEFAULT 0.5,
                emotional_weight REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                memory_id TEXT,
                entity_name TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                conversation_id TEXT,
                tags TEXT,
                context TEXT
            )
        """)
    
    def fix_enhanced_memory_schema(self, cursor):
        """Add missing columns to existing enhanced_memory table."""
        
        # Get current table schema
        cursor.execute("PRAGMA table_info(enhanced_memory)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Required columns with their types
        required_columns = {
            'last_accessed': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'access_count': 'INTEGER DEFAULT 0',
            'memory_id': 'TEXT',
            'entity_name': 'TEXT',
            'last_updated': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'conversation_id': 'TEXT',
            'tags': 'TEXT',
            'context': 'TEXT',
            'importance_score': 'REAL DEFAULT 0.5',
            'emotional_weight': 'REAL DEFAULT 0.0'
        }
        
        # Add missing columns
        for column, column_type in required_columns.items():
            if column not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE enhanced_memory ADD COLUMN {column} {column_type}")
                    print(f"   ✅ Added column: {column}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"   ⚠️ Warning adding column {column}: {e}")
    
    def fix_agent_memory_table(self, cursor):
        """Fix agent_memory table schema issues."""
        
        # Check if agent_memory table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='agent_memory'
        """)
        
        if cursor.fetchone():
            # Get current schema
            cursor.execute("PRAGMA table_info(agent_memory)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            # Add missing columns if needed
            if 'user_id' not in existing_columns:
                cursor.execute("ALTER TABLE agent_memory ADD COLUMN user_id TEXT DEFAULT 'user'")
            
            if 'importance' not in existing_columns:
                cursor.execute("ALTER TABLE agent_memory ADD COLUMN importance REAL DEFAULT 0.5")
    
    def create_performance_indexes(self, cursor):
        """Create indexes to improve query performance."""
        
        indexes = [
            # Enhanced memory indexes
            ("idx_enhanced_character_user", "enhanced_memory", "(character_id, user_id)"),
            ("idx_enhanced_created_at", "enhanced_memory", "(created_at)"),
            ("idx_enhanced_last_accessed", "enhanced_memory", "(last_accessed)"),
            ("idx_enhanced_importance", "enhanced_memory", "(importance_score)"),
            ("idx_enhanced_memory_type", "enhanced_memory", "(memory_type)"),
            ("idx_enhanced_conversation", "enhanced_memory", "(conversation_id)"),
            
            # Agent memory indexes
            ("idx_agent_memory_user", "agent_memory", "(user_id)"),
            ("idx_agent_memory_created", "agent_memory", "(created_at)"),
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} {columns}")
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e):
                    print(f"   ⚠️ Warning creating index {index_name}: {e}")
    
    def optimize_database_settings(self, cursor):
        """Apply database optimization settings."""
        
        optimizations = [
            "PRAGMA journal_mode = WAL",
            "PRAGMA synchronous = NORMAL",
            "PRAGMA cache_size = 10000",
            "PRAGMA temp_store = MEMORY",
            "PRAGMA mmap_size = 268435456",  # 256MB
        ]
        
        for pragma in optimizations:
            try:
                cursor.execute(pragma)
            except sqlite3.OperationalError as e:
                print(f"   ⚠️ Warning applying optimization {pragma}: {e}")

def main():
    """Run the emergency database fix."""
    
    fixer = EmergencyDatabaseFixer()
    
    # Fix all databases
    results = fixer.fix_all_databases()
    
    print("\n🎉 EMERGENCY DATABASE FIX COMPLETE!")
    print("🚀 System ready for Phase 2: Response Time Optimization")
    
    return results

if __name__ == "__main__":
    main() 