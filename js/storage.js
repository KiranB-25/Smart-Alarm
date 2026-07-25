/** Validated browser persistence service. */
import { DEFAULT_STATE, normalizeState } from './state.js';

const STORAGE_KEY = 'smart-alarm.state.v1';

/** @returns {{alarms: Array, settings: object}} */
export function loadState() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? normalizeState(JSON.parse(raw)) : structuredClone(DEFAULT_STATE);
  } catch (error) {
    console.warn('Smart Alarm could not restore saved data.', error);
    return structuredClone(DEFAULT_STATE);
  }
}

/** @param {{alarms: Array, settings: object}} state */
export function saveState(state) {
  try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(normalizeState(state))); return true; }
  catch (error) { console.warn('Smart Alarm could not save data.', error); return false; }
}
