# Per-repo fleet start config for database-operations-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'database-operations-mcp'
    BackendPort  = 10709
    FrontendPort = 10708
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\database-operations-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn-web-app'
        UvicornTarget = 'database_operations_mcp.http_app:web_app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10709' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
