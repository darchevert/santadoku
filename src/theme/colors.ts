/** Winter-night palette for the Santadoku theme: deep midnight-blue sky,
 * snowy cream cards for contrast, holly green as the primary accent and
 * golden star yellow as the secondary one. Berry red is kept for errors. */
export const colors = {
  background: '#16283F',
  surface: '#FBF6EA',
  surfaceMuted: '#EBE3CF',
  ink: '#1F2A3D',
  inkSoft: '#5E6B80',
  accent: '#3DAA5C',
  accentDark: '#2B7F43',
  accentSecondary: '#F2C14E',
  success: '#2E9D5B',
  danger: '#D6453F',
  cardShadow: 'rgba(5, 12, 25, 0.35)',
} as const;

/** Palette for puzzle regions (the village "quartiers"). Chosen to be
 * distinguishable at a glance (including for common forms of color-blindness)
 * at up to 10 regions, while staying in the Christmas family. */
export const regionPalette = [
  '#5DB075', // holly green
  '#E0675F', // berry red
  '#F2C14E', // star gold
  '#6FA8DC', // ice blue
  '#B58BD6', // lavender
  '#F29E6B', // ginger orange
  '#8FD3C8', // mint
  '#D98BB5', // candy pink
  '#C9B28A', // gingerbread
  '#9CB3C9', // frost
] as const;

export function regionColor(regionId: number): string {
  return regionPalette[regionId % regionPalette.length];
}
