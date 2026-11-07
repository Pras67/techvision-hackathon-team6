module.exports = {
  testEnvironment: 'jsdom',

  transform: {
    '^.+\\.[jt]sx?$': 'babel-jest',
  },

  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],

  testMatch: [
    '**/tests/**/*.test.[jt]s?(x)',
  ],
};
