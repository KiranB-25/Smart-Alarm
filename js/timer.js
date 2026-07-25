/** Countdown timer controller. */
import { query } from './utils.js';
import { showToast } from './ui.js';

/** Accurate countdown controller based on a target timestamp. */
export class TimerController {
  /** @param {import('./audio.js').AudioController} audio @param {{settings: object}} state */
  constructor(audio, state) { this.audio = audio; this.state = state; this.remaining = 0; this.endsAt = null; this.frameId = null; this.soundTimeout = null; this.bind(); this.render(); }
  bind() {
    query('#timer-start').addEventListener('click', () => this.startOrPause());
    query('#timer-reset').addEventListener('click', () => this.reset());
  }
  startOrPause() { if (this.endsAt !== null) { this.pause(); return; } window.clearTimeout(this.soundTimeout); this.audio.stop(); if (!this.remaining) this.remaining = this.readInputs(); if (!this.remaining) { showToast('Set a timer longer than zero seconds.', 'error'); return; } this.endsAt = performance.now() + this.remaining; this.setInputsDisabled(true); query('#timer-start').textContent = 'Pause'; query('#timer-start').setAttribute('aria-label', 'Pause countdown timer'); this.tick(); }
  pause() { this.remaining = Math.max(0, this.endsAt - performance.now()); this.endsAt = null; cancelAnimationFrame(this.frameId); this.frameId = null; query('#timer-start').textContent = 'Resume'; query('#timer-start').setAttribute('aria-label', 'Resume countdown timer'); this.render(); }
  tick() { if (this.endsAt === null) return; this.remaining = Math.max(0, this.endsAt - performance.now()); this.render(); if (!this.remaining) { this.complete(); return; } this.frameId = requestAnimationFrame(() => this.tick()); }
  async complete() { this.endsAt = null; cancelAnimationFrame(this.frameId); this.frameId = null; this.setInputsDisabled(false); query('#timer-start').textContent = 'Start'; query('#timer-start').setAttribute('aria-label', 'Start countdown timer'); this.render(); showToast('Timer complete.', 'success'); try { await this.audio.play(this.state.settings.defaultTone); this.soundTimeout = window.setTimeout(() => this.audio.stop(), 8000); } catch (error) { console.warn('Timer completion sound could not play.', error); } }
  reset() { cancelAnimationFrame(this.frameId); window.clearTimeout(this.soundTimeout); this.audio.stop(); this.remaining = 0; this.endsAt = null; this.frameId = null; this.setInputsDisabled(false); query('#timer-start').textContent = 'Start'; query('#timer-start').setAttribute('aria-label', 'Start countdown timer'); this.render(); }
  readInputs() { const hours = this.readNumber('#timer-hours', 99); const minutes = this.readNumber('#timer-minutes', 59); const seconds = this.readNumber('#timer-seconds', 59); return ((hours * 3600) + (minutes * 60) + seconds) * 1000; }
  readNumber(selector, max) { const input = query(selector); const value = Number(input.value); if (!Number.isInteger(value) || value < 0) return 0; if (value > max) { input.value = String(max); return max; } return value; }
  setInputsDisabled(disabled) { for (const input of document.querySelectorAll('[data-timer-input]')) input.disabled = disabled; }
  render() { const totalSeconds = Math.ceil(this.remaining / 1000); const hours = Math.floor(totalSeconds / 3600); const minutes = Math.floor(totalSeconds / 60) % 60; const seconds = totalSeconds % 60; query('#timer-display').innerHTML = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`; }
}
