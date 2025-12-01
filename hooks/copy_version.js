#!/usr/bin/env node

/**
 * Cordova hook to convert version.json into version.js before build
 * This allows the app to read its version via a script tag (works on iOS)
 */

const fs = require('fs');
const path = require('path');

module.exports = function(context) {
    const projectRoot = context.opts.projectRoot;
    const sourceFile = path.join(projectRoot, 'version.json');
    const destFile = path.join(projectRoot, 'www', 'version.js');

    if (!fs.existsSync(sourceFile)) {
        console.error('ERROR: version.json not found in project root');
        process.exit(1);
    }

    console.log('Converting version.json to version.js...');
    const versionData = fs.readFileSync(sourceFile, 'utf8');
    const versionJs = `// Auto-generated version file\nwindow.APP_VERSION = ${versionData};\n`;

    fs.writeFileSync(destFile, versionJs);
    console.log('version.js created successfully');
};
