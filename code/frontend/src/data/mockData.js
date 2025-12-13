/**
 * Mock data for development and testing
 * 
 * This provides sample video data when the backend is not available.
 * Simulates a YouTube-like video library with categories.
 */

// Sample video data
export const mockVideos = [
  {
    id: '1',
    ytId: 'dQw4w9WgXcQ',
    title: 'Synthwave Retro Mix - 80s Electronic Dreams',
    description: 'Eine Reise durch die besten Synthwave-Tracks der 80er Jahre. Perfekt für Late-Night Coding Sessions.',
    channelName: 'RetroWave FM',
    channelId: 'ch1',
    category: 'Musik',
    duration: 3724, // seconds
    viewCount: 1250000,
    likeCount: 45000,
    publishDate: '2024-01-15T12:00:00Z',
    thumbnailUrl: null, // Will use YouTube thumbnail
    tags: ['synthwave', '80s', 'electronic', 'retro'],
  },
  {
    id: '2',
    ytId: 'jNQXAC9IVRw',
    title: 'Classic Gaming - Die Geschichte der Videospiele',
    description: 'Eine Dokumentation über die Anfänge der Videospielindustrie, von Pong bis zu den ersten Heimkonsolen.',
    channelName: 'Retro Gaming TV',
    channelId: 'ch2',
    category: 'Gaming',
    duration: 2856,
    viewCount: 890000,
    likeCount: 32000,
    publishDate: '2024-02-20T15:30:00Z',
    thumbnailUrl: null,
    tags: ['gaming', 'retro', 'documentary', 'history'],
  },
  {
    id: '3',
    ytId: 'M7lc1UVf-VE',
    title: 'VHS Ästhetik Tutorial - Retro Video Effects',
    description: 'Lerne, wie du authentische VHS-Effekte in deinen Videos erstellst. Mit After Effects und DaVinci Resolve.',
    channelName: 'Pixel Art Academy',
    channelId: 'ch3',
    category: 'Tutorial',
    duration: 1245,
    viewCount: 456000,
    likeCount: 21000,
    publishDate: '2024-03-05T10:00:00Z',
    thumbnailUrl: null,
    tags: ['vhs', 'tutorial', 'editing', 'effects'],
  },
  {
    id: '4',
    ytId: '9bZkp7q19f0',
    title: 'Rick und Morty - Best of Season 1',
    description: 'Die lustigsten Momente aus der ersten Staffel von Rick und Morty.',
    channelName: 'Adult Swim Clips',
    channelId: 'ch4',
    category: 'Comedy',
    duration: 987,
    viewCount: 3500000,
    likeCount: 125000,
    publishDate: '2024-01-01T18:00:00Z',
    thumbnailUrl: null,
    tags: ['comedy', 'animation', 'rick and morty'],
  },
  {
    id: '5',
    ytId: 'hT_nvWreIhg',
    title: 'Analog Synthesizer Basics - Moog Tutorial',
    description: 'Einführung in die Welt der analogen Synthesizer. Oszillatoren, Filter und Envelopes erklärt.',
    channelName: 'Synth Master Class',
    channelId: 'ch5',
    category: 'Musik',
    duration: 2134,
    viewCount: 234000,
    likeCount: 18000,
    publishDate: '2024-02-10T14:00:00Z',
    thumbnailUrl: null,
    tags: ['synthesizer', 'music', 'tutorial', 'analog'],
  },
  {
    id: '6',
    ytId: 'kJQP7kiw5Fk',
    title: 'Pixel Art Masterclass - Von 0 zum Profi',
    description: 'Kompletter Kurs für Pixel Art. Lerne die Grundlagen und fortgeschrittene Techniken.',
    channelName: 'Pixel Art Academy',
    channelId: 'ch3',
    category: 'Tutorial',
    duration: 5467,
    viewCount: 678000,
    likeCount: 45000,
    publishDate: '2024-03-10T09:00:00Z',
    thumbnailUrl: null,
    tags: ['pixel art', 'tutorial', 'art', 'design'],
  },
  {
    id: '7',
    ytId: 'fJ9rUzIMcZQ',
    title: 'Bohemian Rhapsody - Queen Live at Wembley',
    description: 'Legendärer Live-Auftritt von Queen beim Live Aid Konzert 1985.',
    channelName: 'Classic Rock TV',
    channelId: 'ch6',
    category: 'Musik',
    duration: 372,
    viewCount: 12000000,
    likeCount: 890000,
    publishDate: '2023-12-01T20:00:00Z',
    thumbnailUrl: null,
    tags: ['queen', 'rock', 'live', 'classic'],
  },
  {
    id: '8',
    ytId: 'ZZ5LpwO-An4',
    title: 'Cyberpunk 2077 - Night City Tour',
    description: 'Eine virtuelle Tour durch Night City. Entdecke alle Bezirke und versteckten Orte.',
    channelName: 'Gaming Chronicles',
    channelId: 'ch7',
    category: 'Gaming',
    duration: 3456,
    viewCount: 567000,
    likeCount: 34000,
    publishDate: '2024-02-28T16:00:00Z',
    thumbnailUrl: null,
    tags: ['cyberpunk', 'gaming', 'tour', 'night city'],
  },
  {
    id: '9',
    ytId: 'pB-5XG-DbAA',
    title: 'CRT TV Restoration - Full Guide',
    description: 'Wie du einen alten CRT-Fernseher restaurierst. Schritt-für-Schritt Anleitung.',
    channelName: 'Retro Tech Repair',
    channelId: 'ch8',
    category: 'Tutorial',
    duration: 2789,
    viewCount: 123000,
    likeCount: 9800,
    publishDate: '2024-03-15T11:00:00Z',
    thumbnailUrl: null,
    tags: ['crt', 'restoration', 'retro', 'tech'],
  },
  {
    id: '10',
    ytId: 'ScMzIvxBSi4',
    title: 'Futurama Marathon - Top 20 Episodes',
    description: 'Die 20 besten Futurama-Episoden aller Zeiten. Mit Szenen und Analyse.',
    channelName: 'Animation Central',
    channelId: 'ch9',
    category: 'Comedy',
    duration: 4567,
    viewCount: 890000,
    likeCount: 67000,
    publishDate: '2024-01-20T19:00:00Z',
    thumbnailUrl: null,
    tags: ['futurama', 'animation', 'comedy', 'best of'],
  },
  {
    id: '11',
    ytId: 'e-ORhEE9VVg',
    title: 'Tron Legacy Soundtrack - Full Album',
    description: 'Der komplette Soundtrack von Daft Punk zu Tron Legacy. Hochwertige Audio-Qualität.',
    channelName: 'Soundtrack Central',
    channelId: 'ch10',
    category: 'Musik',
    duration: 5234,
    viewCount: 2340000,
    likeCount: 156000,
    publishDate: '2023-11-15T21:00:00Z',
    thumbnailUrl: null,
    tags: ['tron', 'daft punk', 'soundtrack', 'electronic'],
  },
  {
    id: '12',
    ytId: 'OPf0YbXqDm0',
    title: 'NES Game Development - 6502 Assembly',
    description: 'Programmiere dein eigenes NES-Spiel in Assembly. Fortgeschrittenes Tutorial.',
    channelName: 'Retro Dev',
    channelId: 'ch11',
    category: 'Tutorial',
    duration: 7890,
    viewCount: 78000,
    likeCount: 6700,
    publishDate: '2024-03-01T08:00:00Z',
    thumbnailUrl: null,
    tags: ['nes', 'assembly', 'gamedev', 'programming'],
  },
];

