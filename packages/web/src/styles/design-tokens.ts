/**
 * Design System Tokens for NhaMinhBach
 * 
 * These tokens define our brand colors, typography, and spacing.
 * Use these constants for consistent styling across the application.
 */

export const colors = {
  primary: '#F06D65',        // For main CTAs, links, highlights
  background: '#FDFBF7',     // Main page background
  surface: '#FFFFFF',        // Card and navbar backgrounds
  textPrimary: '#2C2C2C',    // Main text color
  textSecondary: '#757575',  // Subdued text for descriptions, metadata
  accentCool: '#6C8B9A',     // For specific tags or success states
} as const;

export const typography = {
  fontFamily: {
    sans: "'Inter', system-ui, sans-serif",
  },
} as const;

export const borderRadius = {
  card: '0.75rem',      // For larger elements like ListingCard
  button: '0.5rem',     // For smaller elements like buttons and tags
} as const;

/**
 * Tailwind CSS class mappings for our design tokens
 * Use these when you need arbitrary values in Tailwind classes
 */
export const tailwindClasses = {
  colors: {
    primary: 'bg-[#F06D65]',
    background: 'bg-[#FDFBF7]',
    surface: 'bg-[#FFFFFF]',
    textPrimary: 'text-[#2C2C2C]',
    textSecondary: 'text-[#757575]',
    accentCool: 'text-[#6C8B9A]',
  },
  borderRadius: {
    card: 'rounded-[0.75rem]',
    button: 'rounded-[0.5rem]',
  },
} as const;

export type DesignTokens = {
  colors: typeof colors;
  typography: typeof typography;
  borderRadius: typeof borderRadius;
};
