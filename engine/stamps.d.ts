export interface BrushSettings {
  /** Integer radius in backing pixels; CSS pixels for the 3D adapter. */
  radius: number;
  intensity: number;
  /** Fraction of radius between stamp centers, e.g. .05 = 5%. */
  spacing: number;
  accumulate: boolean;
  strokeType: 'dot' | 'drag';
}
export interface StampEngine {
  settings: BrushSettings;
  readonly active: boolean;
  readonly alphaCanvas: OffscreenCanvas | HTMLCanvasElement;
  sampleAlpha(u: number, v: number): number;
  handleStrokeStart(canvas: HTMLCanvasElement, event: PointerEvent): boolean;
  handleStrokeMove(canvas: HTMLCanvasElement, event: PointerEvent): boolean;
  handleStrokeEnd(canvas: HTMLCanvasElement, event: PointerEvent): boolean;
  cancel(): void;
}
export function createStampEngine(options?: {
  settings?: Partial<BrushSettings>;
  coordinateSpace?: 'pixels' | 'css';
  color?: [number, number, number];
  onStamp?: (x: number, y: number, pressure: number, settings: Readonly<BrushSettings>, alpha: (u: number, v: number) => number) => void;
}): StampEngine;
