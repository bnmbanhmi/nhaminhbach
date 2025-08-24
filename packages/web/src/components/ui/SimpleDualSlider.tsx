import React, { useRef, useEffect } from 'react';

type Props = {
  min: number;
  max: number;
  step?: number;
  values: [number, number];
  onChange: (v: [number, number]) => void;
  format?: (n: number) => string;
  ariaLabel?: string;
};

/**
 * SimpleDualSlider
 * - Two independently draggable thumbs implemented with pointer events
 * - Clicking the track picks the nearest thumb and drags it
 * - No external deps, keyboard handlers on thumbs for accessibility
 * - Removed top Min/Max lines (per request)
 */
const SimpleDualSlider: React.FC<Props> = ({ min, max, step = 1, values, onChange, format, ariaLabel }) => {
  const [left, right] = values;
  const trackRef = useRef<HTMLDivElement | null>(null);
  const draggingRef = useRef<'left' | 'right' | null>(null);
  const rafRef = useRef<number | null>(null);

  const clamp = (v: number) => Math.min(max, Math.max(min, v));

  const pctToValue = (pct: number) => {
  const raw = min + pct * (max - min);
    // quantize to step
    const stepped = Math.round(raw / step) * step;
    return clamp(stepped);
  };

  const posToPct = (clientX: number) => {
    const el = trackRef.current;
    if (!el) return 0;
    const rect = el.getBoundingClientRect();
    const x = clientX - rect.left;
    return Math.min(1, Math.max(0, x / rect.width));
  };

  const onPointerMove = (ev: PointerEvent) => {
    if (!draggingRef.current) return;
    // throttle via rAF
    if (rafRef.current) return;
    rafRef.current = window.requestAnimationFrame(() => {
      rafRef.current = null;
      const pct = posToPct(ev.clientX);
      const val = pctToValue(pct);
      if (draggingRef.current === 'left') {
        const newLeft = Math.min(val, right);
        onChange([newLeft, right]);
      } else {
        const newRight = Math.max(val, left);
        onChange([left, newRight]);
      }
    });
  };

  const onPointerUp = () => {
    draggingRef.current = null;
    if (rafRef.current) {
      window.cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
  };

  const startDrag = (which: 'left' | 'right', ev: React.PointerEvent) => {
    ev.preventDefault();
    draggingRef.current = which;
  // capture on the element receiving the pointer (currentTarget)
  (ev.currentTarget as Element).setPointerCapture?.(ev.pointerId);
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
  };

  const onTrackPointerDown = (ev: React.PointerEvent) => {
    // pick nearest thumb
    const pct = posToPct(ev.clientX);
    const clickedVal = pctToValue(pct);
    const dLeft = Math.abs(clickedVal - left);
    const dRight = Math.abs(clickedVal - right);
    const which = dLeft <= dRight ? 'left' : 'right';
    startDrag(which, ev);
  };

  // keyboard handlers on thumbs
  const thumbKeyDown = (which: 'left' | 'right') => (e: React.KeyboardEvent) => {
    const stepSize = step || 1;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
      e.preventDefault();
      if (which === 'left') onChange([clamp(left - stepSize), right]);
      else onChange([left, clamp(right - stepSize)]);
    } else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (which === 'left') onChange([clamp(left + stepSize <= right ? left + stepSize : right), right]);
      else onChange([left, clamp(right + stepSize)]);
    }
  };

  const leftPct = ((left - min) / (max - min)) * 100;
  const rightPct = ((right - min) / (max - min)) * 100;

  const accent = '#FF9900';
  const trackStyle: React.CSSProperties = {
    background: `linear-gradient(90deg, #e5e7eb ${leftPct}%, ${accent} ${leftPct}%, ${accent} ${rightPct}%, #e5e7eb ${rightPct}%)`
  };

  useEffect(() => {
    return () => {
      if (rafRef.current) window.cancelAnimationFrame(rafRef.current);
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', onPointerUp);
    };
  }, []);

  return (
    <div className="w-full py-3">
      <div
        ref={trackRef}
        className="relative h-8 flex items-center px-2"
        onPointerDown={onTrackPointerDown}
        style={{ touchAction: 'none' }}
      >
        <div className="absolute left-0 right-0 h-2 rounded-lg pointer-events-none" style={trackStyle} />

        {/* left thumb wrapper: larger hit area but visible circle centered on the track */}
        <div
          role="slider"
          tabIndex={0}
          aria-label={ariaLabel ? `${ariaLabel} lower` : 'Lower value'}
          aria-valuemin={min}
          aria-valuemax={max}
          aria-valuenow={left}
          onPointerDown={(e) => startDrag('left', e)}
          onKeyDown={thumbKeyDown('left')}
          className="absolute flex items-center justify-center"
          style={{ left: `${leftPct}%`, top: '50%', transform: 'translate(-50%,-50%)', zIndex: 3, touchAction: 'none', width: 32, height: 32 }}
        >
          <div className="w-4 h-4 rounded-full bg-[#FF9900] shadow" />
        </div>

        {/* right thumb wrapper */}
        <div
          role="slider"
          tabIndex={0}
          aria-label={ariaLabel ? `${ariaLabel} upper` : 'Upper value'}
          aria-valuemin={min}
          aria-valuemax={max}
          aria-valuenow={right}
          onPointerDown={(e) => startDrag('right', e)}
          onKeyDown={thumbKeyDown('right')}
          className="absolute flex items-center justify-center"
          style={{ left: `${rightPct}%`, top: '50%', transform: 'translate(-50%,-50%)', zIndex: 4, touchAction: 'none', width: 32, height: 32 }}
        >
          <div className="w-4 h-4 rounded-full bg-[#FF9900] shadow" />
        </div>
      </div>
      {/* bottom current values */}
      <div className="flex justify-between text-xs mt-1 text-gray-600 px-1">
        <div>{format ? format(left) : left}</div>
        <div>{format ? format(right) : right}</div>
      </div>
    </div>
  );
};

export default SimpleDualSlider;
