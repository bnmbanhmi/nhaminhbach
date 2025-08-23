import { renderHook, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useDebouncedValue } from '../useDebouncedValue';
import React from 'react';

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

describe('useDebouncedValue', () => {
  it('debounces changes and returns updated value after delay', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebouncedValue(value, delay),
      { initialProps: { value: 'a', delay: 50 } }
    );

    expect(result.current).toBe('a');

    // update prop rapidly
    rerender({ value: 'ab', delay: 50 });
    rerender({ value: 'abc', delay: 50 });

    // still old immediately
    expect(result.current).toBe('a');

    // wait for debounce
    await act(async () => {
      await sleep(60);
    });

    expect(result.current).toBe('abc');
  });
});
