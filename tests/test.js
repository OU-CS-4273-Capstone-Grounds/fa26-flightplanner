import { calculateDensityAltitude } from '../performance';

test('calculateDensityAltitude returns correct density altitude', () => {
  const result = calculateDensityAltitude(2500, 25);
  expect(result).toBeCloseTo(4300, 0);
});