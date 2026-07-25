/** Stopwatch and lap-time controller. */
import { query } from './utils.js';

/** Accurate stopwatch controller based on performance timestamps. */
export class StopwatchController {
  constructor() { this.elapsed = 0; this.startedAt = null; this.frameId = null; this.laps = []; this.bind(); this.render(); }
  bind() {
    query('#stopwatch-start').addEventListener('click', () => (this.startedAt === null ? this.start() : this.pause()));
    query('#stopwatch-lap').addEventListener('click', () => this.lap());
    query('#stopwatch-reset').addEventListener('click', () => this.reset());
  }
  start() { if (this.startedAt !== null) return; this.startedAt = performance.now() - this.elapsed; query('#stopwatch-start').textContent = this.elapsed ? 'Resume' : 'Pause'; query('#stopwatch-start').setAttribute('aria-label', 'Pause stopwatch'); this.tick(); }
  pause() { if (this.startedAt === null) return; this.elapsed = performance.now() - this.startedAt; this.startedAt = null; cancelAnimationFrame(this.frameId); this.frameId = null; query('#stopwatch-start').textContent = 'Resume'; query('#stopwatch-start').setAttribute('aria-label', 'Resume stopwatch'); this.render(); }
  tick() { if (this.startedAt === null) return; this.elapsed = performance.now() - this.startedAt; this.render(); this.frameId = requestAnimationFrame(() => this.tick()); }
  lap() { if (this.startedAt === null) return; this.laps.unshift(this.elapsed); this.renderLaps(); }
  reset() { cancelAnimationFrame(this.frameId); this.frameId = null; this.elapsed = 0; this.startedAt = null; this.laps = []; query('#stopwatch-start').textContent = 'Start'; query('#stopwatch-start').setAttribute('aria-label', 'Start stopwatch'); this.render(); this.renderLaps(); }
  render() { query('#stopwatch-display').innerHTML = this.format(this.elapsed); }
  renderLaps() { const list = query('#lap-list'); if (!this.laps.length) { list.innerHTML = '<li class="lap-empty">No laps recorded yet.</li>'; return; } list.innerHTML = this.laps.map((lap, index) => { const previous = this.laps[index + 1] ?? 0; return `<li class="lap-row"><span>Lap ${this.laps.length - index}</span><span>${this.format(lap - previous)}</span><span>${this.format(lap)}</span></li>`; }).join(''); }
  format(milliseconds) { const centiseconds = Math.floor(milliseconds / 10) % 100; const seconds = Math.floor(milliseconds / 1000) % 60; const minutes = Math.floor(milliseconds / 60000) % 60; const hours = Math.floor(milliseconds / 3600000); return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}<small>.${String(centiseconds).padStart(2, '0')}</small>`; }
}
