@echo off
setlocal enabledelayedexpansion

set CONFIGS=default 1 2 3

for %%G in (%CONFIGS%) do (
    echo Running tests with config: %%G
    pytest --config=%%G
)