#!/bin/bash
git submodule update --remote --merge > /dev/null 2>&1
git submodule foreach 'git push origin HEAD > /dev/null 2>&1 || true' > /dev/null 2>&1