#!/usr/bin/env python3
"""
Temporal Event Tracking System for Enhanced Memory

This system adds sophisticated temporal parsing capabilities to track future events,
convert relative dates to absolute dates, and maintain contextual event references.
"""

import re
import json
import sqlite3
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EventStatus(Enum):
    PLANNED = "planned"
    HAPPENING = "happening" 
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class TemporalEvent:
    """Represents an event with full temporal and contextual awareness."""
    id: str
    user_id: str
    character_id: str
    event_description: str
    original_reference: str  # "tomorrow", "next week", etc.
    parsed_date: Optional[date]
    date_confidence: float  # 0.0 to 1.0
    status: EventStatus
    created_at: datetime
    context_before: str  # What was said before mentioning event
    context_after: str   # What was said after mentioning event
    followup_comments: List[Dict[str, Any]]  # All future references to this event
    metadata: Dict[str, Any]

class TemporalEventSystem:
    """Advanced temporal event tracking with sophisticated date parsing."""
    
    def __init__(self, character_id: str, user_id: str, db_path: str = "temporal_events.db"):
        self.character_id = character_id
        self.user_id = user_id
        self.db_path = Path(db_path)
        self._init_database()
        
        # Comprehensive temporal patterns
        self.temporal_patterns = {
            # Today variations
            "today": lambda base: base,
            "tonight": lambda base: base,
            "this evening": lambda base: base,
            "this afternoon": lambda base: base,
            "this morning": lambda base: base,
            
            # Tomorrow variations
            "tomorrow": lambda base: base + timedelta(days=1),
            "tomorrow morning": lambda base: base + timedelta(days=1),
            "tomorrow afternoon": lambda base: base + timedelta(days=1),
            "tomorrow evening": lambda base: base + timedelta(days=1),
            "tomorrow night": lambda base: base + timedelta(days=1),
            
            # Week references
            "next week": lambda base: base + timedelta(weeks=1),
            "this week": lambda base: base,
            "next month": lambda base: base + timedelta(days=30),
            "this month": lambda base: base,
            
            # Specific day references
            "monday": lambda base: self._next_weekday(base, 0),
            "tuesday": lambda base: self._next_weekday(base, 1),
            "wednesday": lambda base: self._next_weekday(base, 2),
            "thursday": lambda base: self._next_weekday(base, 3),
            "friday": lambda base: self._next_weekday(base, 4),
            "saturday": lambda base: self._next_weekday(base, 5),
            "sunday": lambda base: self._next_weekday(base, 6),
        }
        
        # Event detection patterns - comprehensive list
        self.event_patterns = [
            r'\b(I have|I\'ve got|I\'m going to|I will|I\'ll|I plan to|I need to|I\'m planning|my)\s+(.+?)\s+(tomorrow|next week|next month|on \w+|in \d+ days?|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(tomorrow|next week|next month|monday|tuesday|wednesday|thursday|friday|saturday|sunday|in \d+ days?)\s+(I have|I\'ve got|I\'m going to|I will|I\'ll|I plan to|I need to|is my|there\'s)\s+(.+?)\b',
            r'\b(my|the)\s+(meeting|appointment|interview|date|event|party|trip|vacation|wedding|birthday|graduation|presentation|exam|test|surgery|flight|concert)\s+(is|will be|happens)\s+(tomorrow|next week|next month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
        ]

    def _init_database(self):
        """Initialize temporal events database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temporal_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    event_description TEXT NOT NULL,
                    original_reference TEXT NOT NULL,
                    parsed_date TEXT,
                    date_confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    context_before TEXT,
                    context_after TEXT,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_followups (
                    id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    comment_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES temporal_events (id)
                )
            """)
            
            conn.commit()

    def parse_and_track_events(self, message: str, conversation_context: str = "") -> List[TemporalEvent]:
        """Main method: Parse message for temporal events and track them."""
        events = []
        base_date = date.today()
        
        for pattern in self.event_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                event = self._process_event_match(match, message, conversation_context, base_date)
                if event:
                    events.append(event)
                    self._save_event(event)
        
        return events

    def _process_event_match(self, match, message: str, context: str, base_date: date) -> Optional[TemporalEvent]:
        """Process a regex match into a TemporalEvent."""
        # Extract components
        original_ref = self._extract_temporal_reference(match.group())
        event_desc = self._extract_event_description(match.group())
        
        if not original_ref or not event_desc:
            return None
        
        # Parse temporal reference
        parsed_date, confidence = self._parse_temporal_reference(original_ref, base_date)
        
        return TemporalEvent(
            id=self._generate_event_id(event_desc, original_ref),
            user_id=self.user_id,
            character_id=self.character_id,
            event_description=event_desc,
            original_reference=original_ref,
            parsed_date=parsed_date,
            date_confidence=confidence,
            status=EventStatus.PLANNED,
            created_at=datetime.now(),
            context_before=context[-200:] if context else "",
            context_after="",
            followup_comments=[],
            metadata={
                "original_message": message,
                "match_text": match.group(),
                "conversation_timestamp": datetime.now().isoformat()
            }
        )

    def _parse_temporal_reference(self, reference: str, base_date: date) -> Tuple[Optional[date], float]:
        """Convert relative temporal reference to absolute date."""
        ref_lower = reference.lower().strip()
        
        # Direct pattern matching
        if ref_lower in self.temporal_patterns:
            try:
                parsed_date = self.temporal_patterns[ref_lower](base_date)
                return parsed_date, 0.9
            except Exception:
                pass
        
        # Numeric patterns (in X days/weeks)
        numeric_match = re.search(r'in (\d+) (days?|weeks?|months?)', ref_lower)
        if numeric_match:
            try:
                num = int(numeric_match.group(1))
                unit = numeric_match.group(2).rstrip('s')  # Remove plural 's'
                
                if unit == "day":
                    return base_date + timedelta(days=num), 0.95
                elif unit == "week":
                    return base_date + timedelta(weeks=num), 0.95
                elif unit == "month":
                    return base_date + timedelta(days=num * 30), 0.85  # Approximate
            except Exception:
                pass
        
        return None, 0.0

    def _next_weekday(self, base_date: date, weekday: int) -> date:
        """Get next occurrence of weekday (0=Monday, 6=Sunday)."""
        days_ahead = weekday - base_date.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return base_date + timedelta(days=days_ahead)

    def get_event_timeline_for_character(self, days_lookback: int = 7, days_lookahead: int = 30) -> str:
        """Generate timeline context for character to reference past and future events."""
        current_date = date.today()
        start_date = current_date - timedelta(days=days_lookback)
        end_date = current_date + timedelta(days=days_lookahead)
        
        events = self._get_events_in_range(start_date, end_date)
        
        if not events:
            return ""
        
        timeline = ["## 📅 TEMPORAL EVENT AWARENESS:"]
        
        for event in events:
            if not event.parsed_date:
                continue
                
            days_diff = (event.parsed_date - current_date).days
            
            # Determine time context
            if days_diff < -1:
                time_desc = f"{abs(days_diff)} days ago"
                status_emoji = "✅" if event.status == EventStatus.COMPLETED else "❌"
            elif days_diff == -1:
                time_desc = "yesterday"
                status_emoji = "✅" if event.status == EventStatus.COMPLETED else "❌"
            elif days_diff == 0:
                time_desc = "TODAY"
                status_emoji = "🔥"
            elif days_diff == 1:
                time_desc = "TOMORROW"
                status_emoji = "⚡"
            else:
                time_desc = f"in {days_diff} days ({event.parsed_date.strftime('%B %d')})"
                status_emoji = "📅"
            
            # Add event to timeline
            timeline.append(f"{status_emoji} **{event.event_description}** - {time_desc}")
            timeline.append(f"   Originally mentioned as: '{event.original_reference}'")
            
            if event.followup_comments:
                timeline.append(f"   Followup comments: {len(event.followup_comments)} references")
        
        return "\n".join(timeline)

    def add_followup_reference(self, event_description: str, new_comment: str, comment_type: str = "update") -> bool:
        """Add a followup comment when an event is referenced again."""
        # Find matching event
        event = self._find_event_by_description(event_description)
        if not event:
            return False
        
        # Add followup
        followup = {
            "comment": new_comment,
            "type": comment_type,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO event_followups (id, event_id, comment, comment_type, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (f"{event.id}_{datetime.now().timestamp()}", event.id, new_comment, comment_type, followup["timestamp"]))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding followup: {e}")
            return False

    def _extract_temporal_reference(self, text: str) -> Optional[str]:
        """Extract temporal reference from matched text."""
        temporal_keywords = [
            'tomorrow', 'today', 'tonight', 'next week', 'next month', 'this week', 'this month',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'next monday', 'next tuesday', 'next wednesday', 'next thursday',
            'next friday', 'next saturday', 'next sunday'
        ]
        
        text_lower = text.lower()
        
        # Check for exact matches
        for keyword in temporal_keywords:
            if keyword in text_lower:
                return keyword
        
        # Check for numeric patterns
        numeric = re.search(r'in \d+ (days?|weeks?|months?)', text_lower)
        if numeric:
            return numeric.group()
        
        return None

    def _extract_event_description(self, text: str) -> Optional[str]:
        """Extract clean event description."""
        # Remove temporal references and common prefixes
        clean = re.sub(r'\b(tomorrow|next week|next month|today|tonight|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', '', text, flags=re.IGNORECASE)
        clean = re.sub(r'\b(I have|I\'ve got|I\'m going to|I will|I\'ll|I plan to|I need to|is|will be|my|the)\b', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean if clean and len(clean) > 3 else None

    def _save_event(self, event: TemporalEvent):
        """Save event to database."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO temporal_events 
                    (id, user_id, character_id, event_description, original_reference,
                     parsed_date, date_confidence, status, created_at, context_before, 
                     context_after, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id, event.user_id, event.character_id, event.event_description,
                    event.original_reference, 
                    event.parsed_date.isoformat() if event.parsed_date else None,
                    event.date_confidence, event.status.value, event.created_at.isoformat(),
                    event.context_before, event.context_after, json.dumps(event.metadata)
                ))
                conn.commit()
        except Exception as e:
            print(f"Error saving event: {e}")

    def _get_events_in_range(self, start_date: date, end_date: date) -> List[TemporalEvent]:
        """Get events within date range."""
        events = []
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM temporal_events 
                    WHERE user_id = ? AND character_id = ? 
                    AND parsed_date BETWEEN ? AND ?
                    ORDER BY parsed_date
                """, (self.user_id, self.character_id, start_date.isoformat(), end_date.isoformat()))
                
                for row in cursor.fetchall():
                    event = self._row_to_event(row)
                    if event:
                        events.append(event)
        except Exception as e:
            print(f"Error fetching events: {e}")
        
        return events

    def _find_event_by_description(self, description: str) -> Optional[TemporalEvent]:
        """Find event by description similarity."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM temporal_events 
                    WHERE user_id = ? AND character_id = ? 
                    AND event_description LIKE ?
                """, (self.user_id, self.character_id, f"%{description}%"))
                
                row = cursor.fetchone()
                return self._row_to_event(row) if row else None
        except Exception:
            return None

    def _row_to_event(self, row) -> Optional[TemporalEvent]:
        """Convert database row to TemporalEvent."""
        try:
            return TemporalEvent(
                id=row[0],
                user_id=row[1],
                character_id=row[2],
                event_description=row[3],
                original_reference=row[4],
                parsed_date=date.fromisoformat(row[5]) if row[5] else None,
                date_confidence=row[6],
                status=EventStatus(row[7]),
                created_at=datetime.fromisoformat(row[8]),
                context_before=row[9] or "",
                context_after=row[10] or "",
                followup_comments=[],
                metadata=json.loads(row[11]) if row[11] else {}
            )
        except Exception as e:
            print(f"Error converting row: {e}")
            return None

    def _generate_event_id(self, description: str, reference: str) -> str:
        """Generate unique event ID."""
        import hashlib
        base = f"{self.user_id}_{description}_{reference}_{datetime.now().timestamp()}"
        return hashlib.md5(base.encode()).hexdigest()[:16]


# Demo function
def demo_temporal_tracking():
    """Demonstrate advanced temporal event tracking."""
    system = TemporalEventSystem("evelyn_chen", "ed_fornieles")
    
    # Test various temporal references
    test_messages = [
        "I have a job interview tomorrow at 2 PM",
        "Next week I'm going on vacation to Spain with my family", 
        "My dentist appointment is on Friday morning",
        "In 3 days I need to submit my final project for university",
        "My sister's wedding is next month",
        "I'm worried about my presentation tomorrow"
    ]
    
    print("🧠 TEMPORAL EVENT PARSING DEMO:")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\n📝 Processing: '{message}'")
        events = system.parse_and_track_events(message)
        
        for event in events:
            print(f"   ✅ Event: {event.event_description}")
            print(f"   📅 Reference: '{event.original_reference}' → {event.parsed_date}")
            print(f"   🎯 Confidence: {event.date_confidence:.1%}")
    
    # Show timeline
    print(f"\n{system.get_event_timeline_for_character()}")

if __name__ == "__main__":
    demo_temporal_tracking() 