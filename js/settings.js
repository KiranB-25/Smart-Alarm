/** Settings UI and persistence controller. */
import { query } from './utils.js';
import { applyAppearance, showToast } from './ui.js';

/** Applies user preferences and keeps their storage representation current. */
export class SettingsController {
  /** @param {object} state @param {() => void} persist @param {object} dependencies */
  constructor(state, persist, { clock, alarmManager, alarmAudio, timerAudio, notifications }) {
    this.state = state; this.persist = persist; this.clock = clock; this.alarmManager = alarmManager; this.alarmAudio = alarmAudio; this.timerAudio = timerAudio; this.notifications = notifications;
    this.render(); this.bind();
  }
  bind() {
    query('#setting-time-format').addEventListener('click', () => this.setTimeFormat());
    query('#setting-snooze').addEventListener('change', (event) => this.update('snoozeMinutes', Number(event.target.value)));
    query('#setting-tone').addEventListener('change', (event) => this.update('defaultTone', event.target.value));
    query('#setting-volume').addEventListener('input', (event) => this.setVolume(event.target.value));
    query('#setting-notifications').addEventListener('click', () => this.toggleNotifications());
    query('#setting-animations').addEventListener('click', () => this.toggleAnimations());
    query('#theme-choices').addEventListener('click', (event) => { const button = event.target.closest('[data-theme]'); if (button) this.setTheme(button.dataset.theme); });
  }
  render() {
    const settings = this.state.settings;
    query('#setting-time-format').setAttribute('aria-checked', String(settings.timeFormat === '24'));
    query('#setting-snooze').value = String(settings.snoozeMinutes); query('#setting-tone').value = settings.defaultTone;
    query('#setting-volume').value = String(settings.volume); query('#setting-volume-output').textContent = `${Math.round(settings.volume * 100)}%`;
    query('#setting-notifications').setAttribute('aria-checked', String(settings.notificationsEnabled));
    query('#setting-animations').setAttribute('aria-checked', String(settings.animationsEnabled));
    for (const button of document.querySelectorAll('[data-theme]')) button.setAttribute('aria-pressed', String(button.dataset.theme === settings.theme));
  }
  update(key, value) { this.state.settings[key] = value; this.persist(); }
  setTimeFormat() { const format = this.state.settings.timeFormat === '12' ? '24' : '12'; this.update('timeFormat', format); this.clock.setFormat(format); this.alarmManager.render(); this.render(); showToast(`${format}-hour time enabled.`, 'success'); }
  setTheme(theme) { if (!['dark', 'light', 'system'].includes(theme)) return; this.update('theme', theme); applyAppearance(this.state.settings); this.render(); }
  setVolume(value) { const volume = Math.min(1, Math.max(0, Number(value))); this.update('volume', volume); this.alarmAudio.setVolume(volume); this.timerAudio.setVolume(volume); query('#setting-volume-output').textContent = `${Math.round(volume * 100)}%`; }
  async toggleNotifications() {
    if (this.state.settings.notificationsEnabled) { this.update('notificationsEnabled', false); this.render(); return; }
    try {
      const permission = await this.notifications.requestPermission();
      if (permission !== 'granted') { showToast('Notifications were not enabled. You can change this in your browser settings.', 'error'); return; }
      this.update('notificationsEnabled', true); this.render(); showToast('Alarm notifications enabled.', 'success');
    } catch (error) { showToast(error.message || 'Notifications could not be enabled.', 'error'); }
  }
  toggleAnimations() { this.update('animationsEnabled', !this.state.settings.animationsEnabled); applyAppearance(this.state.settings); this.render(); }
}
