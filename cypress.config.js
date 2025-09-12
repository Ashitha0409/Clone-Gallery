import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    responseTimeout: 15000,
    pageLoadTimeout: 30000,

    // Test file patterns
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',

    // Support file
    supportFile: 'cypress/support/e2e.js',

    // Screenshots and videos
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',

    // Coverage
    experimentalWebKitSupport: true,

    setupNodeEvents(on, config) {
      // Coverage setup
      require('@cypress/code-coverage/task')(on, config);

      // Lighthouse audit
      on('task', {
        lighthouse: require('./cypress/plugins/lighthouse'),
      });

      // Custom tasks
      on('task', {
        log(message) {
          console.log(message);
          return null;
        },

        // Database seeding for tests
        seedDatabase() {
          // Add database seeding logic
          return null;
        },

        // Clean up test data
        cleanupTestData() {
          // Add cleanup logic
          return null;
        }
      });

      return config;
    },

    // Environment variables
    env: {
      coverage: true,
      ADMIN_EMAIL: 'admin@clonegallery.local',
      ADMIN_PASSWORD: 'admin123',
      TEST_USER_EMAIL: 'test@clonegallery.local',
      TEST_USER_PASSWORD: 'password123',
      API_BASE_URL: 'http://localhost/api',
    }
  },

  component: {
    devServer: {
      framework: 'laravel',
      bundler: 'vite',
    },
    specPattern: 'resources/js/**/*.cy.{js,jsx,ts,tsx}',
  },

  // Global configuration
  retries: {
    runMode: 2,
    openMode: 0
  },

  // Browser configuration
  chromeWebSecurity: false,

  // Test isolation
  testIsolation: true,

  // Experimental features
  experimentalStudio: true,
  experimentalRunAllSpecs: true,
})
