#!/usr/bin/env python3
import sqlite3
import json
from pathlib import Path

class AIRAGSystem:
    def __init__(self):
        self.db_path = Path('.ai/rag/knowledge.db')
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS codebase_knowledge (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                content_hash TEXT,
                patterns TEXT,
                fixes TEXT,
                agent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_coordination (
                id INTEGER PRIMARY KEY,
                from_agent TEXT,
                to_agent TEXT,
                message TEXT,
                task_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_knowledge(self, file_path, patterns, fixes, agent):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO codebase_knowledge (file_path, patterns, fixes, agent)
            VALUES (?, ?, ?, ?)
        ''', (file_path, json.dumps(patterns), json.dumps(fixes), agent))
        conn.commit()
        conn.close()
    
    def coordinate_agents(self, from_agent, to_agent, message, task_type):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agent_coordination (from_agent, to_agent, message, task_type)
            VALUES (?, ?, ?, ?)
        ''', (from_agent, to_agent, message, task_type))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    rag = AIRAGSystem()
    print("AI RAG System initialized")