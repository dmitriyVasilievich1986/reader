import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import { getAuthorName, parseIntWithCheck } from '@utils';
import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router';

import { useAuthorAPIClient, type SimpleAuthorType } from '@services/apiClient/author';

export function Authors() {
  const limit = 10;
  const columnHeaders = [
    {
      label: 'Name',
      key: 'name',
      isSortable: false,
    },
  ];

  const [authors, setAuthors] = useState<SimpleAuthorType[] | null>(null);
  const [totalAuthors, setTotalAuthors] = useState<number>(0);

  const [searchParams, setSearchParams] = useSearchParams();

  const { getAuthors } = useAuthorAPIClient();

  useEffect(() => {
    const pageRaw = searchParams.get('page');

    if (!pageRaw) {
      setSearchParams((previous) => {
        if (!pageRaw) previous.set('page', '0');
        return previous;
      });
      return;
    }

    const page = parseIntWithCheck(pageRaw, { defaultValue: 0 });
    const filters = searchParams.get('search')
      ? [{ column: 'name', operator: 'ilike', value: searchParams.get('search') }]
      : undefined;

    // Guard against out-of-order responses when params change faster than the network.
    let cancelled = false;
    getAuthors(
      limit,
      page * limit,
      searchParams.get('sortBy') ?? undefined,
      searchParams.get('sortOrder') ?? undefined,
      filters
    )
      .then(({ data, metadata }) => {
        if (cancelled) return;
        setAuthors(data);
        setTotalAuthors(metadata.total);
      })
      .catch((error) => {
        setAuthors([] as SimpleAuthorType[]);
        setTotalAuthors(0);
        console.error('Error fetching authors:', error);
      });

    return () => {
      cancelled = true;
    };
  }, [searchParams]);

  if (authors === null) {
    return (
      <Container maxWidth="lg" sx={{ mt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Skeleton variant="rectangular" sx={{ width: '300px', height: '40px' }} />
          <Skeleton variant="rectangular" sx={{ width: '100px', height: '40px' }} />
        </Box>
        <Skeleton variant="rectangular" sx={{ width: '100%', height: '400px' }} />
      </Container>
    );
  }
  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      <TableContainer component={Paper}>
        <Table sx={{ width: '100%' }} aria-label="simple table">
          <TableHead>
            <TableRow>
              {columnHeaders.map((header) => (
                <TableCell
                  key={header.key}
                  onClick={() => {
                    if (!header.isSortable) return;
                    setSearchParams((previous) => {
                      if (previous.get('sortBy') === header.key) {
                        previous.set(
                          'sortOrder',
                          previous.get('sortOrder') === 'asc' ? 'desc' : 'asc'
                        );
                      } else {
                        previous.set('sortBy', header.key);
                        previous.set('sortOrder', 'asc');
                      }
                      return previous;
                    });
                  }}
                >
                  <TableSortLabel>{header.label}</TableSortLabel>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {(authors ?? []).map((author) => (
              <TableRow key={author.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                <TableCell component="th" scope="row">
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Link
                      to={`/book?filters=${JSON.stringify([{ column: 'author_id', operator: 'eq', value: author.id }])}`}
                      style={{
                        textDecoration: 'none',
                        color: '#023e8a',
                        fontWeight: 'bold',
                        marginLeft: '0.25rem',
                      }}
                    >
                      {getAuthorName(author)}
                    </Link>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={totalAuthors}
          rowsPerPage={limit}
          page={parseIntWithCheck(searchParams.get('page'), { defaultValue: 0 })}
          onPageChange={(_, page) => setSearchParams({ page: page.toString() })}
          rowsPerPageOptions={[]}
        />
      </TableContainer>
    </Container>
  );
}