// Categories derived from videos
export const mockCategories = [
  { name: 'Musik', icon: '🎵', videos: mockVideos.filter(v => v.category === 'Musik') },
  { name: 'Gaming', icon: '🎮', videos: mockVideos.filter(v => v.category === 'Gaming') },
  { name: 'Tutorial', icon: '📚', videos: mockVideos.filter(v => v.category === 'Tutorial') },
  { name: 'Comedy', icon: '😂', videos: mockVideos.filter(v => v.category === 'Comedy') },
];

// Featured video for hero section
export const mockFeaturedVideos = mockVideos.slice(0, 5);

// Continue watching (simulated watch progress)
export const mockContinueWatching = [
  { id: '3', progress: 0.45, watchedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { id: '8', progress: 0.72, watchedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString() },
  { id: '6', progress: 0.15, watchedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() },
];

// Default watchlist
export const mockWatchlist = [
  { id: '1', addedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '7', addedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '11', addedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() },
];

/**
 * Simulate API delay
 */
export function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Mock API functions
 */
export const mockApi = {
  async getVideos() {
    await delay(300);
    return mockVideos;
  },

  async getVideo(id) {
    await delay(200);
    return mockVideos.find(v => v.id === id || v.ytId === id);
  },

  async getCategories() {
    await delay(200);
    return mockCategories;
  },

  async searchVideos(query) {
    await delay(400);
    const q = query.toLowerCase();
    return mockVideos.filter(v =>
      v.title.toLowerCase().includes(q) ||
      v.description.toLowerCase().includes(q) ||
      v.category.toLowerCase().includes(q) ||
      v.tags.some(t => t.toLowerCase().includes(q))
    );
  },

  async getVideosByCategory(category) {
    await delay(300);
    return mockVideos.filter(v => v.category === category);
  },

  async getFeaturedVideos() {
    await delay(200);
    return mockFeaturedVideos;
  },
};

export default mockVideos;
