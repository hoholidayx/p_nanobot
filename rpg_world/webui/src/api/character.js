import api from './index'

export function listCharacters() {
  return api.get('/characters').then((r) => r.data.characters)
}

export function getCharacter(name) {
  return api.get(`/characters/${encodeURIComponent(name)}`).then((r) => r.data)
}

export function createCharacter(data) {
  return api.post('/characters', data).then((r) => r.data.data)
}

export function updateCharacter(name, data) {
  return api
    .put(`/characters/${encodeURIComponent(name)}`, data)
    .then((r) => r.data.data)
}

export function deleteCharacter(name) {
  return api
    .delete(`/characters/${encodeURIComponent(name)}`)
    .then((r) => r.data)
}
