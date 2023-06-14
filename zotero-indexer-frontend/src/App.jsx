import { MantineProvider, ColorSchemeProvider, AppShell } from '@mantine/core';
import { useLocalStorage } from '@mantine/hooks';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import AppHeader from './components/header';
import ResultList from './components/result-list';


function App() {
  const [colorScheme, setColorScheme] = useLocalStorage({
    key: 'mantine-color-scheme',
    defaultValue: 'light',
    getInitialValueInEffect: true,
  });
  const toggleColorScheme = (value) =>
    setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));

  const queryClient = new QueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <ColorSchemeProvider
        colorScheme={colorScheme}
        toggleColorScheme={toggleColorScheme}>
        <MantineProvider
          withGlobalStyles
          withNormalizeCSS
          theme={{ colorScheme }}
        >
          <AppShell
            header={<AppHeader />}
          >
            <ResultList />
          </AppShell>
        </MantineProvider>
      </ColorSchemeProvider>
    </QueryClientProvider>
  )
}

export default App
