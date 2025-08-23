import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import FilterBar from '../FilterBar';

describe('FilterBar', () => {
  it('renders and calls onChange when inputs change', () => {
    const initial = {};
    const handleChange = vi.fn();
    render(<FilterBar value={initial} onChange={handleChange} />);

    // District select exists
    const districtLabel = screen.getByLabelText(/District/i);
    expect(districtLabel).toBeInTheDocument();

    fireEvent.change(districtLabel, { target: { value: 'Cầu Giấy' } });
    expect(handleChange).toHaveBeenCalled();
  });
});
