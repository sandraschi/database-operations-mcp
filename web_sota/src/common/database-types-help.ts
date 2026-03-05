/**
 * Detailed help for each supported database type. Used by the Database types help page
 * and by the Connection wizard inline help.
 */
export interface FieldHelp {
    key: string;
    label: string;
    description: string;
}

export interface DatabaseTypeHelp {
    id: string;
    name: string;
    shortDescription: string;
    description: string;
    whenToUse: string[];
    requiredFields: FieldHelp[];
    optionalFields?: FieldHelp[];
    examples: string[];
    tips: string[];
}

export const DATABASE_TYPES_HELP: DatabaseTypeHelp[] = [
    {
        id: "sqlite",
        name: "SQLite",
        shortDescription: "Single-file, serverless SQL database.",
        description:
            "SQLite stores the entire database in one file on disk. There is no separate server process: your application reads and writes the file directly. It is built into many operating systems and is very common for local apps, tools, and mobile.",
        whenToUse: [
            "Local applications (desktop, mobile, small tools)",
            "Single-user or low concurrency",
            "Backups or copies of data you want to move as a single file",
            "Testing and development without installing a server",
        ],
        requiredFields: [
            {
                key: "database",
                label: "Database path",
                description:
                    "Full path to the .db file (e.g. C:\\Users\\You\\data\\app.db on Windows, /home/user/data/app.db on Linux). Use a relative path like ./mydb.db to store the file relative to the working directory of the backend. If the file does not exist, SQLite will create it when you first write data.",
            },
        ],
        optionalFields: [],
        examples: [
            "C:/data/myapp.db (Windows absolute)",
            "D:\\Projects\\app\\local.db",
            "./data/sqlite.db (relative to backend)",
            ":memory: (in-memory only; data is lost when the connection closes)",
        ],
        tips: [
            "On Windows use forward slashes or escaped backslashes in paths.",
            "For read-only access, the file must already exist.",
            "Avoid putting the file on a network share if many processes will write; SQLite works best with local disk.",
        ],
    },
    {
        id: "postgresql",
        name: "PostgreSQL",
        shortDescription: "Server-based relational database.",
        description:
            "PostgreSQL is a full-featured relational database server. You connect to it over the network by specifying host, port, and credentials. It supports complex queries, transactions, and many extensions. It is widely used in production and for multi-user applications.",
        whenToUse: [
            "Production web apps and APIs",
            "Multi-user or concurrent access",
            "Complex queries, JSON inside columns, full-text search",
            "When you need a dedicated DBA or managed service (e.g. AWS RDS, Azure)",
        ],
        requiredFields: [
            { key: "host", label: "Host", description: "Machine name or IP where PostgreSQL is running. Use localhost or 127.0.0.1 for a server on the same machine." },
            { key: "port", label: "Port", description: "TCP port. The default is 5432. Your DBA or hosting provider will confirm if it is different." },
            { key: "user", label: "User", description: "Database user name. Must have permission to connect and to access the databases you need." },
            { key: "password", label: "Password", description: "Password for that user. Leave blank only if the server is configured to allow passwordless access (e.g. local trust)." },
            { key: "database", label: "Database", description: "Name of the specific database (catalog) to connect to. A single PostgreSQL server can host many databases." },
        ],
        optionalFields: [
            { key: "sslmode", label: "SSL mode", description: "Use 'require' or 'verify-full' for encrypted connections; 'prefer' or 'disable' for local/dev. Default is often 'prefer'." },
        ],
        examples: [
            "host: localhost, port: 5432, user: postgres, database: myapp",
            "host: db.mycompany.com, port: 5432, user: readonly, database: analytics",
        ],
        tips: [
            "Ensure the PostgreSQL server is running and that the port is not blocked by a firewall.",
            "For cloud providers, use the host and port they give you and check their SSL requirements.",
        ],
    },
    {
        id: "mysql",
        name: "MySQL",
        shortDescription: "Popular server-based relational database.",
        description:
            "MySQL is a relational database server you connect to over the network. It is very common for web applications (often with PHP or as the default in many hosting panels). Syntax and features differ slightly from PostgreSQL; both support standard SQL.",
        whenToUse: [
            "Web applications (especially with LAMP/LEMP stacks)",
            "When your host or framework expects MySQL",
            "Replication and read replicas (common in MySQL ecosystems)",
        ],
        requiredFields: [
            { key: "host", label: "Host", description: "Machine name or IP of the MySQL server. Use localhost for the same machine." },
            { key: "port", label: "Port", description: "TCP port. Default is 3306." },
            { key: "user", label: "User", description: "MySQL user name with connect and usage rights." },
            { key: "password", label: "Password", description: "Password for that user." },
            { key: "database", label: "Database", description: "Name of the database (schema) to use." },
        ],
        optionalFields: [],
        examples: [
            "host: localhost, port: 3306, user: root, database: myapp",
            "host: 192.168.1.10, port: 3306, user: appuser, database: production",
        ],
        tips: [
            "MySQL server must be running and the port reachable.",
            "Some hosted MySQL (e.g. MariaDB) use the same connection parameters.",
        ],
    },
    {
        id: "duckdb",
        name: "DuckDB",
        shortDescription: "In-process analytics database (SQL).",
        description:
            "DuckDB is an embedded analytics database: it runs inside your process (like SQLite) but is optimized for analytical queries on larger datasets. It can read and write Parquet, CSV, and JSON. Good for data exploration and local analytics without a server.",
        whenToUse: [
            "Analytics and reporting on CSV, Parquet, or local data",
            "Single-machine data processing",
            "No server setup; everything in one process",
        ],
        requiredFields: [
            {
                key: "database",
                label: "Database path",
                description:
                    "Path to a .duckdb file, or the special value :memory: for an in-memory database. The file is created if it does not exist.",
            },
        ],
        optionalFields: [],
        examples: [
            "C:/analytics/data.duckdb",
            "./my.duckdb",
            ":memory: (temporary; lost when connection closes)",
        ],
        tips: [
            "Use :memory: for quick experiments; use a file path to persist data.",
            "DuckDB can query external files: SELECT * FROM 'file.parquet'; (run from Data or Tools page).",
        ],
    },
    {
        id: "mongodb",
        name: "MongoDB",
        shortDescription: "Document (NoSQL) database.",
        description:
            "MongoDB stores data as flexible documents (usually JSON-like), not as fixed tables. You connect to a server and specify a database name; inside it you have collections rather than tables. The MCP tools can list collections and run queries in a way that fits this model.",
        whenToUse: [
            "Flexible or nested data that does not fit fixed columns",
            "App backends that already use MongoDB",
            "Content or catalog data with varying attributes",
        ],
        requiredFields: [
            { key: "host", label: "Host", description: "MongoDB server hostname or IP." },
            { key: "port", label: "Port", description: "Default is 27017." },
            { key: "database", label: "Database", description: "Name of the database (top-level namespace) to use." },
        ],
        optionalFields: [
            { key: "user", label: "User", description: "Username if authentication is enabled." },
            { key: "password", label: "Password", description: "Password for that user." },
        ],
        examples: [
            "host: localhost, port: 27017, database: myapp",
            "host: cluster0.xxxxx.mongodb.net (for Atlas; may need different driver options)",
        ],
        tips: [
            "MongoDB server must be running. For MongoDB Atlas, use the connection string they provide; you may need to register via the Tools page with a connection_config that matches the driver.",
        ],
    },
    {
        id: "redis",
        name: "Redis",
        shortDescription: "In-memory key-value store and cache.",
        description:
            "Redis is an in-memory data store often used for caching, sessions, and simple key-value or list/set structures. It is very fast but data is in RAM; persistence is optional. Our tools can connect and run appropriate commands.",
        whenToUse: [
            "Caching (e.g. query or API response cache)",
            "Session or short-lived state",
            "Simple keys and values or small structures",
        ],
        requiredFields: [
            { key: "host", label: "Host", description: "Redis server hostname or IP." },
            { key: "port", label: "Port", description: "Default is 6379." },
        ],
        optionalFields: [
            { key: "password", label: "Password", description: "Required if the server has requirepass set. Leave blank for no auth." },
        ],
        examples: [
            "host: localhost, port: 6379",
            "host: redis.mycompany.com, port: 6379, password: (your password)",
        ],
        tips: [
            "Redis is in-memory; restarting the server loses data unless persistence (RDB/AOF) is enabled.",
            "Use a connection name that reflects the environment (e.g. cache_dev, cache_prod).",
        ],
    },
    {
        id: "lancedb",
        name: "LanceDB",
        shortDescription: "Vector database for embeddings and similarity search.",
        description:
            "LanceDB is used for vector (embedding) data and similarity search, e.g. for RAG or semantic search. You can use a local path or a cloud URI. For cloud, you typically need an API key and region in addition to the URI.",
        whenToUse: [
            "Storing and querying vector embeddings",
            "Semantic or similarity search",
            "RAG (retrieval-augmented generation) pipelines",
        ],
        requiredFields: [
            {
                key: "uri",
                label: "URI",
                description:
                    "Local path (e.g. ./lancedb_data) or cloud URI (e.g. db://project_name). For local, the directory is created if needed.",
            },
        ],
        optionalFields: [
            { key: "api_key", label: "API key", description: "For LanceDB cloud; obtain from the LanceDB cloud console." },
            { key: "region", label: "Region", description: "Cloud region, e.g. us-east-1." },
        ],
        examples: [
            "uri: ./data/lancedb (local directory)",
            "uri: db://my_project, api_key: xxx, region: us-east-1 (cloud)",
        ],
        tips: [
            "For local use, a simple path is enough. For cloud, fill in the API key and region as required by your plan.",
        ],
    },
    {
        id: "chromadb",
        name: "ChromaDB",
        shortDescription: "Embedding store for vector search.",
        description:
            "ChromaDB stores embeddings and metadata for similarity search. It can run in-memory, persist to a directory, or connect to a remote server. Common in local RAG and embedding workflows.",
        whenToUse: [
            "Local or embedded vector search",
            "RAG and embedding experiments",
            "When your stack already uses ChromaDB",
        ],
        requiredFields: [
            {
                key: "persist_directory",
                label: "Persist directory",
                description:
                    "Path to a directory where ChromaDB will store data. Omit or use in-memory for non-persistent use (driver-dependent).",
            },
        ],
        optionalFields: [
            { key: "host", label: "Host", description: "For client/server mode; ChromaDB server host." },
            { key: "port", label: "Port", description: "Port for the ChromaDB server." },
        ],
        examples: [
            "persist_directory: ./chroma_data",
            "host: localhost, port: 8000 (if running ChromaDB server)",
        ],
        tips: [
            "Check the ChromaDB driver docs for the exact connection_config keys; persist_directory is common for embedded use.",
        ],
    },
];

export function getHelpForType(id: string): DatabaseTypeHelp | undefined {
    return DATABASE_TYPES_HELP.find((t) => t.id === id);
}
