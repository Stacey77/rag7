/**
 * Channel data loader utility
 * Loads the full channel dataset from channels.full.json
 * 
 * Supports both require() and fs-based loading for compatibility
 * with different environments (Node.js, bundlers, etc.)
 */

const fs = require('fs');
const path = require('path');

/**
 * Load all channels from the channels.full.json file
 * @returns {Array} Array of channel objects
 */
function loadChannels() {
  try {
    // Try require() first (works in Node.js and most bundlers)
    const channels = require('../data/channels.full.json');
    return channels;
  } catch (requireError) {
    // Fallback to fs for environments that don't support require-ing JSON
    try {
      const channelsPath = path.join(__dirname, '../data/channels.full.json');
      const channelsData = fs.readFileSync(channelsPath, 'utf8');
      return JSON.parse(channelsData);
    } catch (fsError) {
      console.error('Failed to load channels:', requireError, fsError);
      throw new Error('Unable to load channels.full.json. Ensure the file exists at src/data/channels.full.json');
    }
  }
}

module.exports = { loadChannels };
