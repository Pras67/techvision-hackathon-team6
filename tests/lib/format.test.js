import { pct } from '../../src/lib/format.js';

describe('pct', () => {
  test('converts a decimal to percentage', () => {
    expect(pct(0.2)).toBe('20.0%');
  });

  test('converts another decimal to percentage', () => {
    expect(pct(0.5)).toBe('50.0%');
  });

  test('uses custom decimal precision', () => {
    expect(pct(0.256, 2)).toBe('25.60%');
  });

  test('handles zero', () => {
    expect(pct(0)).toBe('0.0%');
  });

  test('handles negative values', () => {
    expect(pct(-0.25)).toBe('-25.0%');
  });
});
