## Plot & Palette – Docker update reminder

### What’s bind-mounted vs baked into images

- Backend (`backend`)
  - Bind-mounted at runtime: `./emotions_generation -> /app/emotions_generation`, `./painting_recommendation -> /app/painting_recommendation`, `./uploads`, `./logs`.
  - Baked into image: core app code (e.g., `server.py`, `database.py`, config files copied in Dockerfile).

- Story API (`story-api`)
  - Baked into image (no source bind-mount).

- Frontend container (`frontend`)
  - Baked into image (serves built `dist`).

- Nginx (`nginx`)
  - Static content bind-mounted: `./frontend-vue/dist`, `./uploads`.
  - Nginx config is baked into the image.

### What you need to do after code changes

- Backend – changes in `painting_recommendation/` or `emotions_generation/` (bind-mounted)
  - Usually no rebuild needed. If the process needs a nudge:
  ```bash
  docker compose restart backend
  ```

- Backend – changes in core backend code (baked into image), e.g., `server.py`
  - Rebuild the image and restart the service:
  ```bash
  docker compose up -d --build backend
  # or (no-cache recommended)
  docker compose build --no-cache backend && docker compose up -d backend
  ```

- Story API – any code change
  - Rebuild and restart:
  ```bash
  docker compose up -d --build story-api
  # or
  docker compose build --no-cache story-api && docker compose up -d story-api
  ```

- Frontend container – update containerized static site
  - Rebuild to refresh the container’s `/usr/share/nginx/html`:
  ```bash
  docker compose up -d --build frontend
  ```
  - Note: for local dev you run Vue at `localhost:8080`; no container rebuild needed there.

- Nginx – config changes
  - Rebuild and restart:
  ```bash
  docker compose up -d --build nginx
  ```
  - Static files in `./frontend-vue/dist` and uploads update immediately via bind mount.

### Verify services

```bash
docker compose ps
docker compose logs --tail=80 backend
docker compose logs --tail=80 story-api
```

### Health checks

- Backend (host): `http://localhost:5003/health`
- Story API (host): `http://localhost:5002/health`
- Nginx (host): `http://localhost/health`

