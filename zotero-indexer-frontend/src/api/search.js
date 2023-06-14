import { useQuery } from '@tanstack/react-query';

export default function useSearchQuery(query) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: async () => {
      const response = await fetch(`//localhost:8000/_api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(query),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
    networkMode: 'always',
    refetchOnWindowFocus: false,
  });
}
