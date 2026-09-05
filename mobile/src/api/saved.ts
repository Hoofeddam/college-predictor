import { College } from "./college";
import { request } from "./client";

// Mirrors serialize_saved_college() exactly.
export interface SavedCollege {
  id: number;
  college: College;
  created_at: string | null;
}

// Module-level cache, not Context/Zustand -- lives entirely in this file.
// GET /saved returns a user's full saved list with no pagination, and
// CollegeDetailScreen needs that same list on every mount just to check
// one college's saved status. Rather than re-fetching the whole list every
// time a screen wants to know "is this saved", the first call populates
// this cache and everything after reuses it until something explicitly
// asks for fresh data (forceRefresh, or a save/unsave mutating it in
// place).
let cache: SavedCollege[] | null = null;

export function getSavedColleges(forceRefresh = false): Promise<{ saved: SavedCollege[] }> {
  if (cache && !forceRefresh) {
    return Promise.resolve({ saved: cache });
  }

  return request<{ saved: SavedCollege[] }>("/saved").then((data) => {
    cache = data.saved;
    return data;
  });
}

export function saveCollege(collegeId: number): Promise<{ saved: SavedCollege }> {
  return request<{ saved: SavedCollege }>(`/saved/${collegeId}`, { method: "POST" }).then((data) => {
    // POST is idempotent -- data.saved.id is the definitive row whether it
    // was just created or already existed, so de-duping by that id and
    // putting it first keeps the cache consistent with the backend's own
    // most-recent-first ordering without a second network call.
    if (cache) {
      cache = [data.saved, ...cache.filter((entry) => entry.id !== data.saved.id)];
    }

    return data;
  });
}

export function unsaveCollege(savedId: number): Promise<void> {
  return request<void>(`/saved/${savedId}`, { method: "DELETE" }).then(() => {
    if (cache) {
      cache = cache.filter((entry) => entry.id !== savedId);
    }
  });
}

// Called on logout -- otherwise a second user logging in on the same app
// session would see the first user's cached saved list until a forced
// refresh happened to overwrite it.
export function clearSavedCollegesCache() {
  cache = null;
}
