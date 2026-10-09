; Installer hooks for database-operations-mcp (Tauri NSIS).
; "Register in AI tools" page + register/unregister come from the vendored fleet include
; mcp-clients.nsh (copied from mcp-central-docs by native/build.ps1 - do not edit it here).
!define MCP_REG_NAME "database-operations-mcp"
!define MCP_REG_EXE "database-operations-mcp-backend.exe"
!include "${__FILEDIR__}\mcp-clients.nsh"

; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillDatabaseOperationsMcpFleetProcesses
  DetailPrint "Stopping database-operations-mcp processes..."
  ExecWait 'taskkill /F /IM database-operations-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM database-operations-mcp-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "database-operations-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "database-operations-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "database-operations-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "database-operations-mcp-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillDatabaseOperationsMcpFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro McpClientsUnregister
  !insertmacro KillDatabaseOperationsMcpFleetProcesses
!macroend

!macro NSIS_HOOK_POSTINSTALL
  !insertmacro McpClientsRegister
!macroend
