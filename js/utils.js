/** Shared utility functions. */
/** @returns {string} */
export function createId() { return crypto.randomUUID?.() ?? `alarm-${Date.now()}-${Math.random().toString(16).slice(2)}`; }

/** @param {string} value @param {number} min @param {number} max */
export function isIntegerInRange(value, min, max) { const number = Number(value); return Number.isInteger(number) && number >= min && number <= max; }

/** @param {unknown} error @param {string} fallback */
export function userMessage(error, fallback) { return error instanceof Error && error.message ? error.message : fallback; }

/** @param {string} selector @param {ParentNode} [parent] */
export function query(selector, parent = document) { const element = parent.querySelector(selector); if (!element) throw new Error(`Required element not found: ${selector}`); return element; }

/** Escapes values before inserting them into an HTML string. @param {string} value */
export function escapeHtml(value) { const element = document.createElement('span'); element.textContent = value; return element.innerHTML; }
