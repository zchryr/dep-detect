const { parseManifestFile, extractDependencies } = require('./index');

describe('Dependency Detection', () => {
  describe('parseManifestFile', () => {
    test('parses package.json correctly', async () => {
      const content = JSON.stringify({
        dependencies: { express: '^4.18.2' },
        devDependencies: { jest: '^29.7.0' }
      });
      const result = await parseManifestFile(content, 'package.json');
      expect(result).toHaveProperty('dependencies.express');
      expect(result).toHaveProperty('devDependencies.jest');
    });

    test('parses requirements.txt correctly', async () => {
      const content = 'requests==2.31.0\npytest==7.4.3';
      const result = await parseManifestFile(content, 'requirements.txt');
      expect(result).toContain('requests');
      expect(result).toContain('pytest');
    });
  });

  describe('extractDependencies', () => {
    test('extracts dependencies from package.json', () => {
      const content = {
        dependencies: { express: '^4.18.2' },
        devDependencies: { jest: '^29.7.0' }
      };
      const deps = extractDependencies(content, 'package.json');
      expect(deps).toContain('express');
      expect(deps).toContain('jest');
    });

    test('extracts dependencies from requirements.txt', () => {
      const content = ['requests', 'pytest'];
      const deps = extractDependencies(content, 'requirements.txt');
      expect(deps).toContain('requests');
      expect(deps).toContain('pytest');
    });
  });
});