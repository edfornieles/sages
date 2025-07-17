#!/usr/bin/env python3
"""
IP Geolocation & Timezone Detection System

This system provides:
- Real-time IP geolocation detection
- Timezone-aware temporal calculations  
- Location context for characters
- Privacy-respectful location tracking
"""

import json
import requests
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import pytz
import re

@dataclass
class UserLocationData:
    """Complete user location and timezone information."""
    user_id: str
    ip_address: str
    country: str
    country_code: str
    region: str
    city: str
    timezone: str
    latitude: float
    longitude: float
    isp: str
    detected_at: datetime
    last_updated: datetime
    accuracy_score: float  # 0.0 to 1.0
    metadata: Dict[str, Any]

@dataclass
class TimezoneAwareEvent:
    """Event with full timezone awareness."""
    event_id: str
    user_local_time: datetime
    server_time: datetime
    timezone: str
    original_reference: str  # "tomorrow", "next week"
    parsed_local_date: date
    confidence: float

class IPGeolocationSystem:
    """Advanced IP-based geolocation and timezone detection."""
    
    def __init__(self, db_path: str = "memory_new/db/user_locations.db"):
        self.db_path = Path(db_path)
        self._init_database()
        
        # Multiple geolocation services for redundancy
        self.geolocation_services = [
            {
                "name": "ipapi",
                "url": "http://ip-api.com/json/{ip}",
                "free": True,
                "rate_limit": "45/minute"
            },
            {
                "name": "ipinfo",
                "url": "https://ipinfo.io/{ip}/json",
                "free": True,
                "rate_limit": "50000/month"
            },
            {
                "name": "geojs", 
                "url": "https://get.geojs.io/v1/ip/geo/{ip}.json",
                "free": True,
                "rate_limit": "unlimited"
            }
        ]

    def _init_database(self):
        """Initialize user location database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # User locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_locations (
                    user_id TEXT PRIMARY KEY,
                    ip_address TEXT NOT NULL,
                    country TEXT NOT NULL,
                    country_code TEXT NOT NULL,
                    region TEXT NOT NULL,
                    city TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    isp TEXT,
                    detected_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    accuracy_score REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            # IP lookup cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ip_cache (
                    ip_address TEXT PRIMARY KEY,
                    location_data TEXT NOT NULL,
                    cached_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)
            
            conn.commit()

    def detect_user_location(self, user_id: str, ip_address: str, force_refresh: bool = False) -> Optional[UserLocationData]:
        """Detect user location from IP address with caching."""
        
        # Check if we already have recent data for this user
        if not force_refresh:
            existing_data = self._get_cached_user_location(user_id)
            if existing_data and self._is_location_data_fresh(existing_data):
                return existing_data
        
        # Check IP cache first
        cached_ip_data = self._get_cached_ip_data(ip_address)
        if cached_ip_data and not force_refresh:
            location_data = self._create_user_location_from_cache(user_id, ip_address, cached_ip_data)
            self._save_user_location(location_data)
            return location_data
        
        # Fetch fresh geolocation data
        geo_data = self._fetch_geolocation_data(ip_address)
        if not geo_data:
            return None
        
        # Create user location data
        location_data = self._create_user_location_data(user_id, ip_address, geo_data)
        
        # Cache the results
        self._cache_ip_data(ip_address, geo_data)
        self._save_user_location(location_data)
        
        return location_data

    def _fetch_geolocation_data(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Fetch geolocation data from multiple services."""
        
        # Skip private/local IPs
        if self._is_private_ip(ip_address):
            return self._get_default_location_data()
        
        # Try each service until one works
        for service in self.geolocation_services:
            try:
                url = service["url"].format(ip=ip_address)
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Normalize data format based on service
                    normalized = self._normalize_geolocation_data(data, service["name"])
                    if normalized:
                        normalized["source"] = service["name"]
                        return normalized
                        
            except Exception as e:
                print(f"Geolocation service {service['name']} failed: {e}")
                continue
        
        return None

    def _normalize_geolocation_data(self, data: Dict[str, Any], service_name: str) -> Optional[Dict[str, Any]]:
        """Normalize different geolocation service formats."""
        
        try:
            if service_name == "ipapi":
                return {
                    "country": data.get("country", "Unknown"),
                    "country_code": data.get("countryCode", "XX"),
                    "region": data.get("regionName", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "timezone": data.get("timezone", "UTC"),
                    "latitude": float(data.get("lat", 0.0)),
                    "longitude": float(data.get("lon", 0.0)),
                    "isp": data.get("isp", "Unknown"),
                    "accuracy": 0.9 if data.get("status") == "success" else 0.3
                }
                
            elif service_name == "ipinfo":
                location = data.get("loc", "0,0").split(",")
                return {
                    "country": data.get("country", "Unknown"),
                    "country_code": data.get("country", "XX"),
                    "region": data.get("region", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "timezone": data.get("timezone", "UTC"),
                    "latitude": float(location[0]) if len(location) > 0 else 0.0,
                    "longitude": float(location[1]) if len(location) > 1 else 0.0,
                    "isp": data.get("org", "Unknown"),
                    "accuracy": 0.85
                }
                
            elif service_name == "geojs":
                return {
                    "country": data.get("country", "Unknown"),
                    "country_code": data.get("country_code", "XX"),
                    "region": data.get("region", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "timezone": data.get("timezone", "UTC"),
                    "latitude": float(data.get("latitude", 0.0)),
                    "longitude": float(data.get("longitude", 0.0)),
                    "isp": data.get("organization_name", "Unknown"),
                    "accuracy": 0.8
                }
                
        except Exception as e:
            print(f"Error normalizing {service_name} data: {e}")
            
        return None

    def _create_user_location_data(self, user_id: str, ip_address: str, geo_data: Dict[str, Any]) -> UserLocationData:
        """Create UserLocationData from geolocation response."""
        
        return UserLocationData(
            user_id=user_id,
            ip_address=ip_address,
            country=geo_data.get("country", "Unknown"),
            country_code=geo_data.get("country_code", "XX"),
            region=geo_data.get("region", "Unknown"),
            city=geo_data.get("city", "Unknown"),
            timezone=geo_data.get("timezone", "UTC"),
            latitude=geo_data.get("latitude", 0.0),
            longitude=geo_data.get("longitude", 0.0),
            isp=geo_data.get("isp", "Unknown"),
            detected_at=datetime.now(),
            last_updated=datetime.now(),
            accuracy_score=geo_data.get("accuracy", 0.5),
            metadata={
                "source": geo_data.get("source", "unknown"),
                "detection_method": "ip_geolocation"
            }
        )

    def get_user_local_time(self, user_id: str) -> Tuple[datetime, str]:
        """Get user's current local time and timezone."""
        
        location_data = self._get_cached_user_location(user_id)
        
        if location_data and location_data.timezone:
            try:
                user_tz = pytz.timezone(location_data.timezone)
                local_time = datetime.now(user_tz)
                return local_time, location_data.timezone
            except Exception:
                pass
        
        # Fallback to UTC
        utc_time = datetime.now(pytz.UTC)
        return utc_time, "UTC"

    def convert_relative_date_with_timezone(self, user_id: str, relative_reference: str) -> Optional[TimezoneAwareEvent]:
        """Convert relative date reference to timezone-aware event."""
        
        user_local_time, timezone = self.get_user_local_time(user_id)
        user_local_date = user_local_time.date()
        
        # Parse temporal reference using user's local date
        parsed_date, confidence = self._parse_temporal_reference(relative_reference, user_local_date)
        
        if not parsed_date:
            return None
        
        return TimezoneAwareEvent(
            event_id=f"{user_id}_{relative_reference}_{datetime.now().timestamp()}",
            user_local_time=user_local_time,
            server_time=datetime.now(),
            timezone=timezone,
            original_reference=relative_reference,
            parsed_local_date=parsed_date,
            confidence=confidence
        )

    def generate_location_context_for_character(self, user_id: str) -> str:
        """Generate location context for character awareness."""
        
        location_data = self._get_cached_user_location(user_id)
        
        if not location_data:
            return ""
        
        user_local_time, _ = self.get_user_local_time(user_id)
        
        # Generate time-of-day context
        hour = user_local_time.hour
        if 5 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 17:
            time_period = "afternoon"
        elif 17 <= hour < 21:
            time_period = "evening"
        else:
            time_period = "night"
        
        context_parts = [
            f"## 🌍 USER LOCATION CONTEXT:",
            f"- **Location**: {location_data.city}, {location_data.region}, {location_data.country}",
            f"- **Local Time**: {user_local_time.strftime('%I:%M %p')} ({time_period})",
            f"- **Timezone**: {location_data.timezone}",
            f"- **Date**: {user_local_time.strftime('%A, %B %d, %Y')}"
        ]
        
        return "\n".join(context_parts)

    def _parse_temporal_reference(self, reference: str, base_date: date) -> Tuple[Optional[date], float]:
        """Parse temporal reference using base date."""
        
        ref_lower = reference.lower().strip()
        
        temporal_patterns = {
            "today": lambda d: d,
            "tonight": lambda d: d,
            "tomorrow": lambda d: d + timedelta(days=1),
            "next week": lambda d: d + timedelta(weeks=1),
            "next month": lambda d: d + timedelta(days=30),
            "monday": lambda d: self._next_weekday(d, 0),
            "tuesday": lambda d: self._next_weekday(d, 1),
            "wednesday": lambda d: self._next_weekday(d, 2),
            "thursday": lambda d: self._next_weekday(d, 3),
            "friday": lambda d: self._next_weekday(d, 4),
            "saturday": lambda d: self._next_weekday(d, 5),
            "sunday": lambda d: self._next_weekday(d, 6),
        }
        
        if ref_lower in temporal_patterns:
            try:
                parsed_date = temporal_patterns[ref_lower](base_date)
                return parsed_date, 0.9
            except Exception:
                pass
        
        # Numeric patterns
        numeric_match = re.search(r'in (\d+) (days?|weeks?)', ref_lower)
        if numeric_match:
            try:
                num = int(numeric_match.group(1))
                unit = numeric_match.group(2).rstrip('s')
                
                if unit == "day":
                    return base_date + timedelta(days=num), 0.95
                elif unit == "week":
                    return base_date + timedelta(weeks=num), 0.95
            except Exception:
                pass
        
        return None, 0.0

    def _next_weekday(self, base_date: date, weekday: int) -> date:
        """Get next occurrence of weekday (0=Monday, 6=Sunday)."""
        days_ahead = weekday - base_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return base_date + timedelta(days=days_ahead)

    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP is private/local."""
        private_ranges = [
            "127.", "10.", "192.168.", "172.16.", "172.17.", "172.18.", 
            "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", 
            "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", 
            "172.29.", "172.30.", "172.31.", "::1", "localhost"
        ]
        return any(ip_address.startswith(prefix) for prefix in private_ranges)

    def _get_default_location_data(self) -> Dict[str, Any]:
        """Get default location data for private/local IPs."""
        return {
            "country": "Local Network",
            "country_code": "LN",
            "region": "Local",
            "city": "Localhost", 
            "timezone": "UTC",
            "latitude": 0.0,
            "longitude": 0.0,
            "isp": "Local Network",
            "accuracy": 0.1
        }

    def _get_cached_user_location(self, user_id: str) -> Optional[UserLocationData]:
        """Get cached user location data."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_locations WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return UserLocationData(
                        user_id=row[0],
                        ip_address=row[1],
                        country=row[2],
                        country_code=row[3],
                        region=row[4],
                        city=row[5],
                        timezone=row[6],
                        latitude=row[7],
                        longitude=row[8],
                        isp=row[9],
                        detected_at=datetime.fromisoformat(row[10]),
                        last_updated=datetime.fromisoformat(row[11]),
                        accuracy_score=row[12],
                        metadata=json.loads(row[13]) if row[13] else {}
                    )
        except Exception as e:
            print(f"Error getting cached user location: {e}")
            
        return None

    def _save_user_location(self, location_data: UserLocationData):
        """Save user location data to database."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_locations 
                    (user_id, ip_address, country, country_code, region, city, timezone,
                     latitude, longitude, isp, detected_at, last_updated, accuracy_score, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    location_data.user_id, location_data.ip_address, location_data.country,
                    location_data.country_code, location_data.region, location_data.city,
                    location_data.timezone, location_data.latitude, location_data.longitude,
                    location_data.isp, location_data.detected_at.isoformat(),
                    location_data.last_updated.isoformat(), location_data.accuracy_score,
                    json.dumps(location_data.metadata)
                ))
                conn.commit()
        except Exception as e:
            print(f"Error saving user location: {e}")

    def _is_location_data_fresh(self, location_data: UserLocationData, max_age_hours: int = 24) -> bool:
        """Check if location data is still fresh."""
        age = datetime.now() - location_data.last_updated
        return age.total_seconds() < (max_age_hours * 3600)

    def _get_cached_ip_data(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get cached IP geolocation data."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT location_data, expires_at FROM ip_cache 
                    WHERE ip_address = ? AND expires_at > ?
                """, (ip_address, datetime.now().isoformat()))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
        except Exception:
            pass
            
        return None

    def _cache_ip_data(self, ip_address: str, geo_data: Dict[str, Any], cache_hours: int = 24):
        """Cache IP geolocation data."""
        try:
            expires_at = datetime.now() + timedelta(hours=cache_hours)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ip_cache (ip_address, location_data, cached_at, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    ip_address, json.dumps(geo_data), 
                    datetime.now().isoformat(), expires_at.isoformat()
                ))
                conn.commit()
        except Exception as e:
            print(f"Error caching IP data: {e}")

    def _create_user_location_from_cache(self, user_id: str, ip_address: str, cached_data: Dict[str, Any]) -> UserLocationData:
        """Create UserLocationData from cached IP data."""
        return self._create_user_location_data(user_id, ip_address, cached_data)


