import React from 'react';
import { Range } from 'react-range';

type Props = {
  min: number;
  max: number;
  step?: number;
  values: [number, number];
  onChange: (v: [number, number]) => void;
  format?: (n: number) => string;
};

/**
 * DualRange
 * Lightweight, accessible dual-thumb range built on `react-range`.
 * - Props are strongly typed
 * - Renders a single track with a filled active range
 * - Smooth dragging on pointer and touch devices
 * - Small and themeable via Tailwind + inline colors
 */
const DualRange: React.FC<Props> = ({ min, max, step = 1, values, onChange, format }) => {
  const primary = '#60A5FA'; // theme primary (light-blue)

  return (
    <div className="w-full py-3">
      <Range
        step={step}
        min={min}
        max={max}
        values={values}
        onChange={(v) => onChange([v[0], v[1]] as [number, number])}
    renderTrack={({ props, children }) => (
          <div
            {...props}
            onMouseDown={props.onMouseDown}
            onTouchStart={props.onTouchStart}
            className="w-full h-3 flex items-center"
            style={{ ...props.style }}
          >
            <div className="relative w-full h-2 bg-gray-200 rounded" style={{ height: 10 }}>
              {/* active range */}
              <div
                className="absolute h-2 rounded"
                style={{
                  left: `${((values[0] - min) / (max - min)) * 100}%`,
                  width: `${((values[1] - values[0]) / (max - min)) * 100}%`,
          background: primary,
          transition: 'left 0.06s linear, width 0.06s linear',
                  top: 0,
                }}
              />
              {children}
            </div>
          </div>
        )}
    renderThumb={({ index, props }) => (
          <div
            {...props}
            role="slider"
            aria-valuemin={min}
            aria-valuemax={max}
            aria-valuenow={values[index]}
            className="relative"
      style={{ ...props.style, height: 28, width: 28, display: 'flex', alignItems: 'center', justifyContent: 'center', touchAction: 'none' }}
          >
            <div
              style={{
                height: 20,
                width: 20,
                borderRadius: '50%',
                background: '#fff',
                border: `3px solid ${primary}`,
                boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
                transform: 'translateY(-6px)'
              }}
            />
            {/* tooltip */}
            <div style={{ position: 'absolute', top: -30, left: '50%', transform: 'translateX(-50%)', fontSize: 12 }}>
              {format ? format(values[index]) : values[index]}
            </div>
          </div>
        )}
      />
    </div>
  );
};

export default DualRange;
