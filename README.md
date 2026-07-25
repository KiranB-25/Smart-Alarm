# Smart Alarm

Smart Alarm is a premium, privacy-first alarm, stopwatch, and countdown timer application for modern browsers. It is built entirely with HTML5, CSS3, and native ES modules—no frameworks, build tooling, trackers, or external runtime dependencies.

## Features

- Live digital clock with seconds, AM/PM, date, and 12/24-hour preferences
- Synchronized animated analog clock
- Unlimited alarms with labels, enabled state, editing, deletion, duplicate prevention, and local persistence
- Repeat schedules for once, every day, weekdays, weekends, or specific days
- Eight generated, offline-capable ringtones with preview, pause/resume, and stop controls
- Full ringing view with sound, animated bell, Snooze, Dismiss, and Stop actions
- Configurable snooze duration: 1, 5, 10, 15, or 30 minutes
- Browser notification integration, with user-controlled permission requests
- Stopwatch with pause/resume, reset, centiseconds, and multiple lap records
- Countdown timer with hour, minute, and second inputs, pause/resume, reset, and completion sound
- Persisted light, dark, and system appearance modes; animation preference; audio volume; clock format; notification preference; ringtone; snooze duration; and alarms
- Dedicated Home, Alarm, Clock, Stopwatch, Countdown Timer, and Settings screens with responsive bottom/side navigation
- Responsive, keyboard-accessible UI with reduced-motion support

## Screenshots

Screenshots can be added to [`assets/images/`](assets/images/) as the product evolves.

## Technologies Used

- HTML5
- CSS3: custom properties, Grid, Flexbox, media queries, animations
- Modern JavaScript (ES modules)
- Web Audio API
- Notifications API
- Web Storage API (`localStorage`)

## Folder Structure

```text
Smart-Alarm/
├── index.html
├── css/                 # Design tokens, layout, feature styles, responsiveness
├── js/                  # Feature-oriented ES modules
├── assets/
│   ├── audio/           # Reserved for licensed future sound assets
│   ├── fonts/           # Reserved for self-hosted licensed fonts
│   ├── icons/
│   └── images/
├── README.md
└── .gitignore
```

## Installation

No package installation is required. Clone or download this repository.

```bash
git clone <repository-url>
cd Smart-Alarm
```

## How to Run

Serve the directory with any static web server, then open the provided local address in a modern browser.

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080`.

> Opening `index.html` directly may work, but a local server is recommended for consistent module and notification behavior.

## Usage

1. Create an alarm from **Add alarm**, then select its time, tone, label, and repeat schedule.
2. Use the tone controls to preview the chosen sound before saving.
3. Adjust preferences in **Settings**. Enable notifications from that control when desired.
4. Use the stopwatch for elapsed-time tracking and the countdown for focused sessions.

Audio permission policies vary by browser. Interact with the page before expecting sound; browsers commonly require that initial gesture. Notifications also require HTTPS or `localhost`, plus explicit permission.

## Browser Compatibility

Designed for current versions of Chrome, Edge, Firefox, Safari, and mobile Safari/Chrome. The core clock, alarms, timer, and stopwatch work without notifications. Ringtone playback requires Web Audio API support; notification delivery requires the Notifications API and browser permission.

## Responsive Design

The interface is mobile-first and adapts across small phones, large phones, tablets, laptops, and desktop monitors using fluid type scales, Grid, Flexbox, relative sizing, and responsive breakpoints.

## Future Improvements

- Service-worker and installable PWA support for stronger background behavior
- Optional cloud synchronization and account-based backup
- Importable licensed audio files and custom uploaded ringtones
- Time-zone-aware travel mode
- Wake-up challenges and smart-home integrations

## License

No license has been specified. Add an explicit license before distributing or accepting third-party contributions.

## Author

Kiran Bukhari
