---
name: warn-dangerous-docker
enabled: true
event: bash
pattern: docker\s+system\s+prune\s+-a|docker\s+volume\s+prune|docker\s+rm\s+.*-f
---

⚠️ **DANGEROUS DOCKER COMMAND DETECTED**

You're running a Docker command that could delete important data.

**Command risks:**
- `docker system prune -a`: Deletes ALL unused images, volumes, networks
- `docker volume prune`: Deletes ALL unused volumes (including service data)
- `docker rm -f`: Force removes containers (data loss if not backed up)

**This repository's Docker architecture** (per CLAUDE.md):

```
Service Mesh (tools/docker-compose.yml)
├─ osint_logs, osint_data, osint_reports
├─ telegram_logs, telegram_data
├─ php_logs, php_data, php_uploads
└─ js_logs, js_data, js_uploads
```

**Data isolation pattern:**
Each service has dedicated volumes. Pruning volumes will DELETE this isolated data.

**Before proceeding:**

1. **Check what will be deleted**:
   ```bash
   docker system df          # See space usage
   docker volume ls          # List volumes
   docker volume ls -f dangling=true  # See unused volumes
   ```

2. **Backup critical data** from volumes:
   ```bash
   docker run --rm -v osint_data:/data -v $(pwd):/backup \
     alpine tar czf /backup/osint_data_backup.tar.gz /data
   ```

3. **Use selective cleanup**:
   ```bash
   docker image prune        # Only unused images
   docker container prune    # Only stopped containers
   # Manual volume deletion of specific volumes only
   ```

**Safer alternative:**
```bash
# List what would be deleted first
docker system prune --dry-run
docker volume prune --dry-run
```

Proceed with caution - this is destructive!
