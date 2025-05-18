const core = require('@actions/core');
const github = require('@actions/github');
const yaml = require('js-yaml');
const toml = require('toml');
const ini = require('ini');

// Define manifest file patterns for different languages
const MANIFEST_PATTERNS = {
  python: ['requirements.txt', 'Pipfile', 'Pipfile.lock', 'pyproject.toml'],
  javascript: ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
  java: ['pom.xml', 'build.gradle', 'build.gradle.kts'],
  csharp: ['.csproj', 'packages.config'],
  php: ['composer.json', 'composer.lock'],
  cpp: ['conanfile.txt', 'vcpkg.json', 'CMakeLists.txt'],
  go: ['go.mod', 'go.sum'],
  ruby: ['Gemfile', 'Gemfile.lock'],
  kotlin: ['build.gradle', 'build.gradle.kts', 'pom.xml'],
  swift: ['Package.swift', 'Podfile', 'Podfile.lock'],
  rust: ['Cargo.toml', 'Cargo.lock']
};

// Function to parse different manifest file formats
async function parseManifestFile(content, filename) {
  try {
    if (filename.endsWith('.json')) {
      return JSON.parse(content);
    } else if (filename.endsWith('.yaml') || filename.endsWith('.yml')) {
      return yaml.load(content);
    } else if (filename.endsWith('.toml')) {
      return toml.parse(content);
    } else if (filename.endsWith('.lock')) {
      // Handle lock files based on their type
      if (filename === 'package-lock.json') {
        return JSON.parse(content);
      } else if (filename === 'yarn.lock') {
        return yaml.load(content);
      }
    } else if (filename === 'requirements.txt') {
      // Parse requirements.txt format
      return content.split('\n')
        .filter(line => line.trim() && !line.startsWith('#'))
        .map(line => line.split('==')[0].trim());
    }
    // Add more parsers for other file types as needed
    return null;
  } catch (error) {
    core.warning(`Failed to parse ${filename}: ${error.message}`);
    return null;
  }
}

// Function to extract dependencies from parsed content
function extractDependencies(parsedContent, filename) {
  const dependencies = new Set();

  if (!parsedContent) return dependencies;

  if (filename === 'package.json') {
    const deps = parsedContent.dependencies || {};
    const devDeps = parsedContent.devDependencies || {};
    Object.keys(deps).forEach(dep => dependencies.add(dep));
    Object.keys(devDeps).forEach(dep => dependencies.add(dep));
  } else if (filename === 'requirements.txt') {
    parsedContent.forEach(dep => dependencies.add(dep));
  }
  // Add more extractors for other file types

  return dependencies;
}

async function run() {
  try {
    const token = core.getInput('github-token');
    const octokit = github.getOctokit(token);
    const context = github.context;

    if (!context.payload.pull_request) {
      core.setFailed('This action must be run on a pull request');
      return;
    }

    const { owner, repo } = context.repo;
    const pull_number = context.payload.pull_request.number;

    // Get the diff of the PR
    const { data: diff } = await octokit.rest.pulls.get({
      owner,
      repo,
      pull_number,
      mediaType: {
        format: 'diff'
      }
    });

    // Process the diff to find changed manifest files
    const changedFiles = diff.split('\n')
      .filter(line => line.startsWith('diff --git'))
      .map(line => line.split(' ')[2].substring(2));

    const newDependencies = new Map();

    for (const file of changedFiles) {
      // Check if the file is a manifest file
      const isManifest = Object.values(MANIFEST_PATTERNS)
        .flat()
        .some(pattern => file.endsWith(pattern));

      if (isManifest) {
        // Get the file content
        const { data: fileContent } = await octokit.rest.repos.getContent({
          owner,
          repo,
          path: file,
          ref: context.payload.pull_request.head.sha
        });

        const content = Buffer.from(fileContent.content, 'base64').toString();
        const parsedContent = await parseManifestFile(content, file);
        const dependencies = extractDependencies(parsedContent, file);

        if (dependencies.size > 0) {
          newDependencies.set(file, Array.from(dependencies));
        }
      }
    }

    // Output the results
    if (newDependencies.size > 0) {
      let output = 'New dependencies detected:\n\n';
      for (const [file, deps] of newDependencies) {
        output += `${file}:\n`;
        deps.forEach(dep => output += `  - ${dep}\n`);
        output += '\n';
      }
      core.setOutput('new_dependencies', output);
      core.notice(output);
    } else {
      core.notice('No new dependencies detected');
    }

  } catch (error) {
    core.setFailed(error.message);
  }
}

// Export functions for testing
module.exports = {
  parseManifestFile,
  extractDependencies,
  run
};

// Run the action if this file is executed directly
if (require.main === module) {
  run();
}