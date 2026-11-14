// Draws the app icons (Christmas tree on a snowy midnight sky) as plain
// vector shapes rasterized with 3x3 supersampling: no third-party artwork.
// Run with `node scripts/generate-icons.mjs` (needs the `pngjs` dev dependency).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';

const OUT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'assets');
const SS = 3;

function hex(c, a = 1) {
  return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16), a];
}

class Canvas {
  constructor(size) {
    this.size = size;
    this.n = size * SS;
    this.px = new Float32Array(this.n * this.n * 4); // premultiplied-free RGBA, 0..255 / alpha 0..1
  }
  blend(i, [r, g, b, a]) {
    const p = this.px;
    const da = p[i + 3];
    const oa = a + da * (1 - a);
    if (oa <= 0) return;
    p[i] = (r * a + p[i] * da * (1 - a)) / oa;
    p[i + 1] = (g * a + p[i + 1] * da * (1 - a)) / oa;
    p[i + 2] = (b * a + p[i + 2] * da * (1 - a)) / oa;
    p[i + 3] = oa;
  }
  /** Fills every sub-pixel where inside(x, y) holds; coordinates in 0..1. */
  fill(inside, color, bbox = [0, 0, 1, 1]) {
    const n = this.n;
    const x0 = Math.max(0, Math.floor(bbox[0] * n));
    const y0 = Math.max(0, Math.floor(bbox[1] * n));
    const x1 = Math.min(n - 1, Math.ceil(bbox[2] * n));
    const y1 = Math.min(n - 1, Math.ceil(bbox[3] * n));
    for (let y = y0; y <= y1; y++) {
      for (let x = x0; x <= x1; x++) {
        const c = typeof color === 'function' ? color(x / n, y / n) : color;
        if (inside((x + 0.5) / n, (y + 0.5) / n)) this.blend((y * n + x) * 4, c);
      }
    }
  }
  circle(cx, cy, r, color) {
    this.fill((x, y) => (x - cx) ** 2 + (y - cy) ** 2 <= r * r, color, [cx - r, cy - r, cx + r, cy + r]);
  }
  poly(points, color) {
    const xs = points.map((p) => p[0]);
    const ys = points.map((p) => p[1]);
    this.fill(
      (x, y) => {
        let inside = false;
        for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
          const [xi, yi] = points[i];
          const [xj, yj] = points[j];
          if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
        }
        return inside;
      },
      color,
      [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]
    );
  }
  roundRect(x0, y0, x1, y1, r, color) {
    this.fill(
      (x, y) => {
        const dx = Math.max(x0 + r - x, 0, x - (x1 - r));
        const dy = Math.max(y0 + r - y, 0, y - (y1 - r));
        return x >= x0 && x <= x1 && y >= y0 && y <= y1 && dx * dx + dy * dy <= r * r;
      },
      color,
      [x0, y0, x1, y1]
    );
  }
  star(cx, cy, rOuter, rInner, color) {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const a = -Math.PI / 2 + (i * Math.PI) / 5;
      const r = i % 2 === 0 ? rOuter : rInner;
      pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]);
    }
    this.poly(pts, color);
  }
  png(file, flatten = null) {
    const out = new PNG({ width: this.size, height: this.size });
    const n = this.n;
    for (let y = 0; y < this.size; y++) {
      for (let x = 0; x < this.size; x++) {
        let r = 0, g = 0, b = 0, a = 0;
        for (let sy = 0; sy < SS; sy++) {
          for (let sx = 0; sx < SS; sx++) {
            const i = ((y * SS + sy) * n + (x * SS + sx)) * 4;
            const pa = this.px[i + 3];
            r += this.px[i] * pa;
            g += this.px[i + 1] * pa;
            b += this.px[i + 2] * pa;
            a += pa;
          }
        }
        const cnt = SS * SS;
        const o = (y * this.size + x) * 4;
        if (a > 0) {
          out.data[o] = Math.round(r / a);
          out.data[o + 1] = Math.round(g / a);
          out.data[o + 2] = Math.round(b / a);
        }
        out.data[o + 3] = Math.round((a / cnt) * 255);
      }
    }
    fs.writeFileSync(path.join(OUT, file), PNG.sync.write(out));
    console.log('wrote', file);
  }
}

