import { useAtom } from 'jotai';

import { queryAtom } from '../atoms/query';

export default function ResultList() {
  const [query, setQuery] = useAtom(queryAtom);
  return (
    <div>
      <div>Search results for {query.q}</div>
    </div>
  );
}
