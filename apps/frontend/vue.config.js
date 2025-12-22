const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  outputDir: 'dist',
  assetsDir: 'static',
  productionSourceMap: false,
  
  devServer: {
    port: 8080,
    hot: true,
    open: false,
    proxy: {
      '/api': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
        ws: false,
        logLevel: 'debug',
        // Strip the /api prefix so that /api/health -> /health on the backend
        pathRewrite: { '^/api': '' }
      }
    }
  },
  
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
      }
    }
  },
  
  chainWebpack: config => {
    // Disable prefetch/preload for faster builds
    config.plugins.delete('prefetch')
    config.plugins.delete('preload')
    
    // Optimize build performance
    config.resolve.symlinks(false)
  }
})
