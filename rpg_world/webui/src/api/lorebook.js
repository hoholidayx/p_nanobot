import api from './index'

export function listEntries() {
  return api.get('/lorebook/entries').then((r) => r.data.entries)
}

export function getEntry(name) {
  return api
    .get(`/lorebook/entries/${encodeURIComponent(name)}`)
    .then((r) => r.data)
}

export function createEntry(data) {
  return api.post('/lorebook/entries', data).then((r) => r.data.data)
}

export function updateEntry(name, data) {
  return api
    .put(`/lorebook/entries/${encodeURIComponent(name)}`, data)
    .then((r) => r.data.data)
}

export function deleteEntry(name) {
  return api
    .delete(`/lorebook/entries/${encodeURIComponent(name)}`)
    .then((r) => r.data)
}
