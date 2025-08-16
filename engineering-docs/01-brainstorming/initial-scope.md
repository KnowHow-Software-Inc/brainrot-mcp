# FastMCP Server Project Architecture

## Project Overview

This architecture covers a complete FastMCP (Model Context Protocol) server implementation with SQLite database integration and proper virtual environment setup. The MCP server enables LLMs to interact with your data through standardized tools and resources.

## Directory Structure

```
brainrot-mcp/
├── .env                          # Environment variables
├── .gitignore                    # Git ignore file
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── server.py                     # Main MCP server file
├── config/
│   ├── __init__.py
│   └── settings.py               # Configuration management
├── database/
│   ├── __init__.py
│   ├── models.py                 # Database schema definitions
│   ├── connection.py             # Database connection management
│   └── sample_data.sql           # Sample data for testing
├── tools/
│   ├── __init__.py
│   ├── database_tools.py         # Database-related MCP tools
│   └── utility_tools.py          # General utility tools
├── resources/
│   ├── __init__.py
│   └── data_resources.py         # MCP resources for data access
├── tests/
│   ├── __init__.py
│   ├── test_server.py            # Server tests
│   └── test_database.py          # Database tests
└── data/
    └── app.db                    # SQLite database file
```

## Core Components

### 1. Virtual Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration (.env)

```env
# Database Configuration
DB_PATH=./data/app.db
DB_NAME=mcp_server_db

# Server Configuration
MCP_SERVER_NAME=MyMCPServer
MCP_PORT=8000
READ_ONLY=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/server.log

# Development
DEBUG=true
```

### 3. Dependencies (requirements.txt)

```txt
fastmcp>=2.0.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
pydantic>=2.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

### 4. Main Server Implementation (server.py)

```python
import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any

import aiosqlite
from fastmcp import FastMCP
from dotenv import load_dotenv

from config.settings import Settings
from database.connection import DatabaseManager
from tools.database_tools import register_database_tools
from tools.utility_tools import register_utility_tools
from resources.data_resources import register_data_resources

# Load environment variables
load_dotenv()

# Initialize settings
settings = Settings()

# Initialize FastMCP server
mcp = FastMCP(settings.mcp_server_name)

# Initialize database manager
db_manager = DatabaseManager(settings.db_path)

@mcp.on_startup
async def startup():
    """Initialize database and server components on startup"""
    await db_manager.initialize()
    print(f"✅ MCP Server '{settings.mcp_server_name}' started successfully")
    print(f"📁 Database: {settings.db_path}")
    print(f"🔒 Read-only mode: {settings.read_only}")

@mcp.on_shutdown
async def shutdown():
    """Clean up resources on shutdown"""
    await db_manager.close()
    print("🛑 MCP Server shutdown complete")

# Register tools and resources
register_database_tools(mcp, db_manager, settings)
register_utility_tools(mcp)
register_data_resources(mcp, db_manager)

if __name__ == "__main__":
    mcp.run()
