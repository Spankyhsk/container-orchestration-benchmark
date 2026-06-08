# =========================================
# PARAMETER
# =========================================
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$configPath,

    [Parameter(Mandatory = $false, Position = 1)]
    [string]$mode = $null
)

# =========================================
# VALIDATION
# =========================================
if (-not $configPath) {
    Write-Error "configPath is missing. Usage: run_benchmarks.ps1 <config.json> [mode]"
    exit 1
}

if (-not (Test-Path $configPath)) {
    Write-Error "Config file not found: $configPath"
    exit 1
}

# =========================================
# CONFIG
# =========================================
$config = Get-Content -Path $configPath -Raw | ConvertFrom-Json

# MODE PRIORITY:
# 1. CLI (UI)
# 2. config.json fallback
# 3. default
if (-not $mode) {
    $mode = $config.mode
}

if (-not $mode) {
    $mode = "full"
}

Write-Host "=== MODE: $mode ==="

# =========================================
# STATS
# =========================================
$stats = @{ }

foreach ($env in $config.envs)
{
    $stats[$env] = @{ success = 0; failed = 0 }
}

# =========================================
# START
# =========================================
$benchName = $config.name
if (-not $benchName) { $benchName = "unnamed" }

python -c "from src.reports.discord import send_message; send_message('Benchmark STARTED | NAME=$benchName | MODE=$mode')"

# =========================================
# BENCHMARK PHASE
# =========================================
if ($mode -ne "analyze")
{
    foreach ($scenario in $config.scenarios)
    {
        python -c "from src.reports.discord import send_message; send_message('SCENARIO START: $scenario')"

        foreach ($testType in $config.testTypes)
        {
            foreach ($env in $config.envs)
            {
                for ($i = 0; $i -lt $config.runsPerTest; $i++)
                {
                    $runLabel = "$env | $scenario | $testType | $i"

                    python -c "from src.reports.discord import send_message; send_message('RUN: $runLabel')"

                    try
                    {
                        python -m src.benchmark `
                            --env $env `
                            --testClass $config.testClass `
                            --scenario $scenario `
                            --testType $testType `
                            --run $i

                        $exitCode = $LASTEXITCODE

                        if ($exitCode -eq 0)
                        {
                            $stats[$env].success++
                            python -c "from src.reports.discord import send_message; send_message('SUCCESS: $runLabel')"
                        }
                        else
                        {
                            $stats[$env].failed++
                            python -c "from src.reports.discord import send_message; send_message('FAILED: $runLabel | ExitCode=$exitCode')"
                        }
                    }
                    catch
                    {
                        $stats[$env].failed++
                        $err = $_.Exception.Message.Replace("'", "''")

                        python -c "from src.reports.discord import send_message; send_message('ERROR: $runLabel | $err')"
                    }

                    Start-Sleep -Seconds $config.sleepSeconds
                }
            }
        }

        if ($config.scenarioCooldownSeconds)
        {
            python -c "from src.reports.discord import send_message; send_message('SCENARIO COOLDOWN: $scenario | waiting $($config.scenarioCooldownSeconds)s')"
            Start-Sleep -Seconds $config.scenarioCooldownSeconds
        }
    }
}

# =========================================
# ANALYSIS PHASE (REPLACES aggregation + comparison)
# =========================================
if ($mode -ne "collect")
{
    Write-Host "=== RUN ANALYSIS PIPELINE ==="

    python -m src.run_analysis --config $configPath
}

# =========================================
# REPORTS
# =========================================
if ($mode -ne "collect")
{
    foreach ($scenario in $config.scenarios)
    {
        foreach ($testType in $config.testTypes)
        {
            $pdf = "results/final_comparison/$scenario/$testType/final_report.pdf"

            if (Test-Path $pdf)
            {
                python -c "
from src.reports.discord import send_file
send_file('$pdf', 'FINAL COMPARISON REPORT: $scenario / $testType')
"
            }
        }
    }
}

# =========================================
# SUMMARY
# =========================================
if ($mode -ne "analyze")
{
    $summary = "BENCHMARK DONE`n`n"

    foreach ($env in $stats.Keys)
    {
        $s = $stats[$env].success
        $f = $stats[$env].failed

        $summary += "$env -> SUCCESS $s / FAILED $f`n"
    }

    $summary | python -c "import sys; from src.reports.discord import send_message; send_message(sys.stdin.read())"
}