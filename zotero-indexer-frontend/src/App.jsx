import { MantineProvider, ColorSchemeProvider, AppShell } from '@mantine/core';
import { useLocalStorage } from '@mantine/hooks';

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
  return (
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
  )
}

export default App
