/** Active ringing, snooze, and dismissal controller. */
import { escapeHtml, query } from './utils.js';

/** Presents and controls the full-screen active-alarm experience. */
export class RingingController {
  /** @param {import('./audio.js').AudioController} audio @param {{settings: object}} state @param {(alarm: object) => void} onSnooze */
  constructor(audio, state, onSnooze) { this.audio = audio; this.state = state; this.onSnooze = onSnooze; this.activeAlarm = null; this.timerId = null; this.lastFocused = null; this.bind(); }
  bind() {
    query('#ring-snooze').addEventListener('click', () => this.snooze());
    query('#ring-dismiss').addEventListener('click', () => this.dismiss('Alarm dismissed.'));
    query('#ring-stop').addEventListener('click', () => this.dismiss('Alarm stopped.'));
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && this.activeAlarm) this.dismiss('Alarm stopped.'); });
  }
  /** @param {object} alarm */
  async ring(alarm) {
    if (this.activeAlarm) return false;
    this.activeAlarm = alarm; this.lastFocused = document.activeElement;
    query('#ring-label').textContent = alarm.label || 'Alarm';
    query('#ring-tone').textContent = alarm.toneName || 'Alarm tone';
    const overlay = query('#ringing-overlay'); overlay.hidden = false; query('#ring-dismiss').focus(); this.updateClock();
    try { await this.audio.play(alarm.tone); } catch (error) { console.warn('Alarm audio could not start.', error); }
    return true;
  }
  updateClock() { const current = new Date(); const hour24 = current.getHours(); const hour = this.state.settings.timeFormat === '24' ? hour24 : (hour24 % 12 || 12); query('#ring-time').innerHTML = `${String(hour).padStart(2, '0')}:${String(current.getMinutes()).padStart(2, '0')}<small>${this.state.settings.timeFormat === '12' ? ` ${hour24 >= 12 ? 'PM' : 'AM'}` : ''}</small>`; this.timerId = window.setTimeout(() => this.updateClock(), 1000 - (Date.now() % 1000) + 8); }
  snooze() { const alarm = this.activeAlarm; if (!alarm) return; this.close(); this.onSnooze(alarm); }
  dismiss(message) { if (!this.activeAlarm) return; this.close(); if (message) import('./ui.js').then(({ showToast }) => showToast(message, 'success')); }
  close() { window.clearTimeout(this.timerId); this.timerId = null; this.audio.stop(); this.activeAlarm = null; query('#ringing-overlay').hidden = true; if (this.lastFocused instanceof HTMLElement) this.lastFocused.focus(); }
}
