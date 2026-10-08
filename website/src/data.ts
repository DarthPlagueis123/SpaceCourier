import metadata from './generated/metadata.json';
import recordings from './generated/recordings.json';

export const model = metadata;
export const clips = recordings;
export const format = (value: number, digits = 0) => value.toLocaleString('en-US', { maximumFractionDigits: digits });
export const percentage = (value: number) => `${Math.round(value * 100)}%`;

export const chapters = [
  { slug: 'game', title: 'Meet Space Courier', group: '01 / THE GAME', short: 'The mission', time: '4 min' },
  { slug: 'build-game', title: 'Build the arcade game', group: '01 / THE GAME', short: 'Build the game', time: '9 min' },
  { slug: 'environment', title: 'Make an environment', group: '02 / THE AGENT', short: 'The environment', time: '6 min' },
  { slug: 'state', title: 'What the AI sees', group: '02 / THE AGENT', short: 'State & actions', time: '6 min' },
  { slug: 'basics', title: 'Learn by doing', group: '02 / THE AGENT', short: 'RL essentials', time: '5 min' },
  { slug: 'rewards', title: 'Give learning a direction', group: '02 / THE AGENT', short: 'The reward', time: '5 min' },
  { slug: 'q-learning', title: 'Think beyond the next move', group: '03 / THE NETWORK', short: 'Q-learning', time: '7 min' },
  { slug: 'network', title: 'Build a neural network', group: '03 / THE NETWORK', short: 'The PyTorch model', time: '7 min' },
  { slug: 'memory', title: 'Remember. Replay. Stabilize.', group: '03 / THE NETWORK', short: 'Replay & targets', time: '7 min' },
  { slug: 'exploration', title: 'Try something different', group: '04 / THE EXPERIMENT', short: 'Exploration', time: '4 min' },
  { slug: 'training', title: 'Put the learning loop together', group: '04 / THE EXPERIMENT', short: 'Training & settings', time: '8 min' },
  { slug: 'results', title: 'Read the real results', group: '04 / THE EXPERIMENT', short: 'Results & setbacks', time: '6 min' },
  { slug: 'watch', title: 'Watch the checkpoints', group: '05 / YOUR TURN', short: 'Watch it learn', time: '5 min' },
  { slug: 'reproduce', title: 'Run your own experiment', group: '05 / YOUR TURN', short: 'Train it yourself', time: '8 min' },
  { slug: 'next', title: 'Where to go next', group: '05 / YOUR TURN', short: 'Beyond this project', time: '4 min' },
];

export const navLinks = [
  { to: '/learn/game', label: 'The guide' },
  { to: '/results', label: 'Results' },
  { to: '/watch', label: 'Watch the AI' },
  { to: '/download', label: 'Downloads' },
];
