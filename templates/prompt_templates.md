# Database Operations MCP - Prompt Templates

## Core Database Operations

### Database Connection Management
```
Help me set up and manage my database connections. I need to:
1. Initialize connections to my SQLite, PostgreSQL, and MongoDB databases
2. List all active connections with their status
3. Test each connection and report any issues
4. Close inactive connections to free up resources
```

### Interactive Help and Discovery
```
I'm new to this MCP system. Show me:
1. All available database operations
2. Detailed help for executing queries
3. Examples of common workflows
4. How to get started with different database types
```

### Quick Database Status Check
```
Get me a complete overview of all my database connections. Show health status, performance metrics, and any issues that need attention.
```

### Multi-Database Query Analysis
```
I need to analyze data patterns across my databases. Connect to my PostgreSQL production database and SQLite development database, then compare user activity patterns between them.
```

### Database Schema Exploration
```
Help me understand the structure of my e-commerce database. Show me all tables, their relationships, and identify any potential schema issues or optimization opportunities.
```

### Performance Optimization
```
My PostgreSQL database is running slowly. Run a comprehensive health check, analyze performance metrics, and suggest specific optimizations for better query performance.
```

## Data Operations and Management

### Batch Data Processing
```
I need to perform a complex data migration with multiple steps:
1. Read data from multiple tables in my SQLite database
2. Transform the data (clean, normalize, enrich)
3. Insert the processed data into PostgreSQL
4. Generate a detailed report of the migration results

Use batch_execute to ensure all operations succeed or fail together.
```

### Data Export and Reporting
```
Export the results of this complex query to a CSV file:
- Source: PostgreSQL production database
- Query: [Your complex SQL query here]
- Format: CSV with headers
- Include execution metrics in the report
- Save to: /reports/customer_analysis_$(date +%Y%m%d).csv
```

## Development Workflows

### Database Migration Planning
```
I'm migrating from SQLite to PostgreSQL. Help me:
1. Analyze my current SQLite schema structure
2. Identify any compatibility issues for PostgreSQL
3. Suggest the optimal PostgreSQL schema design
4. Plan the data migration strategy
```

### Development Environment Setup
```
Set up a complete development database environment:
1. Create a new SQLite database for local development
2. Set up the basic schema for a blog application (users, posts, comments)
3. Add sample data for testing
4. Configure performance monitoring
```

### Database Backup and Maintenance
```
Create a comprehensive backup strategy for my production databases. Include automated health checks, performance monitoring, and maintenance recommendations.
```

## Schema Management

### Database Schema Migration
```
Help me manage my database schema changes:
1. Initialize a new schema version in my PostgreSQL database
2. Generate and apply migration scripts
3. Handle data migration between schema versions
4. Rollback if anything goes wrong
5. Document all changes made
```

### Schema Analysis and Documentation
```
Analyze the current database schema and:
1. Generate ER diagrams for all tables
2. Document relationships and constraints
3. Identify potential performance issues
4. Suggest normalization improvements
5. Export the documentation as markdown
```

## AI and Vector Database Operations

### Vector Database Management
```
Help me set up and manage my ChromaDB vector database:
1. Initialize a new ChromaDB instance with persistent storage
2. Create collections for different types of embeddings
3. Optimize the database for semantic search
4. Set up regular backups and monitoring
```

### Semantic Search Setup
```
I want to implement semantic search for my document collection. Help me:
1. Set up a ChromaDB vector database
2. Create collections for different document types
3. Configure embedding storage and retrieval
4. Test similarity search functionality
```

### RAG System Database Design
```
Design a vector database structure for a Retrieval-Augmented Generation (RAG) system. Include collections for documents, embeddings, metadata, and user queries with optimal search performance.
```

### Knowledge Base Vector Storage
```
Convert my existing knowledge base into a vector database:
1. Analyze the current text structure
2. Set up appropriate ChromaDB collections
3. Configure metadata fields for filtering
4. Implement semantic search capabilities
```

## Austrian Business Context

### GDPR Compliance Check
```
Analyze my database structures for GDPR compliance. Identify personal data fields, check data retention policies, and suggest privacy-compliant schema modifications for Austrian/EU regulations.
```

### Multi-Language Database Design
```
Design a database schema that supports German and English content with proper collation and text search capabilities for Austrian business applications.
```

### Local Data Sovereignty
```
Help me implement a local-first database strategy that keeps sensitive data on Austrian servers while optimizing for EU data protection requirements.
```

## Advanced Operations

### Cross-Database Analytics
```
I have user data in PostgreSQL and event logs in a time-series database. Help me create analytical queries that combine data from both sources to understand user behavior patterns.
```

### Database Security Audit
```
Perform a comprehensive security audit of my database connections:
1. Check authentication methods
2. Analyze connection security
3. Review access permissions
4. Identify potential vulnerabilities
5. Suggest security improvements
```

### Performance Benchmarking
```
Run performance benchmarks across my different databases (SQLite, PostgreSQL, ChromaDB) to understand optimal use cases for each system and guide architecture decisions.
```

## Emergency and Troubleshooting

### Database Recovery
```
My production database is experiencing issues. Help me:
1. Diagnose the problem immediately
2. Check data integrity
3. Assess backup status
4. Plan recovery steps if needed
5. Prevent similar issues in the future
```

### Connection Troubleshooting
```
I'm having trouble connecting to my PostgreSQL database. Run comprehensive diagnostics including network connectivity, authentication, permissions, and server status.
```

### Query Performance Issues
```
This specific query is running very slowly: [QUERY]. Analyze its execution plan, identify bottlenecks, and suggest specific optimizations or index improvements.
```

## Data Migration and Integration

### Legacy System Migration
```
I need to migrate data from an old system to a modern database. Help me:
1. Analyze the legacy data structure
2. Design an optimal target schema
3. Plan the migration strategy
4. Validate data integrity after migration
```

### Multi-Source Data Integration
```
Integrate data from multiple sources (CSV files, API endpoints, existing databases) into a unified database structure with proper data validation and transformation.
```

### Real-time Data Synchronization
```
Set up real-time synchronization between my local development SQLite database and production PostgreSQL database for seamless development workflows.
```

## Monitoring and Maintenance

### Automated Health Monitoring
```
Set up automated health monitoring for all my databases with:
1. Daily health checks
2. Performance trend analysis
3. Proactive issue detection
4. Maintenance recommendations
5. Alert thresholds for critical issues
```

### Database Growth Analysis
```
Analyze the growth patterns of my databases over time. Predict future storage needs, identify tables growing fastest, and suggest optimization or archiving strategies.
```

### Backup Verification
```
Verify the integrity and completeness of my database backups. Test restoration procedures and ensure all critical data is properly protected.
```
