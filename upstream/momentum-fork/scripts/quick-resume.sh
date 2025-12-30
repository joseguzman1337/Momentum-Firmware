#!/bin/bash
# Quick resume for firmware development

echo "🚀 Resuming Momentum Firmware development..."

# Check if there's a recent session
if gemini --list-sessions | grep -q "ago"; then
    echo "📋 Recent sessions found"
    gemini --resume
else
    echo "🆕 Starting new session"
    gemini /dev:start
fi