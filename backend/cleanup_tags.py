#!/usr/bin/env python3
"""
Script to clean up malformed tags in the Brainrot database.
Fixes tags that were stored as JSON-encoded strings.
"""

import json
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "data" / "brainrot.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

def clean_tag(tag):
    """Clean a single malformed tag."""
    if not tag:
        return None
    
    # Remove leading/trailing whitespace
    tag = tag.strip()
    
    # Check if it's a malformed tag (starts with [" or just ")
    if tag.startswith('[') or tag.startswith('"'):
        # Remove brackets, quotes, backslashes
        cleaned = re.sub(r'[\[\]"\\]', '', tag)
        cleaned = cleaned.strip()
        if cleaned:
            return cleaned.lower()
    else:
        # Already clean, just normalize to lowercase
        return tag.lower()
    
    return None

def cleanup_tags():
    """Main cleanup function."""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"Connecting to database: {DB_PATH}")
    
    try:
        # Get all contexts
        result = session.execute(text("SELECT id, key, tags FROM contexts"))
        contexts = result.fetchall()
        
        print(f"Found {len(contexts)} contexts to check")
        
        fixed_count = 0
        already_clean = 0
        
        for ctx_id, ctx_key, tags_json in contexts:
            if not tags_json:
                continue
            
            # Parse the JSON tags
            try:
                tags = json.loads(tags_json) if isinstance(tags_json, str) else tags_json
            except json.JSONDecodeError:
                print(f"  ⚠️  Failed to parse tags for '{ctx_key}'")
                continue
            
            if not isinstance(tags, list):
                continue
            
            # Clean each tag
            clean_tags = []
            needs_fix = False
            
            for tag in tags:
                # Check if this tag needs cleaning
                if tag and (tag.startswith('[') or tag.startswith('"') or tag != tag.lower()):
                    needs_fix = True
                    cleaned = clean_tag(tag)
                    if cleaned and cleaned not in clean_tags:
                        clean_tags.append(cleaned)
                elif tag:
                    # Already clean but normalize case
                    normalized = tag.lower()
                    if normalized != tag:
                        needs_fix = True
                    if normalized not in clean_tags:
                        clean_tags.append(normalized)
            
            # Update if needed
            if needs_fix:
                # Update the tags
                new_tags_json = json.dumps(clean_tags)
                session.execute(
                    text("UPDATE contexts SET tags = :tags WHERE id = :id"),
                    {"tags": new_tags_json, "id": ctx_id}
                )
                fixed_count += 1
                print(f"  ✅ Fixed '{ctx_key}': {tags} → {clean_tags}")
            else:
                already_clean += 1
        
        # Commit changes
        session.commit()
        
        print(f"\n📊 Summary:")
        print(f"  - Fixed: {fixed_count} contexts")
        print(f"  - Already clean: {already_clean} contexts")
        print(f"  - Total: {len(contexts)} contexts")
        
        # Show unique tags after cleanup
        result = session.execute(text("SELECT tags FROM contexts WHERE tags IS NOT NULL"))
        all_tags = set()
        for (tags_json,) in result:
            try:
                tags = json.loads(tags_json) if isinstance(tags_json, str) else tags_json
                if isinstance(tags, list):
                    all_tags.update(tags)
            except:
                pass
        
        print(f"\n📌 Unique tags after cleanup: {len(all_tags)}")
        print(f"  {sorted(all_tags)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("🧹 Starting tag cleanup...\n")
    cleanup_tags()
    print("\n✨ Cleanup complete!")