/** Midnight-blue vertical gradient with a soft glow and falling snow. */
function drawSky(c) {
  c.fill(() => true, (x, y) => {
    const t = y;
    const glow = Math.max(0, 1 - Math.hypot(x - 0.5, y - 0.55) / 0.75);
    const r = 14 + t * 18 + glow * 22;
    const g = 28 + t * 30 + glow * 34;
    const b = 58 + t * 36 + glow * 44;
    return [r, g, b, 1];
  });
  let seed = 11;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 46; i++) {
    c.circle(rnd(), rnd(), 0.004 + rnd() * 0.008, hex('#FFFFFF', 0.55 + rnd() * 0.35));
  }
}

/** The tree itself. `scale` shrinks it for the adaptive-icon safe zone. */
function drawTree(c, scale = 1, mono = false) {
  const S = (v, o) => 0.5 + (v - 0.5) * scale + (o ?? 0);
  const X = (v) => S(v);
  const Y = (v) => 0.5 + (v - 0.5) * scale;
  const green = mono ? hex('#FFFFFF') : hex('#2F9E55');
  const greenDark = mono ? hex('#FFFFFF') : hex('#237A41');
  const trunk = mono ? hex('#FFFFFF') : hex('#8A5A3B');
  const gold = mono ? hex('#FFFFFF') : hex('#F7C948');

  // trunk
  c.roundRect(X(0.445), Y(0.76), X(0.555), Y(0.86), 0.01 * scale, trunk);
  // three stacked boughs (back to front)
  const tiers = [
    [0.18, 0.78, 0.5, 0.5],
    [0.24, 0.72, 0.5, 0.38],
    [0.32, 0.66, 0.5, 0.26],
  ];
  for (let i = 0; i < tiers.length; i++) {
    const [l, r, mx, top] = tiers[i];
    const bottom = [0.78, 0.66, 0.54][i];
    const pts = [
      [X(mx), Y(top - 0.06)],
      [X(r + 0.03), Y(bottom)],
      [X(mx), Y(bottom + 0.03)],
      [X(l - 0.03), Y(bottom)],
    ];
    c.poly(pts, i % 2 === 0 ? greenDark : green);
    // scalloped bottom edge
    for (let k = 0; k < 4; k++) {
      const cx = X(l - 0.03 + ((r - l + 0.06) * (k + 0.5)) / 4);
      c.circle(cx, Y(bottom + 0.005), 0.034 * scale + 0.004, i % 2 === 0 ? greenDark : green);
    }
  }
  // snow cap on the lowest bough edge
  if (!mono) {
    for (let k = 0; k < 5; k++) c.circle(X(0.2 + k * 0.15), Y(0.8), 0.018 * scale, hex('#FFFFFF', 0.9));
  }
  // baubles
  if (!mono) {
    const baubles = [
      [0.4, 0.74, '#E0463F'],
      [0.6, 0.72, '#F7C948'],
      [0.5, 0.64, '#6FA8DC'],
      [0.42, 0.52, '#F7C948'],
      [0.58, 0.5, '#E0463F'],
      [0.5, 0.4, '#FFFFFF'],
    ];
    for (const [bx, by, col] of baubles) {
      c.circle(X(bx), Y(by), 0.028 * scale, hex(col));
      c.circle(X(bx) - 0.008 * scale, Y(by) - 0.008 * scale, 0.008 * scale, hex('#FFFFFF', 0.7));
    }
  }
  // star
  c.star(X(0.5), Y(0.2), 0.085 * scale, 0.036 * scale, gold);
}

const SIZE = 1024;

// 1. Full icon (store + iOS): sky + tree.
{
  const c = new Canvas(SIZE);
  drawSky(c);
  drawTree(c, 1);
  c.png('icon.png');
}
// 2. Adaptive background: sky only.
{
  const c = new Canvas(SIZE);
  drawSky(c);
  c.png('android-icon-background.png');
}
// 3. Adaptive foreground: tree inside the 66% safe zone, transparent.
{
  const c = new Canvas(SIZE);
  drawTree(c, 0.66);
  c.png('android-icon-foreground.png');
}
// 4. Monochrome (themed icons): white silhouette.
{
  const c = new Canvas(SIZE);
  drawTree(c, 0.66, true);
  c.png('android-icon-monochrome.png');
}
// 5. Splash: tree on transparent, shown on the app background colour.
{
  const c = new Canvas(SIZE);
  drawTree(c, 0.8);
  c.png('splash-icon.png');
}
// 6. Favicon.
{
  const c = new Canvas(96);
  drawSky(c);
  drawTree(c, 1);
  c.png('favicon.png');
}
