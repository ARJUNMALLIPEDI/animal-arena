// Small, self-contained visual stand-in per category so the UI doesn't
// depend on fetching/hosting real photography for 47 animals.
export const CATEGORY_ICON: Record<string, string> = {
  mammal: '🐾',
  reptile: '🦎',
  fish: '🦈',
  bird: '🪶',
  invertebrate: '🐙',
}

export const CATEGORY_COLOR: Record<string, string> = {
  mammal: 'from-amber-700/40 to-arena-panel',
  reptile: 'from-emerald-700/40 to-arena-panel',
  fish: 'from-sky-700/40 to-arena-panel',
  bird: 'from-violet-700/40 to-arena-panel',
  invertebrate: 'from-fuchsia-700/40 to-arena-panel',
}
