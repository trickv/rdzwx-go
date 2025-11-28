#!/usr/bin/env node

/**
 * Cordova hook to copy version.json into www/ before build
 * This allows the app to read its own version locally
 */

const fs = require('fs');
const path = require('path');

module.exports = function(context) {
    const projectRoot = context.opts.projectRoot;
    const sourceFile = path.join(projectRoot, 'version.json');
    const destFile = path.join(projectRoot, 'www', 'version.json');

    if (!fs.existsSync(sourceFile)) {
        console.error('ERROR: version.json not found in project root');
        process.exit(1);
    }

    console.log('Copying version.json to www/');
    fs.copyFileSync(sourceFile, destFile);
    console.log('version.json copied successfully');
};
