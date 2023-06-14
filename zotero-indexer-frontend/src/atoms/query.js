import { atom } from 'jotai'


export const queryAtom = atom({ q: '' })

export const queryStringAtom = atom(
  (get) => {
    const query = get(queryAtom);
    return query.q;
  },
  (get, set, newQueryString) => {
    const query = get(queryAtom);
    set(queryAtom, { ...query, q: newQueryString });
  }
)
