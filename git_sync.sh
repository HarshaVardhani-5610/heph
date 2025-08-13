#!/bin/bash
set -x

echo "=== Git Sync Debug Script ==="
echo "Current directory: $(pwd)"
echo "Git status:"
git status --porcelain
echo ""

echo "Local HEAD: $(cat .git/refs/heads/main)"
echo "Remote HEAD: $(cat .git/refs/remotes/origin/main)"
echo ""

echo "Recent commits:"
git log --oneline -3
echo ""

echo "Attempting to push..."
git push origin main 2>&1
echo "Push exit code: $?"

echo "=== After push attempt ==="
echo "Remote HEAD now: $(cat .git/refs/remotes/origin/main)"
