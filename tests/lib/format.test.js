import { pct,hourLabel,money, count} from '../../src/lib/format.js';

//tests unit conversion
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

//test hour number converts
describe('hourLabel', () => {
  test('formats a single-digit hour with a leading zero', () => {
    expect(hourLabel(9)).toBe('09:00–10:00');
  });

  test('formats a double-digit hour', () => {
    expect(hourLabel(14)).toBe('14:00–15:00');
  });

  test('formats midnight correctly', () => {
    expect(hourLabel(0)).toBe('00:00–01:00');
  });

  test('returns a dash when the hour is null', () => {
    expect(hourLabel(null)).toBe('–');
  });

  test('returns a dash when the hour is undefined', () => {
    expect(hourLabel(undefined)).toBe('–');
  });
});

//tests pounds sterling
describe('money', () => {
  test('formats a small amount as GBP', () => {
    expect(money(50)).toBe('£50');
  });

  test('formats thousands with commas', () => {
    expect(money(1250)).toBe('£1,250');
  });

  test('formats amounts below 100000 without compact notation', () => {
    expect(money(99999)).toBe('£99,999');
  });

  test('uses compact notation for amounts of 100000 or more', () => {
    expect(money(100000)).toBe('£100k');
  });

  test('preserves the negative sign for large amounts', () => {
    expect(money(-150000)).toBe('\u2212£150k');
  });
});

//tests count functions
describe('count', () => {
  test('formats an integer', () => {
    expect(count(100)).toBe('100');
  });

  test('adds commas to thousands', () => {
    expect(count(1500)).toBe('1,500');
  });

  test('rounds decimal numbers up', () => {
    expect(count(10.6)).toBe('11');
  });

  test('rounds decimal numbers down', () => {
    expect(count(10.2)).toBe('10');
  });

  test('formats zero', () => {
    expect(count(0)).toBe('0');
  });
});
