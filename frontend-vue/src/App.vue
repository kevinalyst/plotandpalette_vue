<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Poppins', sans-serif;
  background-color: #f5f5f5;
  overflow-x: hidden;
}

body.no-scroll {
  overflow: hidden;
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap');

/* Global utility classes */
.hidden {
  display: none !important;
}

/* Smooth transitions */
* {
  transition: all 0.3s ease;
}

/* Focus styles for accessibility */
button:focus,
input:focus,
select:focus,
textarea:focus {
  outline: 2px solid #4ecdc4;
  outline-offset: 2px;
}

/* Button reset */
button {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
}

/* Remove default link styling */
a {
  text-decoration: none;
  color: inherit;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 