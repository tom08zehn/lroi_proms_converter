@echo off
setlocal enabledelayedexpansion

:: ── git_update.bat ──────────────────────────────────────────────────────────
:: Interactive helper for branching, committing, pushing and merging.
::
:: Usage:  double-click or run from cmd / Git Bash
:: ─────────────────────────────────────────────────────────────────────────────

:: ── Verify git is available ─────────────────────────────────────────────────
where git >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: git not found in PATH.
    pause
    exit /b 1
)

:: ── 1. Create or Update? ────────────────────────────────────────────────────
:ask_mode
set "mode="
set /p "mode=Create (c) or Update (u) existing branch? [c]: "
if "!mode!"=="" set "mode=c"
if /i "!mode!"=="c" goto :ask_branch
if /i "!mode!"=="u" goto :ask_branch
echo Invalid selection. Enter 'c' or 'u'.
goto :ask_mode

:: ── 2. Branch name ──────────────────────────────────────────────────────────
:ask_branch
set "branch="
set /p "branch=Branch name (e.g. release/V1.5.0 [uppercase 'V')): "
if "!branch!"=="" (
    echo Branch name cannot be empty.
    goto :ask_branch
)

:: ── 3. Commit message ───────────────────────────────────────────────────────
:ask_message
set "msg="
set /p "msg=Commit message: "
if "!msg!"=="" (
    echo Commit message cannot be empty.
    goto :ask_message
)

:: ── 4. Optional merge target ────────────────────────────────────────────────
set "merge_target="
set /p "merge_target=Merge with branch (blank = don't merge): "

:: ── Summary ─────────────────────────────────────────────────────────────────
echo.
echo =========================================
if /i "!mode!"=="c" (
    echo  Mode:    CREATE new branch
) else (
    echo  Mode:    UPDATE existing branch
)
echo  Branch:  !branch!
echo  Commit:  !msg!
if "!merge_target!"=="" (
    echo  Merge:   (none)
) else (
    echo  Merge:   !branch! -- !merge_target!
)
echo =========================================
echo.
set "confirm="
set /p "confirm=Proceed? (y/n) [y]: "
if "!confirm!"=="" set "confirm=y"
if /i not "!confirm!"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.

:: ── Create or switch to branch ──────────────────────────────────────────────
if /i "!mode!"=="c" (
    echo [1/5] Creating branch: !branch!
    git checkout -b "!branch!"
) else (
    echo [1/5] Switching to branch: !branch!
    git checkout "!branch!"
)
if !errorlevel! neq 0 (
    echo ERROR: git checkout failed.
    pause
    exit /b 1
)

:: ── Stage all changes ───────────────────────────────────────────────────────
echo [2/5] Staging all changes...
git add -A
if !errorlevel! neq 0 (
    echo ERROR: git add failed.
    pause
    exit /b 1
)

:: ── Commit ──────────────────────────────────────────────────────────────────
echo [3/5] Committing...
git commit -m "!msg!"
if !errorlevel! neq 0 (
    echo WARNING: Nothing to commit, or commit failed.
)

:: ── Push ─────────────────────────────────────────────────────────────────────
echo [4/5] Pushing to origin...
git push -u origin "!branch!"
if !errorlevel! neq 0 (
    echo ERROR: git push failed.
    pause
    exit /b 1
)

:: ── Merge (optional) ────────────────────────────────────────────────────────
:: Strip whitespace from merge_target
for /f "tokens=*" %%a in ("!merge_target!") do set "merge_target=%%a"

if "!merge_target!"=="" (
    echo [5/5] No merge requested.
    goto :done
)

echo [5/5] Merging !branch! into !merge_target!...

git checkout "!merge_target!"
if !errorlevel! neq 0 (
    echo ERROR: Could not switch to !merge_target!.
    pause
    exit /b 1
)

git merge "!branch!"
if !errorlevel! neq 0 (
    echo ERROR: Merge failed. Resolve conflicts, then run:
    echo   git add -A ^&^& git commit ^&^& git push
    pause
    exit /b 1
)

git push origin "!merge_target!"
if !errorlevel! neq 0 (
    echo ERROR: Push of merged !merge_target! failed.
    pause
    exit /b 1
)

echo Merged and pushed !merge_target!.

:done
echo.
echo =========================================
echo  Done.
echo =========================================
pause
