# Contributing to Plot & Palette

Thank you for your interest in contributing to Plot & Palette! This guide will help you get started with collaborative development.

## 🚀 Quick Start for Contributors

### First-Time Setup

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd "plot&palette"
   ./setup.sh  # Run the automated setup script
   ```

2. **Verify Installation**
   ```bash
   # Check all services are running
   docker-compose ps
   
   # Test the application
   curl http://localhost/api/health
   
   # Run diagnostics
   python diagnostic.py
   ```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Frontend changes go in `frontend-vue/src/`
   - Backend changes go in `server.py`, `database.py`, etc.
   - New services go in their own directories

3. **Test Your Changes**
   ```bash
   # Test frontend changes
   cd frontend-vue
   npm run serve  # Dev server with hot reload
   
   # Test backend changes
   docker-compose restart backend
   docker-compose logs backend
   
   # Run full diagnostic
   python diagnostic.py
   ```

4. **Build Production Version**
   ```bash
   cd frontend-vue
   npm run build
   docker-compose up --build -d
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

## 🏗️ Development Environment

### Frontend Development (Vue.js)

**Directory Structure:**
```
frontend-vue/
├── src/views/          # Main pages (HomePage, GradientPalette, etc.)
├── src/components/     # Reusable components (Modal, LoadingSpinner)
├── src/router/         # Vue Router configuration
└── src/assets/         # Static assets and images
```

**Development Commands:**
```bash
cd frontend-vue

# Install dependencies
npm install

# Start development server (hot reload)
npm run serve  # Runs on http://localhost:8080

# Build for production
npm run build

# Lint and fix code
npm run lint
```

**Frontend Coding Standards:**
- Use Vue 3 Composition API
- Scoped CSS in `<style scoped>` sections
- ES6+ JavaScript syntax
- Responsive design (mobile-first)
- Follow existing component patterns

### Backend Development (Python)

**Main Backend (Flask):**
```bash
# Start only database and other services
docker-compose up -d database emotion-api story-api

# Run backend locally for development
pip install -r requirements-prod.txt
python server.py  # Runs on http://localhost:5000
```

**Microservices:**
- **Emotion API**: `emotions_generation/emotion_prediction_api.py`
- **Story API**: `story_generation/secure_story_generator.py`

**Backend Coding Standards:**
- Python 3.8+ syntax
- Flask best practices for main API
- FastAPI for microservices
- Proper error handling and logging
- Type hints where applicable

## 🧪 Testing Guidelines

### Manual Testing Checklist

Before submitting a PR, test these user flows:

1. **Homepage to Palette Capture**
   - [ ] Homepage loads with all images
   - [ ] "Start Journey" button navigates to gradient page
   - [ ] GIFs cycle through 50 palettes
   - [ ] Palette capture works without errors

2. **Color Analysis Flow**
   - [ ] Captured palette displays correctly
   - [ ] Color analysis returns valid results
   - [ ] Emotion cards display properly
   - [ ] Emotion selection navigates to gallery

3. **Gallery and Story Generation**
   - [ ] Recommended paintings load
   - [ ] Drag and drop functionality works
   - [ ] Character selection works
   - [ ] Story generation completes successfully
   - [ ] Story displays with proper formatting

4. **Sharing and Navigation**
   - [ ] Social sharing buttons work
   - [ ] Link copying works
   - [ ] Navigation between pages works
   - [ ] Browser back/forward works

### API Testing

```bash
# Test main backend endpoints
curl http://localhost/api/health
curl -X POST http://localhost/api/save-palette -F "image=@test-image.png"

# Test microservices
curl http://localhost:8001/health  # Emotion API
curl http://localhost:8002/health  # Story API

# Run full diagnostic
python diagnostic.py
```

## 📝 Code Style and Standards

### Git Commit Messages

Use conventional commit format:
```
feat: add new color analysis algorithm
fix: resolve palette capture memory leak
docs: update API documentation
style: fix linting issues in GalleryPage
refactor: optimize database queries
test: add unit tests for emotion prediction
```

