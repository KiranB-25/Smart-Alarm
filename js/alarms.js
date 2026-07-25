/** Alarm lifecycle, validation, and schedule configuration controller. */
import { createId, escapeHtml, isIntegerInRange, query } from './utils.js';
import { showToast } from './ui.js';

export const TONES = [
  ['classic-bell', 'Classic Bell'], ['digital-alarm', 'Digital Alarm'], ['morning-birds', 'Morning Birds'], ['soft-piano', 'Soft Piano'],
  ['nature', 'Nature'], ['electronic', 'Electronic'], ['gentle-chime', 'Gentle Chime'], ['sunrise', 'Sunrise'],
];
const TONE_IDS = new Set(TONES.map(([id]) => id));
const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/** Manages alarm CRUD and the accessible editor UI. */
export class AlarmManager {
  /** @param {object} state @param {() => void} persist @param {import('./audio.js').AudioController} audio */
  constructor(state, persist, audio) { this.state = state; this.persist = persist; this.audio = audio; this.editingId = null; this.bind(); this.render(); }

  bind() {
    query('#add-alarm').addEventListener('click', () => this.openEditor());
    query('#cancel-alarm').addEventListener('click', () => this.closeEditor());
    query('#alarm-repeat').addEventListener('change', (event) => this.toggleCustomDays(event.target.value));
    query('#alarm-form').addEventListener('submit', (event) => this.save(event));
    query('#alarm-list').addEventListener('click', (event) => this.handleListAction(event));
    query('#tone-play').addEventListener('click', () => this.previewTone());
    query('#tone-pause').addEventListener('click', () => this.pauseTone());
    query('#tone-stop').addEventListener('click', () => this.stopTone());
  }

  render() {
    const list = query('#alarm-list');
    if (!this.state.alarms.length) { list.innerHTML = '<li class="empty-state">No alarms yet. Add one to make your next morning a little easier.</li>'; return; }
    list.innerHTML = this.state.alarms.slice().sort((a, b) => (a.hour * 60 + a.minute) - (b.hour * 60 + b.minute)).map((alarm) => `
      <li class="alarm-row" data-alarm-id="${alarm.id}" data-enabled="${alarm.enabled}">
        <button class="toggle" type="button" role="switch" aria-checked="${alarm.enabled}" aria-label="${alarm.enabled ? 'Disable' : 'Enable'} ${escapeHtml(alarm.label || 'alarm')}" data-action="toggle"></button>
        <time class="alarm-time">${this.formatTime(alarm)}</time>
        <div class="alarm-details"><p class="alarm-label">${escapeHtml(alarm.label || 'Alarm')}</p><p class="alarm-meta">${this.describeRepeat(alarm)} · ${this.toneName(alarm.tone)}</p></div>
        <div class="alarm-actions"><button class="icon-button" type="button" data-action="edit" aria-label="Edit ${escapeHtml(alarm.label || 'alarm')}">✎</button><button class="icon-button button-danger" type="button" data-action="delete" aria-label="Delete ${escapeHtml(alarm.label || 'alarm')}">×</button></div>
      </li>`).join('');
  }

  openEditor(alarm = null) {
    this.editingId = alarm?.id ?? null;
    const form = query('#alarm-form'); form.hidden = false;
    query('#alarm-form-title').textContent = alarm ? 'Edit alarm' : 'New alarm';
    query('#alarm-time').value = alarm ? `${String(alarm.hour).padStart(2, '0')}:${String(alarm.minute).padStart(2, '0')}` : '07:00';
    query('#alarm-label').value = alarm?.label ?? '';
    query('#alarm-tone').value = alarm?.tone ?? this.state.settings.defaultTone;
    query('#alarm-repeat').value = alarm?.repeat ?? 'once';
    for (const input of form.querySelectorAll('[name="days"]')) input.checked = Boolean(alarm?.days?.includes(Number(input.value)));
    this.toggleCustomDays(alarm?.repeat ?? 'once'); query('#alarm-time').focus();
  }

  closeEditor() { this.stopTone(); query('#alarm-form').hidden = true; this.editingId = null; query('#alarm-form').reset(); }
  toggleCustomDays(repeat) { query('#custom-days').hidden = repeat !== 'custom'; }

  save(event) {
    event.preventDefault();
    const form = event.currentTarget; const [hourText, minuteText] = query('#alarm-time', form).value.split(':');
    if (!isIntegerInRange(hourText, 0, 23) || !isIntegerInRange(minuteText, 0, 59)) { showToast('Choose a valid alarm time.', 'error'); return; }
    const repeat = query('#alarm-repeat', form).value;
    const days = [...form.querySelectorAll('[name="days"]:checked')].map((input) => Number(input.value));
    if (repeat === 'custom' && !days.length) { showToast('Choose at least one custom repeat day.', 'error'); return; }
    const tone = query('#alarm-tone', form).value;
    if (!TONE_IDS.has(tone)) { showToast('Choose a ringtone before saving this alarm.', 'error'); return; }
    const candidate = { id: this.editingId ?? createId(), hour: Number(hourText), minute: Number(minuteText), label: query('#alarm-label', form).value.trim().slice(0, 60), tone, repeat, days, enabled: true };
    const duplicate = this.state.alarms.some((alarm) => alarm.id !== candidate.id && alarm.hour === candidate.hour && alarm.minute === candidate.minute && alarm.repeat === candidate.repeat && JSON.stringify(alarm.days ?? []) === JSON.stringify(candidate.days));
    if (duplicate) { showToast('An alarm with the same time and repeat schedule already exists.', 'error'); return; }
    const previous = this.state.alarms.find((alarm) => alarm.id === candidate.id);
    if (previous) Object.assign(previous, candidate, { enabled: previous.enabled }); else this.state.alarms.push(candidate);
    this.persist(); this.render(); this.closeEditor(); showToast(previous ? 'Alarm updated.' : 'Alarm created.', 'success');
  }

