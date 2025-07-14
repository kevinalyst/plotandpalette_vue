# 🎨 Animated Gradient Palette Generator

A beautiful, interactive web application that generates flowing animated gradients using scientifically-selected color palettes. Capture any moment of the animation and share it as a unique image!

## ✨ Features

- **LAB Color Space**: Uses LAB color space for perceptually uniform and harmonious color combinations
- **Fluid Animation**: Multiple layered gradients with organic, flowing movement
- **One-Click Capture**: Stop the animation at any moment and capture the current state
- **Instant Sharing**: Upload captured images and get shareable URLs immediately
- **Modern UI**: Clean, minimalist interface with smooth animations
- **Mobile Responsive**: Works beautifully on all devices
- **Performance Optimized**: GPU-accelerated animations and service worker caching
- **Accessibility**: Keyboard shortcuts and reduced motion support

## 🚀 Quick Start

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. **Clone or download** this project to your local machine

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Start the server**:

   ```bash
   npm start
   ```

4. **Open your browser** and go to `http://localhost:3000`

### For Development

```bash
npm run dev  # Runs with nodemon for auto-restart
```

## 🎮 How to Use

1. **Watch the Animation**: Open the app and enjoy the flowing gradient animation
2. **Stop & Capture**: Click the "Stop & Capture" button when you see a combination you love
3. **Get Your URL**: The app will process your capture and provide a shareable URL
4. **Share**: Copy the URL and share your unique palette with others!

### Keyboard Shortcuts

- **Spacebar**: Stop and capture the current gradient
- **Escape**: Close modal dialogs

### Mobile Support

- **Long Press**: Hold the screen for 500ms to capture (equivalent to spacebar)
- **Touch Optimized**: All buttons and interactions work perfectly on mobile

## 🎨 Color Science

This app uses the **LAB color space** instead of RGB or HSV because:

- **Perceptual Uniformity**: Equal changes in LAB values correspond to equal changes in perceived color
- **Better Harmony**: Colors selected from LAB space naturally work well together
- **Professional Grade**: Used in graphic design and color matching industries

The included palette contains 20 carefully selected colors that ensure beautiful combinations every time.

## 🛠 Technical Details

### Frontend

- **HTML5 Canvas**: Using html2canvas for image capture
- **CSS3 Animations**: GPU-accelerated transforms and gradients
- **Vanilla JavaScript**: No frameworks, pure performance
- **Service Worker**: Offline support and caching

### Backend

- **Node.js + Express**: RESTful API server
- **Multer**: File upload handling
- **Crypto**: Secure unique filename generation
- **CORS**: Cross-origin resource sharing support

### Animation Techniques

- **Multiple Layers**: Radial, conic, and linear gradients
- **Staggered Timing**: Different animation speeds for organic feel
- **Transform Optimization**: Using `transform` instead of layout-triggering properties
- **Blend Modes**: CSS blend modes for color interaction

## 📁 Project Structure

```text
plot&palette/
├── index.html          # Main HTML file
├── styles.css          # All CSS styles and animations
├── script.js           # Frontend JavaScript
├── server.js           # Backend Express server
├── package.json        # Node.js dependencies
├── sw.js              # Service worker for caching
├── README.md          # This file
└── uploads/           # Generated images (created automatically)
```

## 🔧 Configuration

### Environment Variables

```bash
PORT=3000              # Server port (default: 3000)
NODE_ENV=production    # Environment mode
```

### Customization

- **Colors**: Edit the `LAB_COLORS` array in `script.js`
- **Animation Speed**: Modify CSS animation durations in `styles.css`
- **File Limits**: Adjust upload limits in `server.js`

## 🚀 Deployment

### Local Development

```bash
npm run dev
```

### Production

```bash
npm start
```

### Docker (Optional)

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## 🎯 Performance Optimizations

- **GPU Acceleration**: All transforms use `transform3d` for hardware acceleration
- **Efficient Selectors**: Minimal DOM queries and event listeners
- **Image Compression**: Optimized PNG output for smaller file sizes
- **Caching Strategy**: Service worker caches static assets
- **Reduced Motion**: Respects user's motion preferences

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests!

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- **html2canvas** for excellent screenshot capabilities
- **Express.js** for the robust backend framework
- **LAB Color Space** research for the color science foundation

---

Created with ❤️ for color enthusiasts and digital artists
