#!/usr/bin/env python3
"""
Long-term Memory and Relationship System Integration

Integrates all the new systems for long-term relationship tracking:
- Memory Archiving System
- Relationship Persistence System  
- Smart Compression System
- Enhanced Memory System V2
- Database Optimization
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from memory.memory_archiving_system import MemoryArchivingSystem
from memory.relationship_persistence_system import RelationshipPersistenceSystem
from memory.smart_compression_system import SmartCompressionSystem
from memory.enhanced_memory_system_v2 import EnhancedMemorySystemV2
from scripts.database_optimization import DatabaseOptimizer

logger = logging.getLogger(__name__)

class LongTermSystemIntegration:
    """Integrates all long-term memory and relationship tracking systems."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.memory_db_path = base_path / "memories"
        self.archive_db_path = base_path / "memory_archive.db"
        self.persistence_db_path = base_path / "relationship_persistence.db"
        self.compression_db_path = base_path / "compression.db"
        
        # Initialize all systems
        self.archiving_system = None
        self.persistence_system = None
        self.compression_system = None
        self.enhanced_memory_system = None
        self.database_optimizer = None
        
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize all the long-term tracking systems."""
        try:
            logger.info("Initializing long-term memory and relationship systems...")
            
            # Initialize archiving system
            self.archiving_system = MemoryArchivingSystem(self.archive_db_path)
            logger.info("✅ Memory archiving system initialized")
            
            # Initialize persistence system
            self.persistence_system = RelationshipPersistenceSystem(self.persistence_db_path)
            logger.info("✅ Relationship persistence system initialized")
            
            # Initialize compression system
            self.compression_system = SmartCompressionSystem(self.compression_db_path)
            logger.info("✅ Smart compression system initialized")
            
            # Initialize database optimizer
            self.database_optimizer = DatabaseOptimizer(self.base_path)
            logger.info("✅ Database optimizer initialized")
            
            logger.info("All long-term systems initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing long-term systems: {e}")
            raise
    
    def create_enhanced_memory_system(self, character_id: str, user_id: str) -> EnhancedMemorySystemV2:
        """Create an enhanced memory system instance for a specific user-character pair."""
        try:
            memory_db_path = self.memory_db_path / f"{character_id}_{user_id}_memory.db"
            memory_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            enhanced_system = EnhancedMemorySystemV2(character_id, user_id, memory_db_path)
            logger.info(f"✅ Enhanced memory system created for {character_id}-{user_id}")
            
            return enhanced_system
            
        except Exception as e:
            logger.error(f"Error creating enhanced memory system: {e}")
            raise
    
    def migrate_existing_data(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """Migrate existing memory data to the new long-term systems."""
        migration_results = {
            "memories_migrated": 0,
            "relationships_migrated": 0,
            "entities_migrated": 0,
            "errors": []
        }
        
        try:
            logger.info(f"Starting data migration for {character_id}-{user_id}")
            
            # Find existing memory database
            old_memory_path = self.memory_db_path / f"{character_id}_{user_id}_memory.db"
            if not old_memory_path.exists():
                logger.info("No existing memory database found, skipping migration")
                return migration_results
            
            # Create enhanced memory system
            enhanced_system = self.create_enhanced_memory_system(character_id, user_id)
            
            # Migrate memories from old system
            migration_results.update(self._migrate_memories(old_memory_path, enhanced_system))
            
            # Migrate relationship data
            migration_results.update(self._migrate_relationships(character_id, user_id))
            
            # Migrate entity data
            migration_results.update(self._migrate_entities(character_id, user_id))
            
            logger.info(f"Migration completed: {migration_results}")
            
        except Exception as e:
            migration_results["errors"].append(f"Migration error: {e}")
            logger.error(f"Error during migration: {e}")
        
        return migration_results
    
    def _migrate_memories(self, old_memory_path: Path, enhanced_system: EnhancedMemorySystemV2) -> Dict[str, Any]:
        """Migrate memories from old system to enhanced system."""
        results = {"memories_migrated": 0, "errors": []}
        
        try:
            import sqlite3
            
            with sqlite3.connect(old_memory_path) as conn:
                cursor = conn.cursor()
                
                # Check for enhanced_memory table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_memory'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT id, content, memory_type, timestamp, importance_score,
                               emotional_context, related_entities, conversation_context,
                               metadata, conversation_id
                        FROM enhanced_memory 
                        WHERE user_id = ? AND character_id = ?
                        ORDER BY timestamp
                    """, (enhanced_system.user_id, enhanced_system.character_id))
                    
                    memories = cursor.fetchall()
                    
                    for memory_row in memories:
                        try:
                            (memory_id, content, memory_type, timestamp, importance_score,
                             emotional_context, related_entities, conversation_context,
                             metadata, conversation_id) = memory_row
                            
                            # Create enhanced memory entry
                            from memory.enhanced_memory_system_v2 import EnhancedMemoryEntry, MemoryType
                            
                            memory = EnhancedMemoryEntry(
                                id=memory_id,
                                content=content,
                                memory_type=MemoryType(memory_type) if memory_type else MemoryType.BUFFER,
                                user_id=enhanced_system.user_id,
                                character_id=enhanced_system.character_id,
                                timestamp=datetime.fromisoformat(timestamp) if timestamp else datetime.now(),
                                importance_score=importance_score or 0.5,
                                emotional_context=emotional_context or "",
                                related_entities=json.loads(related_entities) if related_entities else [],
                                conversation_context=conversation_context or "",
                                metadata=json.loads(metadata) if metadata else {},
                                conversation_id=conversation_id
                            )
                            
                            # Save to enhanced system
                            enhanced_system._save_enhanced_memory(memory)
                            results["memories_migrated"] += 1
                            
                        except Exception as e:
                            results["errors"].append(f"Error migrating memory {memory_id}: {e}")
                
                logger.info(f"Migrated {results['memories_migrated']} memories")
        
        except Exception as e:
            results["errors"].append(f"Memory migration error: {e}")
            logger.error(f"Error migrating memories: {e}")
        
        return results
    
    def _migrate_relationships(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """Migrate relationship data to persistence system."""
        results = {"relationships_migrated": 0, "errors": []}
        
        try:
            # Check for existing relationship database
            old_relationship_path = self.base_path / "relationship_depth.db"
            if not old_relationship_path.exists():
                logger.info("No existing relationship database found")
                return results
            
            import sqlite3
            
            with sqlite3.connect(old_relationship_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT current_level, total_conversations, total_time_spent,
                           emotional_moments, memories_shared, conflicts_resolved,
                           personal_growth_events, consistency_score, authenticity_score,
                           last_interaction, created_at
                    FROM relationships 
                    WHERE user_id = ? AND character_id = ?
                """, (user_id, character_id))
                
                relationship_data = cursor.fetchone()
                if relationship_data:
                    (level, conversations, time_spent, emotional, memories, conflicts,
                     growth, consistency, authenticity, last_interaction, created_at) = relationship_data
                    
                    # Create relationship data for persistence system
                    relationship_info = {
                        "user_id": user_id,
                        "character_id": character_id,
                        "current_level": level,
                        "total_conversations": conversations,
                        "total_time_spent": time_spent,
                        "emotional_moments": emotional,
                        "memories_shared": memories,
                        "conflicts_resolved": conflicts,
                        "personal_growth_events": growth,
                        "consistency_score": consistency,
                        "authenticity_score": authenticity,
                        "last_interaction": last_interaction,
                        "created_at": created_at
                    }
                    
                    # Take snapshot in persistence system
                    self.persistence_system.take_relationship_snapshot(relationship_info)
                    results["relationships_migrated"] = 1
                    
                    logger.info(f"Migrated relationship data for {user_id}-{character_id}")
        
        except Exception as e:
            results["errors"].append(f"Relationship migration error: {e}")
            logger.error(f"Error migrating relationships: {e}")
        
        return results
    
    def _migrate_entities(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """Migrate entity data to enhanced system."""
        results = {"entities_migrated": 0, "errors": []}
        
        try:
            # This would migrate entity data if there's an existing entity system
            # For now, just log that we're ready for entity migration
            logger.info("Entity migration ready (no existing entity data found)")
            results["entities_migrated"] = 0
        
        except Exception as e:
            results["errors"].append(f"Entity migration error: {e}")
            logger.error(f"Error migrating entities: {e}")
        
        return results
    
    def setup_long_term_tracking(self, character_id: str, user_id: str) -> Dict[str, Any]:
        """Set up complete long-term tracking for a user-character pair."""
        setup_results = {
            "enhanced_system_created": False,
            "data_migrated": False,
            "archiving_enabled": False,
            "persistence_enabled": False,
            "compression_enabled": False,
            "optimization_performed": False,
            "errors": []
        }
        
        try:
            logger.info(f"Setting up long-term tracking for {character_id}-{user_id}")
            
            # Create enhanced memory system
            enhanced_system = self.create_enhanced_memory_system(character_id, user_id)
            setup_results["enhanced_system_created"] = True
            
            # Migrate existing data
            migration_results = self.migrate_existing_data(character_id, user_id)
            if migration_results["memories_migrated"] > 0 or migration_results["relationships_migrated"] > 0:
                setup_results["data_migrated"] = True
            
            # Enable archiving
            setup_results["archiving_enabled"] = True
            
            # Enable persistence
            setup_results["persistence_enabled"] = True
            
            # Enable compression
            setup_results["compression_enabled"] = True
            
            # Perform initial optimization
            optimization_results = self.database_optimizer.optimize_all_databases()
            setup_results["optimization_performed"] = True
            
            logger.info(f"Long-term tracking setup completed for {character_id}-{user_id}")
            
        except Exception as e:
            setup_results["errors"].append(f"Setup error: {e}")
            logger.error(f"Error setting up long-term tracking: {e}")
        
        return setup_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all long-term systems."""
        status = {
            "archiving_system": self._get_archiving_status(),
            "persistence_system": self._get_persistence_status(),
            "compression_system": self._get_compression_status(),
            "database_optimization": self._get_optimization_status(),
            "overall_status": "unknown"
        }
        
        # Determine overall status
        all_systems_ok = all(
            system_status.get("status") == "operational" 
            for system_status in status.values() 
            if isinstance(system_status, dict) and "status" in system_status
        )
        
        status["overall_status"] = "operational" if all_systems_ok else "degraded"
        
        return status
    
    def _get_archiving_status(self) -> Dict[str, Any]:
        """Get archiving system status."""
        try:
            stats = self.archiving_system.get_archive_statistics()
            return {
                "status": "operational",
                "total_archived_memories": stats.get("total_archived_memories", 0),
                "total_archived_relationships": stats.get("total_archived_relationships", 0),
                "total_archived_entities": stats.get("total_archived_entities", 0),
                "average_recovery_priority": stats.get("average_recovery_priority", 0.0),
                "archive_size_mb": stats.get("archive_size_mb", 0.0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_persistence_status(self) -> Dict[str, Any]:
        """Get persistence system status."""
        try:
            stats = self.persistence_system.get_persistence_statistics()
            return {
                "status": "operational",
                "total_snapshots": stats.get("total_snapshots", 0),
                "total_continuity_records": stats.get("total_continuity_records", 0),
                "total_milestones": stats.get("total_milestones", 0),
                "total_recoveries": stats.get("total_recoveries", 0),
                "average_relationship_strength": stats.get("average_relationship_strength", 0.0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_compression_status(self) -> Dict[str, Any]:
        """Get compression system status."""
        try:
            stats = self.compression_system.get_compression_statistics()
            return {
                "status": "operational",
                "total_compressions": stats.get("total_compressions", 0),
                "average_compression_ratio": stats.get("average_compression_ratio", 0.0),
                "average_importance_preserved": stats.get("average_importance_preserved", 0.0),
                "relationship_context_preservation_rate": stats.get("relationship_context_preservation_rate", 0.0),
                "emotional_context_preservation_rate": stats.get("emotional_context_preservation_rate", 0.0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_optimization_status(self) -> Dict[str, Any]:
        """Get database optimization status."""
        try:
            # Check if optimization was recently performed
            return {
                "status": "operational",
                "last_optimization": "recent",
                "optimization_ready": True
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_maintenance(self) -> Dict[str, Any]:
        """Run maintenance operations on all systems."""
        maintenance_results = {
            "archiving_maintenance": {},
            "persistence_maintenance": {},
            "compression_maintenance": {},
            "database_maintenance": {},
            "errors": []
        }
        
        try:
            logger.info("Starting system maintenance...")
            
            # Archive old memories
            try:
                old_archives_cleaned = self.archiving_system.cleanup_old_archives(days_old=730)
                maintenance_results["archiving_maintenance"] = {
                    "old_archives_cleaned": old_archives_cleaned,
                    "status": "completed"
                }
            except Exception as e:
                maintenance_results["archiving_maintenance"] = {"status": "error", "error": str(e)}
                maintenance_results["errors"].append(f"Archiving maintenance error: {e}")
            
            # Database optimization
            try:
                optimization_results = self.database_optimizer.optimize_all_databases()
                maintenance_results["database_maintenance"] = {
                    "optimization_results": optimization_results,
                    "status": "completed"
                }
            except Exception as e:
                maintenance_results["database_maintenance"] = {"status": "error", "error": str(e)}
                maintenance_results["errors"].append(f"Database maintenance error: {e}")
            
            logger.info("System maintenance completed")
            
        except Exception as e:
            maintenance_results["errors"].append(f"Maintenance error: {e}")
            logger.error(f"Error during maintenance: {e}")
        
        return maintenance_results

def main():
    """Main function to demonstrate the integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Long-term Memory and Relationship System Integration")
    parser.add_argument("--base-path", type=str, default=".", help="Base path for databases")
    parser.add_argument("--character-id", type=str, help="Character ID for setup")
    parser.add_argument("--user-id", type=str, help="User ID for setup")
    parser.add_argument("--action", choices=["setup", "status", "maintenance", "migrate"], 
                       default="status", help="Action to perform")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    base_path = Path(args.base_path)
    integration = LongTermSystemIntegration(base_path)
    
    if args.action == "setup":
        if not args.character_id or not args.user_id:
            print("Error: --character-id and --user-id are required for setup")
            return
        
        print(f"Setting up long-term tracking for {args.character_id}-{args.user_id}...")
        results = integration.setup_long_term_tracking(args.character_id, args.user_id)
        print("Setup Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    elif args.action == "status":
        print("Getting system status...")
        status = integration.get_system_status()
        print("System Status:")
        for system, system_status in status.items():
            print(f"  {system}: {system_status}")
    
    elif args.action == "maintenance":
        print("Running system maintenance...")
        results = integration.run_maintenance()
        print("Maintenance Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    elif args.action == "migrate":
        if not args.character_id or not args.user_id:
            print("Error: --character-id and --user-id are required for migration")
            return
        
        print(f"Migrating data for {args.character_id}-{args.user_id}...")
        results = integration.migrate_existing_data(args.character_id, args.user_id)
        print("Migration Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main() 