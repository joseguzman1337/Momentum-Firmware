#!/bin/bash
git --no-pager log -n 1 > git_log_check.txt 2>&1
git status >> git_log_check.txt 2>&1
