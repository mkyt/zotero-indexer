import { useAtom } from 'jotai';

import { queryAtom } from '../atoms/query';
import useSearchQuery from '../api/search';

export default function ResultList() {
  const [query, setQuery] = useAtom(queryAtom);
  const { data, isLoading, isError } = useSearchQuery(query);
  if (isLoading) {
    return <div>Loading...</div>;
  }
  console.log(data);
  return (
    <div>
      <div>Search results for {query.q}</div>
    </div>
  );
}
