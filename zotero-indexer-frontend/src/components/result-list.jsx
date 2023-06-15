import { useAtom } from 'jotai';
import { useMantineTheme, createStyles, Card, Text, Image } from '@mantine/core';
import { queryAtom } from '../atoms/query';
import useSearchQuery from '../api/search';
import getCoverImageURL from '../api/cover';

import './result-list.css';

const Highlighter = ({ children, colorScheme }) => {
  const theme = useMantineTheme();

  return (
    <span className={`highlighter ${theme.colorScheme}`} dangerouslySetInnerHTML={{ __html: children }} />
  );
};

const useStyles = createStyles((theme) => ({
  card: {
    backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.colors.gray[0],
    marginTop: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  inner: {
    display: 'flex',
    justifyContent: 'space-between',
  },
}));

function author2string(author) {
  var components = []
  if (author.literal) {
    components.push(author.literal)
  }
  if (author.given) {
    components.push(author.given)
  }
  if (author.family) {
    components.push(author.family)
  }
  return components.join(' ')
}

function Authors(props) {
  const authors = props.authors;
  const max_authors = props.maxAuthors || 8;
  if (!authors || authors.length === 0) {
    return null;
  }
  const converted = authors.map(author2string)
  var combined = '';
  if (authors.length > max_authors) {
    for (var i = 0; i < max_authors - 1; i++) {
      combined += converted[i] + ', ';
    }
    for (var i = max_authors - 1; i < authors.length - 1; i++) {
      if (converted[i].includes('<span class="highlight">')) {
        combined += '..., ' + author2string(authors[i]) + ', ..., ';
      }
    }
    combined += author2string(authors[authors.length - 1]);
  } else {
    combined = converted.join(', ');
  }
  return (
    <Highlighter>{ combined }</Highlighter>
  )
}

function VolumeIssuePages(props) {
  const doc = props.document.metadata;
  var res = ''
  if (doc.issued['date-parts']) {
    const date_parts = doc.issued['date-parts'][0];
    if (date_parts && date_parts.length > 0) {
      res += date_parts[0];
    }
  }
  if (doc.volume) {
    if (res.length > 0) {
      res += '; ';
    }
    res += doc.volume;
  }
  if (doc.issue) {
    res += '(' + doc.issue + ')';
  }
  if (doc.page) {
    if (res.length > 0) {
      res += ':';
    }
    res += doc.page;
  }
  return (
    <span>{res}</span>
  );
}

function Article(props) {
  const doc = props.document;
  const { classes } = useStyles();
  return (
    <Card withBorder radius="md" className={classes.card}>
      <div className={classes.inner}>
        <div className={classes.info}>
          <Text fz="lg" fw={700}><Highlighter>{doc.metadata['title']}</Highlighter></Text>
          <Text color="dimmed"><Authors authors={doc.metadata['author']} /></Text>
          <Text><span class="journal-title"><Highlighter>{doc.metadata['container-title']}</Highlighter></span> <VolumeIssuePages document={doc} /> {doc.metadata['DOI'] ? ' doi:' + doc.metadata['DOI'] : ''}</Text>
          <Text></Text>
        </div>
        <div>
          <Image
            styles={(theme) => ({
              root: {
                marginLeft: theme.spacing.md,
              },
              image: {
                border: '1px solid',
                borderColor: theme.colors.dark[0],
              }
            })}
            radius={3}
            src={getCoverImageURL(doc)}
            width={150}
            withPlaceholder />
        </div>
      </div>
    </Card>
  );
}

function Book(props) {
  const doc = props.document;
  const { classes } = useStyles();
  return (
    <Card withBorder radius="md" className={classes.card}>
      <Highlighter>{doc.metadata['title']}</Highlighter>
      <Highlighter>{doc.metadata['publisher']}</Highlighter>
      <Authors authors={doc.metadata['author']} />
      <Highlighter>{doc.metadata['ISBN']}</Highlighter>
    </Card>
  );
}

function Document(props) {
  const doc = props.document;
  const { classes } = useStyles();

  if (doc.metadata.type === 'article-journal') {
    return (
      <Article document={doc} />
    );
  } else if (doc.metadata.type === 'book') {
    return (
      <Book document={doc} />
    );
  } else {
    return (
      <Card withBorder radius="md" className={classes.card}>
        <Highlighter>{doc.metadata['title']}</Highlighter>
        <Highlighter>{doc.metadata['container-title']}</Highlighter>
        <Authors authors={doc.metadata['author']} />
        <Highlighter>{doc.metadata['DOI']}</Highlighter>
      </Card>
    );
  }

}



export default function ResultList() {
  const [query, setQuery] = useAtom(queryAtom);
  const { data, isLoading, isError } = useSearchQuery(query);
  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (isError) {
    return <div>Error!</div>;
  }
  return (
    <div>
      <div>Search results for "{query.q}"</div>
      {data.data.map((doc, idx) => (
        <Document key={idx} document={doc} />
      ))}
    </div>
  );
}
