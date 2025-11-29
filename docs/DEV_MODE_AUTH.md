# Dev Mode: Temporary Auth Disable

**Status**: ⚠️ DEV ONLY - DO NOT USE IN PRODUCTION  
**Purpose**: Simplify development by allowing password storage during testing  
**Security**: Passwords saved in plaintext - INSECURE!

---

## 🚨 WARNING

**This feature is ONLY for development. NEVER enable in production!**

Passwords will be stored in **plaintext** on disk. Anyone with access to your `%APPDATA%\database-operations-mcp` directory can read your database passwords.

---

## 📋 How to Enable Dev Mode

### Option 1: Environment Variable (Recommended)

Set before starting Claude Desktop:

**PowerShell:**
```powershell
$env:ENABLE_PASSWORD_STORAGE = "1"
```

**Windows Command Prompt:**
```cmd
set ENABLE_PASSWORD_STORAGE=1
```

**Permanent (User-level):**
```powershell
[System.Environment]::SetEnvironmentVariable("ENABLE_PASSWORD_STORAGE", "1", "User")
```

### Option 2: Claude Desktop Config

Add to your Claude Desktop MCP server config:

```json
{
  "mcpServers": {
    "database-operations-mcp": {
      "command": "python",
      "args": ["-m", "database_operations_mcp"],
      "env": {
        "ENABLE_PASSWORD_STORAGE": "1"
      }
    }
  }
}
```

---

## ✅ What Dev Mode Does

### 1. Saves Passwords to Storage

When `ENABLE_PASSWORD_STORAGE=1`:
- Passwords are saved alongside connection configs
- Stored in plaintext in `%APPDATA%\database-operations-mcp`
- **WARNING**: Anyone with file access can read passwords!

### 2. Auto-Reconnect After Restart

```python
# After restart, connections restore automatically
result = await restore_saved_connections(auto_reconnect=True)
# Reconnects using saved passwords (if available)
```

### 3. Convenient Development Workflow

**First time:**
```python
await init_database(
    "postgresql",
    {
        "host": "localhost",
        "user": "admin",
        "password": "dev123",  # Saved to disk!
        "database": "test"
    },
    "dev_db"
)
```

**After restart:**
```python
# Automatically reconnects
await restore_saved_connections(auto_reconnect=True)
# Connection restored with saved password!
```

---

## 🛡️ Security Risks

### What Gets Saved (Dev Mode)

```json
{
  "prod_db": {
    "name": "prod_db",
    "type": "postgresql",
    "params": {
      "host": "db.example.com",
      "user": "admin",
      "password": "secret123",  // ← PLAINTEXT on disk!
      "database": "production"
    }
  }
}
```

### Who Can Access

Anyone with access to:
- Your Windows user account
- Your `%APPDATA%` directory
- Filesystem backups
- Malware with file access

---

## 🔒 Production Mode (Default)

**Default behavior (secure):**
- Passwords are **NEVER** saved
- Connections must be re-authenticated after restart
- User provides password each session

**How it works:**
```python
# Connection saved without password
await init_database(..., connection_params={"password": "secret"})
# Saved config: {host, user, database}  ← password excluded

# After restart:
await restore_saved_connections()
# Returns: {host, user, database}  ← password missing

# User must reconnect:
await init_database(..., connection_params={
    **saved_config,
    "password": "secret"  # ← Must provide again
})
```

---

## 📝 Development Best Practices

### 1. Use Dev Databases Only

Only enable dev mode with:
- Local development databases
- Test/development servers
- Non-sensitive test data

**NEVER use with:**
- Production databases
- Real customer data
- Databases with sensitive information

### 2. Clean Up After Testing

After development:
```powershell
# Remove dev mode
Remove-Item Env:\ENABLE_PASSWORD_STORAGE

# Clear saved passwords
Remove-Item "$env:APPDATA\database-operations-mcp" -Recurse -Force
```

### 3. Use Environment-Specific Configs

Keep separate configs for dev/prod:

**Dev:**
```powershell
$env:ENABLE_PASSWORD_STORAGE = "1"
$env:DB_HOST = "localhost"
```

**Prod:**
```powershell
# ENABLE_PASSWORD_STORAGE not set (secure)
$env:DB_HOST = "prod.db.example.com"
```

---

## 🧪 Testing Auto-Reconnect

### Step 1: Enable Dev Mode
```powershell
$env:ENABLE_PASSWORD_STORAGE = "1"
```

### Step 2: Create Connection
```python
await init_database(
    "sqlite",
    {"database": "test.db"},
    "test"
)
```

### Step 3: Restart Claude Desktop

### Step 4: Auto-Reconnect
```python
result = await restore_saved_connections(auto_reconnect=True)
# Should reconnect automatically
```

---

## ⚠️ Checklist Before Production

Before deploying to production:

- [ ] `ENABLE_PASSWORD_STORAGE` environment variable NOT set
- [ ] All saved passwords removed from storage directory
- [ ] Production config uses secure mode (no password storage)
- [ ] Team aware that passwords must be provided each session
- [ ] Documentation updated about authentication workflow

---

## 🔄 Disabling Dev Mode

**Remove environment variable:**
```powershell
Remove-Item Env:\ENABLE_PASSWORD_STORAGE
```

**Clear saved passwords:**
```powershell
# WARNING: Deletes all saved connections!
Remove-Item "$env:APPDATA\database-operations-mcp" -Recurse -Force
```

**Or selectively remove passwords:**
- Edit storage files manually
- Use `delete_connection()` tool to remove specific connections
- Re-create connections without dev mode

---

## 📊 Comparison

| Feature | Dev Mode | Production Mode |
|---------|----------|----------------|
| Password Storage | ✅ Saved (plaintext) | ❌ Never saved |
| Auto-Reconnect | ✅ Works automatically | ❌ Manual reconnect |
| Security | ⚠️ INSECURE | ✅ Secure |
| Restart Behavior | Restores with passwords | Needs password input |
| Use Case | Development only | Production |

---

**Remember**: Dev mode is for convenience during development. Always disable before production deployment!

