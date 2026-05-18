/**
 * Navbar.tsx
 *
 * This file contains the Navbar component, which is a sticky app bar with primary navigation links (e.g. Home).
 *
 * @returns MUI `AppBar` wrapping a toolbar and router links.
 */

import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { Link } from 'react-router';

import { Image } from '@components/image';

import { Logout } from './logout/Logout';
import { default as defaultImage } from './reader.svg';
/**
 * Sticky app bar with primary navigation links (e.g. Home).
 *
 * @returns MUI `AppBar` wrapping a toolbar and router links.
 */
export function Navbar() {
  return (
    <AppBar position="static">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              width: '100%',
              alignItems: 'center',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Image src={defaultImage} width={50} height={50} alt="Home" />
              <Stack direction="row" spacing={2}>
                <Link
                  to="/"
                  className="text-[#fff3b0] transition-colors hover:text-[#e09f3e] no-underline"
                >
                  <Typography variant="h6" sx={{ color: 'inherit' }}>
                    Home
                  </Typography>
                </Link>
                <Link
                  to="/book"
                  className="text-[#fff3b0] transition-colors hover:text-[#e09f3e] no-underline"
                >
                  <Typography variant="h6" sx={{ color: 'inherit' }}>
                    Books
                  </Typography>
                </Link>
              </Stack>
            </Box>
            <Logout />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
