#!/usr/bin/env node
/**
 * Type-safe type checking script that bypasses TS6310 project references error
 * on Lovable platform where tsconfig files are read-only.
 * 
 * This script creates a temporary tsconfig without project references for type checking.
 */

import { readFileSync, writeFileSync, unlinkSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');

try {
  // Read the original tsconfig.json
  const tsconfigPath = join(rootDir, 'tsconfig.json');
  const tsconfigContent = readFileSync(tsconfigPath, 'utf-8');
  const tsconfig = JSON.parse(tsconfigContent);
  
  // Remove project references to avoid TS6310 error
  const safeTsconfig = {
    ...tsconfig,
    references: undefined,
  };
  
  // Create a temporary tsconfig without references
  const tempTsconfigPath = join(rootDir, 'tsconfig.temp.json');
  writeFileSync(tempTsconfigPath, JSON.stringify(safeTsconfig, null, 2));
  
  try {
    // Run type checking with the temporary config
    console.log('Running type check without project references...');
    execSync(
      `tsc --noEmit --skipLibCheck --project ${tempTsconfigPath}`,
      { stdio: 'inherit', cwd: rootDir }
    );
    console.log('✓ Type check passed');
  } finally {
    // Clean up temporary file
    try {
      unlinkSync(tempTsconfigPath);
    } catch (e) {
      // Ignore cleanup errors
    }
  }
} catch (error) {
  console.error('Type check failed:', error.message);
  process.exit(1);
}