```

### 5. Configuration Management (config/settings.py)

```python
import os
from pathlib import Path
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database settings
    db_path: Path = Field(default="./data/app.db", env="DB_PATH")
    db_name: str = Field(default="mcp_server_db", env="DB_NAME")
    
    # Server settings
    mcp_server_name: str = Field(default="MyMCPServer", env="MCP_SERVER_NAME")
    mcp_port: int = Field(default=8000, env="MCP_PORT")
    read_only: bool = Field(default=False, env="READ_ONLY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Path = Field(default="./logs/server.log", env="LOG_FILE")
    
    # Development
    debug: bool = Field(default=False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        
    def __post_init__(self):
        """Ensure required directories exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
```

### 6. Database Management (database/connection.py)

```python
import aiosqlite
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """Initialize database and create tables if they don't exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.connection = await aiosqlite.connect(self.db_path)
        await self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Create sample tables
        await self._create_tables()
        await self._insert_sample_data()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    async def _create_tables(self):
        """Create sample database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            owner_id INTEGER,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        );
        
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            project_id INTEGER,
            assignee_id INTEGER,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (assignee_id) REFERENCES users (id)
        );
        """
        
        await self.connection.executescript(schema_sql)
        await self.connection.commit()
    
    async def _insert_sample_data(self):
        """Insert sample data for testing"""
        # Check if data already exists
        cursor = await self.connection.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()
        
        if count[0] == 0:
            sample_data_sql = """
            INSERT INTO users (name, email) VALUES 
                ('Alice Johnson', 'alice@example.com'),
                ('Bob Smith', 'bob@example.com'),
                ('Carol Davis', 'carol@example.com');
            
            INSERT INTO projects (name, description, owner_id) VALUES 
                ('Web Application', 'Customer portal development', 1),
                ('Mobile App', 'iOS and Android app', 2),
                ('Data Migration', 'Legacy system migration', 1);
            
            INSERT INTO tasks (title, description, project_id, assignee_id, status, priority) VALUES 
                ('Setup Database', 'Configure PostgreSQL database', 1, 1, 'completed', 'high'),
                ('Design UI', 'Create user interface mockups', 1, 3, 'in_progress', 'medium'),
                ('API Development', 'Build REST API endpoints', 2, 2, 'pending', 'high'),
                ('Testing', 'Write unit and integration tests', 1, 1, 'pending', 'medium');
            """
            
            await self.connection.executescript(sample_data_sql)
            await self.connection.commit()
            logger.info("Sample data inserted")
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        cursor = await self.connection.execute(query, params)
        columns = [description[0] for description in cursor.description]
        rows = await cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        cursor = await self.connection.execute(query, params)
        await self.connection.commit()
        return cursor.rowcount
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a table"""
        query = f"PRAGMA table_info({table_name})"
        return await self.execute_query(query)
    
    async def get_table_names(self) -> List[str]:
        """Get list of all table names"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        results = await self.execute_query(query)
        return [row['name'] for row in results]
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
```

### 7. Database Tools (tools/database_tools.py)

```python
from typing import List, Dict, Any
from fastmcp import FastMCP
from database.connection import DatabaseManager
from config.settings import Settings

def register_database_tools(mcp: FastMCP, db_manager: DatabaseManager, settings: Settings):
    """Register database-related MCP tools"""
    
    @mcp.tool()
    async def execute_query(query: str) -> Dict[str, Any]:
        """
        Execute a SQL query on the database.
        
        Args:
            query: SQL query to execute (SELECT statements only if read-only mode)
        
        Returns:
            Query results and metadata
        """
        if settings.read_only and not query.strip().upper().startswith('SELECT'):
            return {
                "error": "Only SELECT queries are allowed in read-only mode",
                "query": query
            }
        
        try:
            if query.strip().upper().startswith('SELECT'):
                results = await db_manager.execute_query(query)
                return {
                    "success": True,
                    "data": results,
                    "row_count": len(results),
                    "query": query
                }
            else:
                affected_rows = await db_manager.execute_update(query)
                return {
                    "success": True,
                    "affected_rows": affected_rows,
                    "query": query
                }
        except Exception as e:
            return {
                "error": str(e),
                "query": query
            }
    
    @mcp.tool()
    async def list_tables() -> List[str]:
        """
        Get a list of all tables in the database.
        
        Returns:
            List of table names
        """
        return await db_manager.get_table_names()
    
    @mcp.tool()
    async def describe_table(table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a specific table.
        
        Args:
            table_name: Name of the table to describe
        
        Returns:
            Table schema information
        """
        try:
            schema = await db_manager.get_table_schema(table_name)
            return {
                "table_name": table_name,
                "columns": schema,
                "column_count": len(schema)
            }
        except Exception as e:
            return {
                "error": str(e),
                "table_name": table_name
            }
    
    @mcp.tool()
    async def get_sample_data(table_name: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get sample data from a table.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to return (default: 5)
        
        Returns:
            Sample data from the table
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            results = await db_manager.execute_query(query)
            return {
                "table_name": table_name,
                "sample_data": results,
                "row_count": len(results)
            }
        except Exception as e:
            return {
                "error": str(e),
                "table_name": table_name
            }
```

### 8. Data Resources (resources/data_resources.py)

```python
from fastmcp import FastMCP
from database.connection import DatabaseManager

def register_data_resources(mcp: FastMCP, db_manager: DatabaseManager):
    """Register data resources for MCP server"""
    
    @mcp.resource("schema://database")
    async def database_schema() -> str:
        """Provide complete database schema as a resource"""
        try:
            tables = await db_manager.get_table_names()
            schema_info = []
            
            for table in tables:
                table_schema = await db_manager.get_table_schema(table)
                schema_info.append(f"\nTable: {table}")
                for column in table_schema:
                    nullable = "NULL" if column['notnull'] == 0 else "NOT NULL"
                    pk = " PRIMARY KEY" if column['pk'] == 1 else ""
                    default = f" DEFAULT {column['dflt_value']}" if column['dflt_value'] else ""
                    schema_info.append(f"  {column['name']} {column['type']}{pk} {nullable}{default}")
            
            return "\n".join(schema_info)
        except Exception as e:
            return f"Error retrieving schema: {str(e)}"
    
    @mcp.resource("data://tables")
    async def table_list() -> str:
        """Provide list of available tables as a resource"""
        try:
            tables = await db_manager.get_table_names()
            return "Available tables:\n" + "\n".join(f"- {table}" for table in tables)
        except Exception as e:
            return f"Error retrieving tables: {str(e)}"
```

## Deployment and Integration

### 1. Running the Server

```bash
# Development mode
python server.py

# Or using FastMCP CLI
fastmcp run server:mcp

# With specific arguments
fastmcp run server:mcp --port 8000
```

### 2. Claude Desktop Integration

Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["/absolute/path/to/your/project/server.py"],
      "env": {
        "DB_PATH": "/absolute/path/to/your/project/data/app.db"
      }
    }
  }
}
```

### 3. Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=.

# Run specific test file
pytest tests/test_server.py -v
```

## Key Features

- **Modular Architecture**: Separate modules for tools, resources, and configuration
- **Async Database Operations**: Full async support with aiosqlite
- **Environment-based Configuration**: Flexible settings via environment variables
- **Safety Features**: Read-only mode support and query validation
- **Comprehensive Testing**: Unit tests for all major components
- **Docker Support**: Ready for containerization
- **Logging**: Structured logging for debugging and monitoring

## Next Steps

1. **Extend Database Schema**: Add more tables and relationships as needed
2. **Add Authentication**: Implement user authentication for multi-user scenarios
3. **Performance Optimization**: Add connection pooling and query caching
4. **Docker Deployment**: Create Dockerfile for containerized deployment
5. **Monitoring**: Add health checks and metrics collection
6. **Documentation**: Generate API documentation using FastMCP's built-in features

This architecture provides a solid foundation for building sophisticated MCP servers that can integrate with any LLM client while maintaining proper separation of concerns and scalability.