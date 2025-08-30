# Plot & Palette - AI-Powered Color Analysis & Story Generation

A sophisticated web application that analyzes color palettes from animated GIFs, predicts emotions using machine learning, and generates personalized stories based on painting recommendations.

## 🎨 What is Plot & Palette?

Plot & Palette is an innovative application that combines color science, emotion analysis, and creative storytelling:

1. **Color Palette Analysis** - Upload or capture color palettes from 50+ animated GIFs
2. **Emotion Prediction** - AI model analyzes colors and predicts associated emotions
3. **Art Recommendation** - Get personalized painting recommendations based on your emotional profile
4. **Story Generation** - AI creates unique narratives inspired by your selected artworks and emotions
5. **Social Sharing** - Share your generated stories across social platforms

## 🏗️ Project Architecture

### Frontend (Vue.js SPA)
```
frontend-vue/
├── src/
│   ├── views/                    # Main application pages
│   │   ├── HomePage.vue         # Landing page with color bar and paintings
│   │   ├── GradientPalette.vue  # GIF cycling and palette capture
│   │   ├── ColorPalettePage.vue # Color analysis and emotion selection
│   │   ├── GalleryPage.vue      # Painting recommendations and character selection
│   │   └── StoryPage.vue        # Story display and sharing
│   ├── components/              # Reusable components
│   │   ├── LoadingSpinner.vue   # Loading animation with magic cube
│   │   └── Modal.vue            # Modal dialogs for results
│   ├── router/                  # Vue Router configuration
│   │   └── index.js             # Route definitions and navigation
│   ├── assets/                  # Static assets
│   │   └── images/              # All application images and GIFs
│   ├── App.vue                  # Main application layout
│   ├── main.js                  # Vue app initialization
│   └── style.css                # Global styles
├── public/                      # Public assets
└── package.json                 # Frontend dependencies
```

### Backend Services
```
├── server.py                    # Main Flask backend API
├── database.py                  # Database connection and operations
├── recommendation_service_embedded.py  # Painting recommendation logic
├── emotions_generation/         # Emotion prediction microservice
│   ├── emotion_prediction_api.py    # FastAPI emotion analysis service
│   ├── final_emotion_model.pkl      # Trained ML model
│   ├── final_scaler.pkl             # Feature scaler
│   └── requirements.txt             # Python dependencies
└── story_generation/            # Story generation microservice
    ├── image_story_generator.py     # Story generation logic
    ├── secure_story_generator.py   # Secure story API
    └── requirements.txt             # Python dependencies
```

### Infrastructure
```
├── docker-compose.yml           # Multi-service orchestration
├── Dockerfile                   # Main application container
├── deployment/nginx/            # Nginx reverse proxy configuration
├── database/                    # Database initialization scripts
└── logs/                        # Application and nginx logs
```

### Static Assets
```
├── image/                       # Core application images (excluded from repo by default)
│   ├── logo.png, colourbar.png, paintings.png
│   ├── style1-a.png through style5-a.png (character images)
│   └── magiccube.gif, dance.gif, keyboard.gif
└── palette GIF/                 # 50 animated color palette GIFs (excluded from repo)
    └── 1.gif through 50.gif
```

## 🚀 Quick Start Guide

### Prerequisites

