// GIF Preloader Service
class GifPreloader {
  constructor() {
    this.preloadedGifs = []
    this.currentBatch = []
    this.isLoading = false
    this.playHistory = []
    this.currentPlayIndex = 0
  }

  // Get available GIF paths from R2 (1-20)
  async getAllGifPaths() {
    const gifPaths = []
    const MAX_GIFS = 20
    for (let i = 1; i <= MAX_GIFS; i++) {
      // Use R2 bucket URLs via our API endpoint
      gifPaths.push(`/api/assets/palettes/${i}.gif`)
    }
    return gifPaths
  }

  // Preload initial batch of GIFs for immediate playback
  async preloadInitialGifs(count = 3) {
    if (this.isLoading) {
      console.log('⏳ Already preloading GIFs...')
      return this.preloadedGifs
    }

    this.isLoading = true
    console.log(`🎯 Preloading initial batch of ${count} GIFs...`)

    try {
      // Get all available GIF paths
      const allGifPaths = await this.getAllGifPaths()
      console.log(`📁 Found ${allGifPaths.length} available GIFs`)

      // Load first 3 GIFs (1.gif, 2.gif, 3.gif)
      const selectedGifs = allGifPaths.slice(0, count)

      // Preload the selected GIFs
      const preloadPromises = selectedGifs.map(gifPath => this.preloadSingleGif(gifPath))
      const results = await Promise.allSettled(preloadPromises)

      // Filter successful loads
      this.preloadedGifs = results
        .filter(result => result.status === 'fulfilled')
        .map(result => result.value)

      // Store remaining GIFs for future loading
      this.remainingGifs = allGifPaths.slice(count)

      console.log(`✅ Successfully preloaded ${this.preloadedGifs.length}/${count} initial GIFs`)
      
      this.isLoading = false
      return this.preloadedGifs

    } catch (error) {
      console.error('❌ Error preloading initial GIFs:', error)
      this.isLoading = false
      return []
    }
  }

  // Preload next GIF while current one is playing (sequential)
  async preloadNextGif() {
    if (this.isLoading || !this.remainingGifs || this.remainingGifs.length === 0) {
      return null
    }

    console.log('🔄 Preloading next GIF in sequence...')
    this.isLoading = true

    try {
      // Get next GIF from remaining pool
      const nextGifPath = this.remainingGifs.shift()
      const preloadedGif = await this.preloadSingleGif(nextGifPath)
      
      // Add to preloaded pool
      this.preloadedGifs.push(preloadedGif)
      
      console.log(`✅ Preloaded next GIF: ${preloadedGif}`)
      console.log(`📊 Pool status: ${this.preloadedGifs.length} loaded, ${this.remainingGifs.length} remaining`)
      
      this.isLoading = false
      return preloadedGif

    } catch (error) {
      console.error('❌ Error preloading next GIF:', error)
      this.isLoading = false
      return null
    }
  }

  // Preload a single GIF
  preloadSingleGif(gifPath) {
    return new Promise((resolve, reject) => {
      const img = new Image()
      
      img.onload = () => {
        console.log('✅ Preloaded GIF:', gifPath)
        resolve(gifPath)
      }
      
      img.onerror = () => {
        console.error('❌ Failed to preload GIF:', gifPath)
        reject(new Error(`Failed to load ${gifPath}`))
      }
      
      img.src = gifPath
    })
  }

  // Get next GIF to display (and trigger preloading of the next one)
  getNextGif() {
    if (this.preloadedGifs.length === 0) {
      console.log('⚠️ No preloaded GIFs available')
      return null
    }

    // Get the next GIF to display
    const nextGif = this.preloadedGifs[this.currentPlayIndex % this.preloadedGifs.length]
    this.currentPlayIndex++

    // Trigger preloading of next GIF in background
    setTimeout(() => {
      this.preloadNextGif()
    }, 1000) // Start preloading 1 second after current GIF starts

    console.log('🎬 Next GIF to display:', nextGif)
    return nextGif
  }

  // Check if GIFs are ready for playback
  isReady() {
    return this.preloadedGifs.length > 0 && !this.isLoading
  }

  // Get all currently preloaded GIFs
  getPreloadedGifs() {
    return [...this.preloadedGifs]
  }

  // Reset the preloader
  reset() {
    this.preloadedGifs = []
    this.currentBatch = []
    this.remainingGifs = []
    this.playHistory = []
    this.currentPlayIndex = 0
    this.isLoading = false
    console.log('🔄 GIF preloader reset')
  }

  // Legacy method for backward compatibility
  async preloadRandomGifs(count = 3) {
    return await this.preloadInitialGifs(count)
  }
}

// Export singleton instance
export default new GifPreloader()