  handleListAction(event) {
    const button = event.target.closest('[data-action]'); if (!button) return;
    const row = button.closest('[data-alarm-id]'); const alarm = this.state.alarms.find((item) => item.id === row?.dataset.alarmId); if (!alarm) return;
    if (button.dataset.action === 'toggle') { alarm.enabled = !alarm.enabled; this.persist(); this.render(); showToast(`Alarm ${alarm.enabled ? 'enabled' : 'disabled'}.`, 'success'); }
    if (button.dataset.action === 'edit') this.openEditor(alarm);
    if (button.dataset.action === 'delete') { this.state.alarms = this.state.alarms.filter((item) => item.id !== alarm.id); this.persist(); this.render(); showToast('Alarm deleted.'); }
  }

  async previewTone() { try { const tone = query('#alarm-tone').value; await this.audio.play(TONE_IDS.has(tone) ? tone : this.state.settings.defaultTone); query('#tone-play').setAttribute('aria-pressed', 'true'); query('#tone-pause').setAttribute('aria-pressed', 'false'); } catch (error) { showToast(error.message || 'Unable to play this ringtone.', 'error'); } }
  async pauseTone() { try { if (this.audio.paused) { await this.audio.resume(); query('#tone-pause').setAttribute('aria-pressed', 'false'); } else { await this.audio.pause(); query('#tone-pause').setAttribute('aria-pressed', 'true'); } } catch (error) { showToast(error.message || 'Unable to pause this ringtone.', 'error'); } }
  stopTone() { this.audio.stop(); const play = document.querySelector('#tone-play'); const pause = document.querySelector('#tone-pause'); if (play) play.setAttribute('aria-pressed', 'false'); if (pause) pause.setAttribute('aria-pressed', 'false'); }

  formatTime(alarm) { const period = alarm.hour >= 12 ? 'PM' : 'AM'; const hour = this.state.settings.timeFormat === '24' ? alarm.hour : (alarm.hour % 12 || 12); return `${String(hour).padStart(2, '0')}:${String(alarm.minute).padStart(2, '0')}${this.state.settings.timeFormat === '12' ? `<small> ${period}</small>` : ''}`; }
  toneName(tone) { return TONES.find(([id]) => id === tone)?.[1] ?? 'Classic Bell'; }
  describeRepeat(alarm) { if (alarm.repeat === 'custom') return alarm.days.map((day) => DAY_NAMES[day]).join(', '); return ({ once: 'Once', everyday: 'Every day', weekdays: 'Weekdays', weekends: 'Weekends' })[alarm.repeat] ?? 'Once'; }
}

/** Evaluates enabled alarms at minute boundaries and handles snoozes. */
export class AlarmScheduler {
  /** @param {object} state @param {(alarm: object) => void} onRing @param {() => void} persist */
  constructor(state, onRing, persist) { this.state = state; this.onRing = onRing; this.persist = persist; this.seen = new Set(); this.snoozeTimers = new Set(); this.timerId = null; }
  start() { this.check(); this.scheduleNextCheck(); }
  stop() { window.clearTimeout(this.timerId); for (const id of this.snoozeTimers) window.clearTimeout(id); this.snoozeTimers.clear(); }
  scheduleNextCheck() { this.timerId = window.setTimeout(() => { this.check(); this.scheduleNextCheck(); }, 1000 - (Date.now() % 1000) + 12); }
  check() {
    const now = new Date();
    if (now.getSeconds() > 1) return;
    for (const alarm of this.state.alarms) {
      if (!alarm.enabled || alarm.hour !== now.getHours() || alarm.minute !== now.getMinutes() || !this.matchesDay(alarm, now)) continue;
      const key = `${alarm.id}:${now.getFullYear()}-${now.getMonth()}-${now.getDate()}-${now.getHours()}-${now.getMinutes()}`;
      if (this.seen.has(key)) continue; this.seen.add(key); this.trigger(alarm);
    }
    if (this.seen.size > 1000) this.seen.clear();
  }
  matchesDay(alarm, date) { const day = date.getDay(); return alarm.repeat === 'everyday' || (alarm.repeat === 'weekdays' && day >= 1 && day <= 5) || (alarm.repeat === 'weekends' && (day === 0 || day === 6)) || (alarm.repeat === 'custom' && (alarm.days ?? []).includes(day)) || alarm.repeat === 'once'; }
  trigger(alarm) { if (alarm.repeat === 'once') { alarm.enabled = false; this.persist(); } this.onRing(alarm); }
  snooze(alarm) { const minutes = this.state.settings.snoozeMinutes; const id = window.setTimeout(() => { this.snoozeTimers.delete(id); this.onRing({ ...alarm, label: `${alarm.label || 'Alarm'} · Snoozed` }); }, minutes * 60 * 1000); this.snoozeTimers.add(id); import('./ui.js').then(({ showToast }) => showToast(`Snoozed for ${minutes} minute${minutes === 1 ? '' : 's'}.`, 'success')); }
}
