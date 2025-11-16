import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    // Test environment
    environment: 'jsdom',

    // Global setup
    globals: true,
    setupFiles: ['./src/tests/setup.ts'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        '**/dist/',
        '**/*.config.{ts,js}',
        '**/vite.config.ts',
        '**/vitest.config.ts',
      ],
      // Coverage thresholds
      lines: 70,
      functions: 70,
      branches: 65,
      statements: 70,
    },

    // Test file patterns
    include: [
      '**/__tests__/**/*.{test,spec}.{ts,tsx}',
      '**/*.{test,spec}.{ts,tsx}'
    ],
    exclude: [
      'node_modules',
      'dist',
      '.git',
      '.cache'
    ],

    // Reporter
    reporters: ['verbose', 'html'],
    outputFile: {
      html: './test-results/index.html',
    },

    // Performance
    threads: true,
    isolate: true,

    // Timeout
    testTimeout: 10000,
    hookTimeout: 10000,

    // Watch mode
    watch: false,

    // Mock configuration
    mockReset: true,
    clearMocks: true,
    restoreMocks: true,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@services': path.resolve(__dirname, './src/services'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
})
