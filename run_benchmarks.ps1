# =========================================
# PARAMETER
# =========================================
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$configPath
)

# =========================================
# VALIDATION
# =========================================
if (-not $configPath) {
    Write-Error "configPath is missing. Usage: run_benchmarks.ps1 <config.json>"
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

$mode = $config.mode
if (-not $mode) { $mode = "full" }

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
python -c "from src.reports.discord import send_message; send_message('Benchmark STARTED')"

# =========================================
# BENCHMARK PHASE (SKIP IF analyze)
# =========================================
if ($mode -ne "analyze")
{
    # scenarios ganz außen
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

        # cooldown zwischen scenarios
        if ($config.scenarioCooldownSeconds)
        {
            python -c "from src.reports.discord import send_message; send_message('SCENARIO COOLDOWN: $scenario | waiting $($config.scenarioCooldownSeconds)s')"

            Start-Sleep -Seconds $config.scenarioCooldownSeconds
        }
    }
}

# =========================================
# AGGREGATION (SKIP IF collect-only)
# =========================================
if ($mode -ne "collect")
{
    foreach ($env in $config.envs)
    {
        foreach ($scenario in $config.scenarios)
        {
            foreach ($testType in $config.testTypes)
            {
                python -c "from src.evaluation.aggregator import run_aggregation; run_aggregation('$env', '$($config.testClass)', '$scenario', '$testType')"
            }
        }
    }
}

# =========================================
# COMPARISON STEP (ONLY analyze/full)
# =========================================
if ($mode -ne "collect")
{
    foreach ($scenario in $config.scenarios)
    {
        foreach ($testType in $config.testTypes)
        {
            $dockerPath = "results/docker/$($config.testClass)/$scenario/$testType/aggregate.json"
            $k3sPath    = "results/k3s/$($config.testClass)/$scenario/$testType/aggregate.json"
            $outputDir  = "results/final_comparison/$scenario/$testType"

            python -c "
from src.comparison.comparator import compare_group

compare_group(
    '$dockerPath',
    '$k3sPath',
    '$outputDir'
)
"
        }
    }
}

# =========================================
# FINAL REPORTS (ONLY analyze/full)
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
# SUMMARY (ONLY collect/full)
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