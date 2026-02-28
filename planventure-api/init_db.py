#!/usr/bin/env python3
"""
Database initialization script for PlanVenture API.

This script creates all database tables defined in the models.
Run this script to set up the database before starting the application.
"""

import os
from app import app, db
from models import User, Trip

def init_database():
    """Initialize the database and create all tables."""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify the database connection
            with db.engine.connect() as connection:
                tables = db.inspect(db.engine).get_table_names()
                print(f"📋 Created tables: {', '.join(tables)}")
                
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            raise

def drop_database():
    """Drop all database tables."""
    with app.app_context():
        try:
            db.drop_all()
            print("🗑️  All database tables dropped successfully!")
        except Exception as e:
            print(f"❌ Error dropping database: {str(e)}")
            raise

def reset_database():
    """Drop and recreate all database tables."""
    print("🔄 Resetting database...")
    drop_database()
    init_database()
    print("✅ Database reset complete!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        if action == "init":
            init_database()
        elif action == "drop":
            drop_database()
        elif action == "reset":
            reset_database()
        else:
            print("Usage: python init_db.py [init|drop|reset]")
            print("  init  - Create all database tables")
            print("  drop  - Drop all database tables") 
            print("  reset - Drop and recreate all database tables")
            sys.exit(1)
    else:
        # Default action is to initialize
        init_database()