1. **Docker & Docker Compose**
   - [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Ensure Docker Compose is included (comes with Docker Desktop)

2. **Node.js & npm** (for development)
   - [Install Node.js 16+](https://nodejs.org/)
   - npm comes bundled with Node.js

3. **Git**
   - [Install Git](https://git-scm.com/downloads)

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd "plot&palette"
   ```

2. **Setup Environment Variables**
   ```bash
   # Copy the example environment file
   cp docker.env.example docker.env
   
   # Edit docker.env with your settings (optional - defaults work for development)
   nano docker.env
   ```

3. **Optional: Pull large demo assets**
   - Large assets (palette GIFs, some images, uploads) are excluded from the public repo to keep the portfolio clean.
   - If you need them locally, place them under:
     - `palette GIF/` for animated palettes
     - `image/` for static images
     - or configure GCS bucket `plot-and-palette-dumpster` for runtime storage

3. **Build and Start All Services**
   ```bash
   # Build and start all Docker containers
   docker-compose up --build -d
   
   # This will start:
   # - MySQL database on port 3306
   # - Main Flask backend on port 5000
   # - Emotion prediction API on port 8001
   # - Story generation API on port 8002
   # - Nginx reverse proxy on port 80
   ```

4. **Initialize the Database**
   ```bash
   # Wait for services to start (about 30 seconds), then initialize DB
   docker-compose exec backend python database.py
   ```

5. **Build the Frontend**
   ```bash
   cd frontend-vue
   npm install
   npm run build
   ```

6. **Access the Application**
   - Open your browser to: `http://localhost`
   - The application should be fully functional!

## 🛠️ Development Setup

For active development with hot reload:

### Frontend Development
```bash
cd frontend-vue
npm install
npm run serve  # Starts dev server on http://localhost:8080
```

### Backend Development
```bash
# Start only backend services
docker-compose up -d database emotion-api story-api

# Run main backend locally for development
pip install -r requirements-prod.txt
python server.py  # Runs on http://localhost:5000
```

### Full Development Environment
```bash
# Terminal 1: Start backend services
docker-compose up database emotion-api story-api nginx

# Terminal 2: Start frontend dev server
cd frontend-vue
npm run serve

# Terminal 3: Run main backend locally (optional)
python server.py
```

## 📊 Service Health Monitoring

The application includes a comprehensive diagnostic system:

```bash
# Check all service health
python diagnostic.py

# Manual service checks
curl http://localhost/api/health        # Main backend
curl http://localhost:8001/health       # Emotion API
curl http://localhost:8002/health       # Story API
```

## 🎮 How to Use the Application

1. **Start Your Journey** - Click "Start the Journey!" on the homepage
2. **Select a Palette** - Choose from 50 animated color palettes or let them cycle
3. **Capture Colors** - Click when you see a palette you like
4. **View Analysis** - See your color breakdown and predicted emotions
5. **Choose Emotion** - Select the emotion that resonates with you
6. **Explore Gallery** - Browse recommended paintings based on your selection
7. **Select Artworks** - Drag and drop paintings that inspire you
8. **Choose Style** - Pick a narrative character (Poet, Storyteller, etc.)
9. **Read Your Story** - Enjoy your personalized AI-generated story
10. **Share** - Share your story on social media or copy the link

## 🔧 Configuration Options

### Environment Variables (docker.env)
```bash
# Database Configuration
MYSQL_ROOT_PASSWORD=your_password
MYSQL_DATABASE=plot_palette
MYSQL_USER=app_user
MYSQL_PASSWORD=app_password

# API Keys (optional - for enhanced features)
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key

# Application Settings
FLASK_ENV=production
DEBUG=False
```

### Frontend Configuration
- **API Base URL**: Configure in `frontend-vue/src/main.js`
- **Router Mode**: Hash vs History mode in `frontend-vue/src/router/index.js`
- **Build Settings**: Modify `frontend-vue/vue.config.js`

## 📦 Repository Hygiene
- To keep this portfolio repository lightweight, the following are ignored via `.gitignore`:
  - `frontend-vue/node_modules/`, `frontend-vue/dist/`
  - `uploads/` (runtime artifacts)
  - Large asset folders: `palette GIF/`, `image/`, `GIF/`, `illustrations/`
  - Logs and local backups.
- Containers only copy what’s needed at runtime (backend code, ML resources, built SPA).

## 🚨 Troubleshooting

### Common Issues

1. **Services Won't Start**
   ```bash
   # Check Docker status
   docker-compose ps
   
   # View logs
   docker-compose logs [service-name]
   
   # Restart services
   docker-compose restart
   ```

2. **Database Connection Errors**
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up -d database
   # Wait 30 seconds
   docker-compose exec backend python database.py
   ```

3. **Frontend Build Failures**
   ```bash
   cd frontend-vue
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

4. **Port Conflicts**
   - Modify ports in `docker-compose.yml`
   - Common conflicts: 80 (nginx), 3306 (mysql), 5000 (flask)

### Performance Issues
- Large GIF files may cause slow loading
- Consider optimizing images in `palette GIF/` folder
- Use `npm run build` for production deployment

## 🤝 Contributing

### Development Workflow
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test locally: `npm run serve` + `docker-compose up`
4. Build production: `npm run build`
5. Commit and push: `git commit -m "Your changes" && git push`
6. Create a pull request

### Code Standards
- **Frontend**: Vue.js 3 Composition API, ES6+
- **Backend**: Python 3.8+, Flask/FastAPI
- **Styling**: Scoped CSS, responsive design
- **Testing**: Manual testing recommended before commits

### Adding New Features
- **New Pages**: Add to `frontend-vue/src/views/`
- **New API Endpoints**: Add to `server.py` with proper error handling
- **New Services**: Create new Docker service in `docker-compose.yml`

## 📝 API Documentation

### Main Backend Endpoints
- `GET /api/health` - Service health check
- `POST /api/save-palette` - Upload palette image
- `POST /api/get-recommendations` - Get painting recommendations
- `POST /api/generate-story` - Create story from selections

### Emotion API Endpoints  
- `GET /health` - Emotion service health
- `POST /predict` - Predict emotions from color data

### Story API Endpoints
- `GET /health` - Story service health  
- `POST /generate` - Generate story from prompts

## 📜 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙋‍♂️ Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Run the diagnostic script: `python diagnostic.py`
4. Create an issue in the repository

---

**Happy Coding! 🎨✨**

*Plot & Palette - Where Colors Meet Stories* 