# Demo function
def demo_geolocation_system():
    """Demonstrate the IP geolocation system."""
    system = IPGeolocationSystem()
    
    print("🌍 IP GEOLOCATION SYSTEM DEMO:")
    print("=" * 50)
    
    # Test with your actual public IP first
    test_user = "ed_fornieles"
    
    # Get public IP
    try:
        response = requests.get("https://httpbin.org/ip", timeout=5)
        current_ip = response.json()["origin"]
        print(f"\n📍 Testing your IP: {current_ip}")
        
        location_data = system.detect_user_location(test_user, current_ip)
        
        if location_data:
            print(f"   ✅ Location: {location_data.city}, {location_data.region}, {location_data.country}")
            print(f"   🕐 Timezone: {location_data.timezone}")
            print(f"   🎯 Accuracy: {location_data.accuracy_score:.1%}")
            
            # Test temporal conversion
            user_time, tz = system.get_user_local_time(test_user)
            print(f"   ⏰ Your Local Time: {user_time.strftime('%Y-%m-%d %I:%M %p')} ({tz})")
            
            # Test "tomorrow" conversion
            tomorrow_event = system.convert_relative_date_with_timezone(test_user, "tomorrow")
            if tomorrow_event:
                print(f"   📅 'Tomorrow' = {tomorrow_event.parsed_local_date}")
                print(f"   🌍 Location Context:")
                context = system.generate_location_context_for_character(test_user)
                print(context)
        else:
            print(f"   ❌ Could not detect location")
            
    except Exception as e:
        print(f"❌ Error getting public IP: {e}")

if __name__ == "__main__":
    demo_geolocation_system() 