#!/bin/bash
echo "Starting sync and push..."
git add .
git commit -m "Sync/Push All: final synchronization"
git push origin dev --force-with-lease
git submodule foreach --recursive "
  COMMIT=\$(git rev-parse HEAD)
  echo 'Pushing \$path to personal forks...'
  git push personal \$COMMIT:refs/heads/dev --force 2>/dev/null || :
  git push personal \$COMMIT:refs/heads/main --force 2>/dev/null || :
  git push personal \$COMMIT:refs/heads/master --force 2>/dev/null || :
"
echo "Done."
