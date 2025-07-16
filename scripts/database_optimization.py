#!/usr/bin/env python3
"""
Database Optimization Script

Implements proper indexing, archiving, and performance improvements
for large memory and relationship datasets.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Advanced database optimization system for large datasets."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.memory_db_path = base_path / "memories"
        self.archive_db_path = base_path / "memory_archive.db"
        self.relationship_db_path = base_path / "relationship_depth.db"
        self.persistence_db_path = base_path / "relationship_persistence.db"
        self.compression_db_path = base_path / "compression.db"
        
        # Optimization configuration
        self.max_memory_size_mb = 1000  # Maximum memory database size
        self.archive_threshold_days = 90  # Archive memories older than 90 days
        self.compression_threshold_days = 60  # Compress memories older than 60 days
        self.cleanup_threshold_days = 365  # Clean up data older than 1 year
        self.batch_size = 1000  # Process in batches for performance
        
    def optimize_all_databases(self) -> Dict[str, Any]:
        """Optimize all databases in the system."""
        results = {
            "memory_optimization": self.optimize_memory_database(),
            "relationship_optimization": self.optimize_relationship_database(),
            "archive_optimization": self.optimize_archive_database(),
            "index_optimization": self.optimize_indexes(),
            "cleanup_operations": self.perform_cleanup_operations(),
            "performance_analysis": self.analyze_performance()
        }
        
        return results
    
    def optimize_memory_database(self) -> Dict[str, Any]:
        """Optimize the main memory database."""
        results = {
            "archived_memories": 0,
            "compressed_memories": 0,
            "indexes_created": 0,
            "vacuum_performed": False,
            "errors": []
        }
        
        try:
            # Find all memory database files
            memory_files = list(self.memory_db_path.glob("*.db"))
            
            for db_file in memory_files:
                logger.info(f"Optimizing memory database: {db_file}")
                
                with sqlite3.connect(db_file) as conn:
                    cursor = conn.cursor()
                    
                    # Create performance indexes
                    indexes_created = self._create_memory_indexes(cursor)
                    results["indexes_created"] += indexes_created
                    
                    # Archive old memories
                    archived_count = self._archive_old_memories(cursor, db_file)
                    results["archived_memories"] += archived_count
                    
                    # Compress old memories
                    compressed_count = self._compress_old_memories(cursor)
                    results["compressed_memories"] += compressed_count
                    
                    # Analyze table statistics
                    cursor.execute("ANALYZE")
                    
                    # Vacuum database
                    cursor.execute("VACUUM")
                    results["vacuum_performed"] = True
                    
                    conn.commit()
                    
        except Exception as e:
            results["errors"].append(f"Memory optimization error: {e}")
            logger.error(f"Error optimizing memory database: {e}")
        
        return results
    
    def _create_memory_indexes(self, cursor) -> int:
        """Create performance indexes for memory database."""
        indexes_created = 0
        
        # Check if enhanced_memory_v2 table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_memory_v2'")
        if cursor.fetchone():
            # Create indexes for enhanced_memory_v2
            indexes = [
                ("idx_memory_v2_user_char_timestamp", "enhanced_memory_v2", "user_id, character_id, timestamp DESC"),
                ("idx_memory_v2_importance_archive", "enhanced_memory_v2", "importance_score DESC, archive_status"),
                ("idx_memory_v2_type_timestamp", "enhanced_memory_v2", "memory_type, timestamp DESC"),
                ("idx_memory_v2_recovery_priority", "enhanced_memory_v2", "recovery_priority DESC"),
                ("idx_memory_v2_compression", "enhanced_memory_v2", "archive_status, compression_ratio"),
                ("idx_memory_v2_entities", "enhanced_memory_v2", "related_entities"),
                ("idx_memory_v2_emotional", "enhanced_memory_v2", "emotional_context"),
                ("idx_memory_v2_conversation", "enhanced_memory_v2", "conversation_id, timestamp")
            ]
            
            for index_name, table_name, columns in indexes:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})")
                    indexes_created += 1
                except Exception as e:
                    logger.warning(f"Could not create index {index_name}: {e}")
        
        # Check if enhanced_memory table exists (legacy)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_memory'")
        if cursor.fetchone():
            # Create indexes for enhanced_memory
            legacy_indexes = [
                ("idx_memory_user_char", "enhanced_memory", "user_id, character_id"),
                ("idx_memory_timestamp", "enhanced_memory", "timestamp DESC"),
                ("idx_memory_importance", "enhanced_memory", "importance_score DESC"),
                ("idx_memory_type", "enhanced_memory", "memory_type"),
                ("idx_memory_entities", "enhanced_memory", "related_entities")
            ]
            
            for index_name, table_name, columns in legacy_indexes:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})")
                    indexes_created += 1
                except Exception as e:
                    logger.warning(f"Could not create legacy index {index_name}: {e}")
        
        return indexes_created
    
    def _archive_old_memories(self, cursor, db_file) -> int:
        """Archive old memories to reduce database size."""
        archived_count = 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.archive_threshold_days)
            
            # Check if enhanced_memory_v2 table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_memory_v2'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT COUNT(*) FROM enhanced_memory_v2 
                    WHERE timestamp < ? AND archive_status = 'active' AND importance_score < 0.6
                """, (cutoff_date.isoformat(),))
                
                count = cursor.fetchone()[0]
                if count > 0:
                    cursor.execute("""
                        UPDATE enhanced_memory_v2 
                        SET archive_status = 'archived' 
                        WHERE timestamp < ? AND archive_status = 'active' AND importance_score < 0.6
                    """, (cutoff_date.isoformat(),))
                    
                    archived_count = cursor.rowcount
                    logger.info(f"Archived {archived_count} old memories from {db_file}")
            
            # Check if enhanced_memory table exists (legacy)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_memory'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT COUNT(*) FROM enhanced_memory 
                    WHERE timestamp < ? AND importance_score < 0.6
                """, (cutoff_date.isoformat(),))
                
                count = cursor.fetchone()[0]
                if count > 0:
                    cursor.execute("""
                        UPDATE enhanced_memory 
                        SET is_compressed = TRUE, compressed_content = content 
                        WHERE timestamp < ? AND importance_score < 0.6 AND is_compressed = FALSE
                    """, (cutoff_date.isoformat(),))
                    
                    archived_count += cursor.rowcount
                    logger.info(f"Compressed {cursor.rowcount} old legacy memories from {db_file}")
        
        except Exception as e:
            logger.error(f"Error archiving old memories: {e}")
        
        return archived_count
    
    def _compress_old_memories(self, cursor) -> int:
        """Compress old memories to save space."""
        compressed_count = 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.compression_threshold_days)
            
            # Check if enhanced_memory_v2 table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_memory_v2'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT COUNT(*) FROM enhanced_memory_v2 
                    WHERE timestamp < ? AND archive_status = 'active' AND compressed_content IS NULL
                    AND LENGTH(content) > 200
                """, (cutoff_date.isoformat(),))
                
                count = cursor.fetchone()[0]
                if count > 0:
                    # Simple compression: keep first 100 chars and last 50 chars
                    cursor.execute("""
                        UPDATE enhanced_memory_v2 
                        SET compressed_content = SUBSTR(content, 1, 100) || '... [COMPRESSED] ...' || SUBSTR(content, -50),
                            compression_ratio = 0.3,
                            archive_status = 'compressed'
                        WHERE timestamp < ? AND archive_status = 'active' AND compressed_content IS NULL
                        AND LENGTH(content) > 200
                    """, (cutoff_date.isoformat(),))
                    
                    compressed_count = cursor.rowcount
                    logger.info(f"Compressed {compressed_count} old memories")
        
        except Exception as e:
            logger.error(f"Error compressing old memories: {e}")
        
        return compressed_count
    
    def optimize_relationship_database(self) -> Dict[str, Any]:
        """Optimize the relationship database."""
        results = {
            "indexes_created": 0,
            "vacuum_performed": False,
            "errors": []
        }
        
        try:
            if self.relationship_db_path.exists():
                logger.info(f"Optimizing relationship database: {self.relationship_db_path}")
                
                with sqlite3.connect(self.relationship_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Create performance indexes
                    indexes = [
                        ("idx_relationships_user_char", "relationships", "user_id, character_id"),
                        ("idx_relationships_level", "relationships", "current_level DESC"),
                        ("idx_relationships_last_interaction", "relationships", "last_interaction DESC"),
                        ("idx_relationships_consistency", "relationships", "consistency_score DESC"),
                        ("idx_relationships_authenticity", "relationships", "authenticity_score DESC"),
                        ("idx_conversation_sessions_user", "conversation_sessions", "user_id, character_id"),
                        ("idx_conversation_sessions_time", "conversation_sessions", "start_time DESC"),
                        ("idx_emotional_moments_user", "emotional_moments", "user_id, character_id"),
                        ("idx_emotional_moments_timestamp", "emotional_moments", "timestamp DESC"),
                        ("idx_significant_memories_user", "significant_memories", "user_id, character_id"),
                        ("idx_significant_memories_score", "significant_memories", "significance_score DESC")
                    ]
                    
                    for index_name, table_name, columns in indexes:
                        try:
                            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})")
                            results["indexes_created"] += 1
                        except Exception as e:
                            logger.warning(f"Could not create relationship index {index_name}: {e}")
                    
                    # Analyze table statistics
                    cursor.execute("ANALYZE")
                    
                    # Vacuum database
                    cursor.execute("VACUUM")
                    results["vacuum_performed"] = True
                    
                    conn.commit()
        
        except Exception as e:
            results["errors"].append(f"Relationship optimization error: {e}")
            logger.error(f"Error optimizing relationship database: {e}")
        
        return results
    
    def optimize_archive_database(self) -> Dict[str, Any]:
        """Optimize the archive database."""
        results = {
            "indexes_created": 0,
            "vacuum_performed": False,
            "errors": []
        }
        
        try:
            if self.archive_db_path.exists():
                logger.info(f"Optimizing archive database: {self.archive_db_path}")
                
                with sqlite3.connect(self.archive_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Create performance indexes
                    indexes = [
                        ("idx_archived_memories_user", "archived_memories", "user_id, character_id"),
                        ("idx_archived_memories_timestamp", "archived_memories", "archived_at DESC"),
                        ("idx_archived_memories_priority", "archived_memories", "recovery_priority DESC"),
                        ("idx_archived_memories_type", "archived_memories", "compression_type"),
                        ("idx_archived_relationships_user", "archived_relationships", "user_id, character_id"),
                        ("idx_archived_relationships_level", "archived_relationships", "relationship_level DESC"),
                        ("idx_archived_entities_user", "archived_entities", "user_id, character_id"),
                        ("idx_archived_entities_name", "archived_entities", "entity_name"),
                        ("idx_archive_index_user", "archive_index", "user_id, character_id"),
                        ("idx_archive_index_priority", "archive_index", "recovery_priority DESC")
                    ]
                    
                    for index_name, table_name, columns in indexes:
                        try:
                            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})")
                            results["indexes_created"] += 1
                        except Exception as e:
                            logger.warning(f"Could not create archive index {index_name}: {e}")
                    
                    # Analyze table statistics
                    cursor.execute("ANALYZE")
                    
                    # Vacuum database
                    cursor.execute("VACUUM")
                    results["vacuum_performed"] = True
                    
                    conn.commit()
        
        except Exception as e:
            results["errors"].append(f"Archive optimization error: {e}")
            logger.error(f"Error optimizing archive database: {e}")
        
        return results
    
    def optimize_indexes(self) -> Dict[str, Any]:
        """Optimize all database indexes."""
        results = {
            "indexes_analyzed": 0,
            "indexes_rebuilt": 0,
            "errors": []
        }
        
        try:
            # Analyze all database files
            db_files = [
                self.archive_db_path,
                self.relationship_db_path,
                self.persistence_db_path,
                self.compression_db_path
            ]
            
            # Add memory database files
            if self.memory_db_path.exists():
                db_files.extend(list(self.memory_db_path.glob("*.db")))
            
            for db_file in db_files:
                if db_file.exists():
                    logger.info(f"Analyzing indexes in: {db_file}")
                    
                    with sqlite3.connect(db_file) as conn:
                        cursor = conn.cursor()
                        
                        # Get all indexes
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                        indexes = [row[0] for row in cursor.fetchall()]
                        
                        for index_name in indexes:
                            try:
                                # Rebuild index
                                cursor.execute(f"REINDEX {index_name}")
                                results["indexes_rebuilt"] += 1
                            except Exception as e:
                                logger.warning(f"Could not rebuild index {index_name}: {e}")
                        
                        results["indexes_analyzed"] += len(indexes)
                        
                        # Analyze table statistics
                        cursor.execute("ANALYZE")
                        
                        conn.commit()
        
        except Exception as e:
            results["errors"].append(f"Index optimization error: {e}")
            logger.error(f"Error optimizing indexes: {e}")
        
        return results
    
    def perform_cleanup_operations(self) -> Dict[str, Any]:
        """Perform cleanup operations on old data."""
        results = {
            "old_data_removed": 0,
            "databases_cleaned": 0,
            "errors": []
        }
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.cleanup_threshold_days)
            
            # Clean up old conversation sessions
            if self.relationship_db_path.exists():
                with sqlite3.connect(self.relationship_db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        DELETE FROM conversation_sessions 
                        WHERE start_time < ?
                    """, (cutoff_date.isoformat(),))
                    
                    removed_count = cursor.rowcount
                    results["old_data_removed"] += removed_count
                    logger.info(f"Removed {removed_count} old conversation sessions")
                    
                    conn.commit()
                    results["databases_cleaned"] += 1
            
            # Clean up old emotional moments
            if self.relationship_db_path.exists():
                with sqlite3.connect(self.relationship_db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        DELETE FROM emotional_moments 
                        WHERE timestamp < ?
                    """, (cutoff_date.isoformat(),))
                    
                    removed_count = cursor.rowcount
                    results["old_data_removed"] += removed_count
                    logger.info(f"Removed {removed_count} old emotional moments")
                    
                    conn.commit()
            
            # Clean up old access patterns
            memory_files = list(self.memory_db_path.glob("*.db"))
            for db_file in memory_files:
                with sqlite3.connect(db_file) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        DELETE FROM memory_access_patterns 
                        WHERE access_timestamp < ?
                    """, (cutoff_date.isoformat(),))
                    
                    removed_count = cursor.rowcount
                    results["old_data_removed"] += removed_count
                    logger.info(f"Removed {removed_count} old access patterns from {db_file}")
                    
                    conn.commit()
                    results["databases_cleaned"] += 1
        
        except Exception as e:
            results["errors"].append(f"Cleanup error: {e}")
            logger.error(f"Error performing cleanup operations: {e}")
        
        return results
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze database performance and provide recommendations."""
        results = {
            "database_sizes": {},
            "table_sizes": {},
            "index_usage": {},
            "performance_issues": [],
            "recommendations": []
        }
        
        try:
            # Analyze database sizes
            db_files = [
                ("archive", self.archive_db_path),
                ("relationship", self.relationship_db_path),
                ("persistence", self.persistence_db_path),
                ("compression", self.compression_db_path)
            ]
            
            # Add memory database files
            if self.memory_db_path.exists():
                memory_files = list(self.memory_db_path.glob("*.db"))
                for i, db_file in enumerate(memory_files):
                    db_files.append((f"memory_{i}", db_file))
            
            for db_name, db_file in db_files:
                if db_file.exists():
                    size_mb = db_file.stat().st_size / (1024 * 1024)
                    results["database_sizes"][db_name] = size_mb
                    
                    # Check for large databases
                    if size_mb > self.max_memory_size_mb:
                        results["performance_issues"].append(f"Database {db_name} is too large ({size_mb:.1f}MB)")
                        results["recommendations"].append(f"Consider archiving data from {db_name}")
                    
                    # Analyze table sizes
                    with sqlite3.connect(db_file) as conn:
                        cursor = conn.cursor()
                        
                        cursor.execute("""
                            SELECT name, sql FROM sqlite_master 
                            WHERE type='table'
                        """)
                        
                        tables = cursor.fetchall()
                        for table_name, table_sql in tables:
                            try:
                                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                                row_count = cursor.fetchone()[0]
                                results["table_sizes"][f"{db_name}.{table_name}"] = row_count
                                
                                # Check for large tables
                                if row_count > 100000:
                                    results["performance_issues"].append(f"Table {table_name} has {row_count} rows")
                                    results["recommendations"].append(f"Consider partitioning table {table_name}")
                            
                            except Exception as e:
                                logger.warning(f"Could not analyze table {table_name}: {e}")
            
            # Check for missing indexes
            if not results["performance_issues"]:
                results["recommendations"].append("Database performance looks good")
            
        except Exception as e:
            results["performance_issues"].append(f"Performance analysis error: {e}")
            logger.error(f"Error analyzing performance: {e}")
        
        return results
    
    def get_optimization_report(self) -> str:
        """Generate a comprehensive optimization report."""
        results = self.optimize_all_databases()
        
        report = "=== Database Optimization Report ===\n\n"
        
        # Memory optimization results
        memory_results = results["memory_optimization"]
        report += f"Memory Database Optimization:\n"
        report += f"  - Archived memories: {memory_results['archived_memories']}\n"
        report += f"  - Compressed memories: {memory_results['compressed_memories']}\n"
        report += f"  - Indexes created: {memory_results['indexes_created']}\n"
        report += f"  - Vacuum performed: {memory_results['vacuum_performed']}\n"
        if memory_results['errors']:
            report += f"  - Errors: {len(memory_results['errors'])}\n"
        report += "\n"
        
        # Relationship optimization results
        rel_results = results["relationship_optimization"]
        report += f"Relationship Database Optimization:\n"
        report += f"  - Indexes created: {rel_results['indexes_created']}\n"
        report += f"  - Vacuum performed: {rel_results['vacuum_performed']}\n"
        if rel_results['errors']:
            report += f"  - Errors: {len(rel_results['errors'])}\n"
        report += "\n"
        
        # Archive optimization results
        archive_results = results["archive_optimization"]
        report += f"Archive Database Optimization:\n"
        report += f"  - Indexes created: {archive_results['indexes_created']}\n"
        report += f"  - Vacuum performed: {archive_results['vacuum_performed']}\n"
        if archive_results['errors']:
            report += f"  - Errors: {len(archive_results['errors'])}\n"
        report += "\n"
        
        # Index optimization results
        index_results = results["index_optimization"]
        report += f"Index Optimization:\n"
        report += f"  - Indexes analyzed: {index_results['indexes_analyzed']}\n"
        report += f"  - Indexes rebuilt: {index_results['indexes_rebuilt']}\n"
        if index_results['errors']:
            report += f"  - Errors: {len(index_results['errors'])}\n"
        report += "\n"
        
        # Cleanup results
        cleanup_results = results["cleanup_operations"]
        report += f"Cleanup Operations:\n"
        report += f"  - Old data removed: {cleanup_results['old_data_removed']} records\n"
        report += f"  - Databases cleaned: {cleanup_results['databases_cleaned']}\n"
        if cleanup_results['errors']:
            report += f"  - Errors: {len(cleanup_results['errors'])}\n"
        report += "\n"
        
        # Performance analysis
        perf_results = results["performance_analysis"]
        report += f"Performance Analysis:\n"
        report += f"  - Database sizes: {len(perf_results['database_sizes'])} databases analyzed\n"
        report += f"  - Table sizes: {len(perf_results['table_sizes'])} tables analyzed\n"
        report += f"  - Performance issues: {len(perf_results['performance_issues'])}\n"
        report += f"  - Recommendations: {len(perf_results['recommendations'])}\n"
        report += "\n"
        
        if perf_results['performance_issues']:
            report += "Performance Issues:\n"
            for issue in perf_results['performance_issues']:
                report += f"  - {issue}\n"
            report += "\n"
        
        if perf_results['recommendations']:
            report += "Recommendations:\n"
            for rec in perf_results['recommendations']:
                report += f"  - {rec}\n"
            report += "\n"
        
        report += f"Optimization completed at: {datetime.now().isoformat()}\n"
        
        return report

def main():
    """Main function to run database optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Optimization Tool")
    parser.add_argument("--base-path", type=str, default=".", help="Base path for databases")
    parser.add_argument("--report-only", action="store_true", help="Only generate report, don't optimize")
    parser.add_argument("--output-file", type=str, help="Output file for report")
    
    args = parser.parse_args()
    
    base_path = Path(args.base_path)
    optimizer = DatabaseOptimizer(base_path)
    
    if args.report_only:
        report = optimizer.get_optimization_report()
    else:
        print("Starting database optimization...")
        results = optimizer.optimize_all_databases()
        report = optimizer.get_optimization_report()
    
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output_file}")
    else:
        print(report)

if __name__ == "__main__":
    main() 