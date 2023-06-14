import { useState } from 'react'
import { useMantineColorScheme, useMantineTheme, createStyles, Header, TextInput, rem, ActionIcon } from '@mantine/core';
import { IconSearch, IconArrowRight, IconSun, IconMoonStars } from '@tabler/icons-react';
import { useAtom } from 'jotai';

import { queryStringAtom } from '../atoms/query';


const useHeaderStyles = createStyles((theme) => ({
  header: {
    paddingLeft: theme.spacing.md,
    paddingRight: theme.spacing.md,
  },
  inner: {
    height: rem(60),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  search: {
    margin: theme.spacing.md,
    flex: 1,
  },
}));


export default function AppHeader() {
  const { classes } = useHeaderStyles();
  const [query, setQuery] = useAtom(queryStringAtom);
  const [search, setSearch] = useState(query);
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const theme = useMantineTheme();
  return (
    <Header height={60} className={classes.header}>
      <div className={classes.inner}>
        <div>Zotero Search</div>
        <TextInput
          className={classes.search}
          value={search}
          onChange={(event) => setSearch(event.currentTarget.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.nativeEvent.isComposing) {
              setQuery(search);
            }
          }}
          radius="xl"
          placeholder="Search"
          icon={<IconSearch size="1.1rem" stroke={1.5} />}
          rightSection={
            <ActionIcon
              size={32}
              color={theme.primaryColor}
              radius="xl"
              variant="filled"
              onClick={() => setQuery(search)}
            >
              <IconArrowRight size="1.1rem" stroke={1.5} />
            </ActionIcon>
          }
        />
        <ActionIcon
          variant="outline"
          color={colorScheme === 'dark' ? 'yellow' : 'blue'}
          onClick={() => toggleColorScheme()}
          title="Toggle color scheme"
        >
          {colorScheme === 'dark' ? <IconSun size="1.1rem" /> : <IconMoonStars size="1.1rem" />}
        </ActionIcon>
      </div>
    </Header>
  )
}
