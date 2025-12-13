import { describe, it, expect } from 'vitest';
import { formatDuration, getYouTubeEmbedUrl } from '../utils';

describe('utils', () => {
  it('formatDuration formats seconds correctly', () => {
    expect(formatDuration(75)).toBe('1:15');
    expect(formatDuration(3605)).toBe('1:00:05');
    expect(formatDuration(0)).toBe('0:00');
  });

  it('getYouTubeEmbedUrl returns nocookie url and parameters', () => {
    const url = getYouTubeEmbedUrl('abc123', { autoplay: true, startTime: 60 });
    expect(url).toContain('youtube-nocookie.com/embed/abc123');
    expect(url).toContain('autoplay=1');
    expect(url).toContain('start=60');
  });
});
