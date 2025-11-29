@{
    # PSScriptAnalyzer configuration file
    # Similar to .ruff.toml or pyproject.toml for PowerShell

    # Include default rules
    IncludeDefaultRules = $true

    # Severity level: Error, Warning, Information
    Severity = @('Error', 'Warning')

    # Exclude specific rules
    ExcludeRules = @(
        'PSAvoidUsingWriteHost',  # We use Write-Host intentionally for user feedback
        'PSUseShouldProcessForStateChangingFunctions',  # Scripts may intentionally skip this
        'PSAvoidUsingPositionalParameters'  # Some cmdlets are clearer with positional params
    )

    # Rules to include (if you want only specific ones)
    # IncludeRules = @('PSUseApprovedVerbs', 'PSAvoidUsingCmdletAliases')

    # Custom rule parameters
    Rules = @{
        PSAvoidUsingCmdletAliases = @{
            Severity = 'Warning'
        }
        PSPlaceOpenBrace = @{
            Enable = $true
            OnSameLine = $true
            NewLineAfter = $true
            IgnoreOneLineBlock = $true
        }
        PSPlaceCloseBrace = @{
            Enable = $true
            NewLineAfter = $true
            IgnoreOneLineBlock = $true
            NoEmptyLineBefore = $false
        }
        PSUseConsistentIndentation = @{
            Enable = $true
            IndentationSize = 4
            PipelineIndentation = 'IncreaseIndentationForFirstPipeline'
            Kind = 'space'
        }
        PSUseConsistentWhitespace = @{
            Enable = $true
            CheckInnerBrace = $true
            CheckOpenBrace = $true
            CheckOpenParen = $true
            CheckOperator = $true
            CheckPipe = $true
            CheckPipeForRedundantWhitespace = $true
            CheckSeparator = $true
            CheckParameter = $false
            CheckVariable = $false
        }
    }
}








