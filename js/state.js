/** Application state defaults and immutable update helpers. */
export const DEFAULT_SETTINGS = Object.freeze({
  timeFormat: '12', theme: 'system', snoozeMinutes: 5, notificationsEnabled: false,
  volume: 0.7, defaultTone: 'classic-bell', animationsEnabled: true,
});

export const DEFAULT_STATE = Object.freeze({ alarms: [], settings: DEFAULT_SETTINGS });
const TONE_IDS = new Set(['classic-bell', 'digital-alarm', 'morning-birds', 'soft-piano', 'nature', 'electronic', 'gentle-chime', 'sunrise']);

/** @param {unknown} value @returns {boolean} */
export function isRecord(value) { return Boolean(value) && typeof value === 'object' && !Array.isArray(value); }

/** @param {unknown} value @returns {typeof DEFAULT_SETTINGS} */
export function normalizeSettings(value) {
  const source = isRecord(value) ? value : {};
  const snoozeOptions = [1, 5, 10, 15, 30];
  return {
    timeFormat: source.timeFormat === '24' ? '24' : '12',
    theme: ['dark', 'light', 'system'].includes(source.theme) ? source.theme : (['espresso', 'midnight', 'dusk'].includes(source.theme) ? 'dark' : DEFAULT_SETTINGS.theme),
    snoozeMinutes: snoozeOptions.includes(Number(source.snoozeMinutes)) ? Number(source.snoozeMinutes) : DEFAULT_SETTINGS.snoozeMinutes,
    notificationsEnabled: source.notificationsEnabled === true,
    volume: Number.isFinite(Number(source.volume)) ? Math.min(1, Math.max(0, Number(source.volume))) : DEFAULT_SETTINGS.volume,
    defaultTone: TONE_IDS.has(source.defaultTone) ? source.defaultTone : DEFAULT_SETTINGS.defaultTone,
    animationsEnabled: source.animationsEnabled !== false,
  };
}

/** @param {unknown} value @returns {{alarms: Array, settings: typeof DEFAULT_SETTINGS}} */
export function normalizeState(value) {
  const source = isRecord(value) ? value : {};
  const settings = normalizeSettings(source.settings);
  const alarms = Array.isArray(source.alarms) ? source.alarms.map((alarm) => normalizeAlarm(alarm, settings.defaultTone)).filter(Boolean) : [];
  return { alarms, settings };
}

function normalizeAlarm(value, defaultTone) {
  if (!isRecord(value) || typeof value.id !== 'string' || !value.id) return null;
  const hour = Number(value.hour); const minute = Number(value.minute);
  if (!Number.isInteger(hour) || hour < 0 || hour > 23 || !Number.isInteger(minute) || minute < 0 || minute > 59) return null;
  const repeat = ['once', 'everyday', 'weekdays', 'weekends', 'custom'].includes(value.repeat) ? value.repeat : 'once';
  const days = Array.isArray(value.days) ? [...new Set(value.days.map(Number).filter((day) => Number.isInteger(day) && day >= 0 && day <= 6))] : [];
  return { id: value.id, hour, minute, label: typeof value.label === 'string' ? value.label.slice(0, 60) : '', tone: TONE_IDS.has(value.tone) ? value.tone : defaultTone, repeat, days, enabled: value.enabled !== false };
}