### Code Review Checklist

**Frontend (Vue.js):**
- [ ] Components are properly scoped
- [ ] No hardcoded URLs (use environment variables)
- [ ] Responsive design works on mobile
- [ ] Accessibility attributes included
- [ ] Loading states implemented
- [ ] Error handling included

**Backend (Python):**
- [ ] Proper error handling and status codes
- [ ] Database connections properly closed
- [ ] Logging statements included
- [ ] Input validation implemented
- [ ] Security considerations addressed

### File Structure Guidelines

**Adding New Features:**

1. **New Vue Page:**
   ```
   frontend-vue/src/views/NewPage.vue
   ```
   - Update `router/index.js` with new route
   - Follow existing page patterns
   - Include loading states and error handling

2. **New API Endpoint:**
   ```python
   # In server.py
   @app.route('/api/new-endpoint', methods=['POST'])
   def new_endpoint():
       # Implementation
   ```
   - Add to main Flask app
   - Include proper error handling
   - Update API documentation

3. **New Microservice:**
   ```
   new_service/
   ├── api.py
   ├── requirements.txt
   └── Dockerfile
   ```
   - Add to `docker-compose.yml`
   - Follow existing service patterns
   - Include health check endpoint

## 🐛 Debugging and Troubleshooting

### Common Development Issues

1. **Frontend Build Failures**
   ```bash
   cd frontend-vue
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

2. **Docker Service Issues**
   ```bash
   # View logs for specific service
   docker-compose logs backend
   docker-compose logs emotion-api
   
   # Restart specific service
   docker-compose restart backend
   
   # Rebuild and restart
   docker-compose up --build -d backend
   ```

3. **Database Connection Issues**
   ```bash
   # Reset database completely
   docker-compose down -v
   docker-compose up -d database
   sleep 30
   docker-compose exec backend python database.py
   ```

4. **Port Conflicts**
   - Check `docker-compose.yml` for port mappings
   - Common conflicts: 80 (nginx), 3306 (mysql), 5000 (flask)
   - Use `lsof -i :PORT` to find conflicting processes

### Debugging Tools

```bash
# Real-time logs
docker-compose logs -f backend

# Enter container for debugging
docker-compose exec backend bash

# Check service health
python diagnostic.py

# Database debugging
docker-compose exec database mysql -u root -p plot_palette
```

## 🚢 Deployment and Production

### Environment Setup

1. **Development**: Use `npm run serve` + local Docker services
2. **Staging**: Full Docker deployment with `docker-compose up`
3. **Production**: Optimized build with `npm run build`

### Performance Considerations

- Large GIF files (palette GIFs are 15-45MB each)
- Database query optimization
- Image loading optimization
- Caching strategies

## 📚 Resources and Documentation

### Project Resources
- **Main README**: Comprehensive setup and usage guide
- **API Documentation**: Available in README.md
- **Architecture Diagrams**: See project structure sections

### External Resources
- [Vue.js Documentation](https://vuejs.org/guide/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Collaboration Guidelines

### Communication

- Use clear, descriptive commit messages
- Comment complex code sections
- Update documentation when adding features
- Create issues for bugs or feature requests

### Code Reviews

- Review changes thoroughly
- Test functionality before approving
- Provide constructive feedback
- Check for security considerations

### Branch Strategy

- `main`: Production-ready code
- `feature/*`: New features
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

## 🎯 Current Development Priorities

1. **Performance Optimization**
   - Image loading optimization
   - Database query performance
   - Frontend bundle size reduction

2. **Feature Enhancements**
   - Advanced color analysis algorithms
   - Additional story generation styles
   - Social sharing improvements

3. **Developer Experience**
   - Automated testing setup
   - CI/CD pipeline implementation
   - Better error reporting

---

**Questions?** Create an issue or reach out to the project maintainers.

**Happy Contributing! 🎨✨** 