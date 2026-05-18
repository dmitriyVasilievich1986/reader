/**
 * Login route: username/password form that authenticates via {@link useAuthAPIClient}, stores the access token in a cookie,
 * and navigates to the `redirectTo` query parameter (default `/`).
 *
 * @module pages/login/Login
 */

import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { InputAdornment } from '@mui/material';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import dayjs from 'dayjs';
import Cookies from 'js-cookie';
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router';

import { SubmitButton } from '@components/submitButton';
import { useAuthAPIClient } from '@services/apiClient/auth';
import { useMainStore } from '@store/main/mainStore';

/**
 * Presents credential fields and submits login; shows API errors as helper text on both fields.
 *
 * @returns The login form inside a centered container.
 */
export function Login() {
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');

  const navigate = useNavigate();

  const { user, setUser } = useMainStore();

  const [searchParams] = useSearchParams();
  const redirectTo = searchParams.get('redirectTo') ?? '/';

  const { login } = useAuthAPIClient();

  useEffect(() => {
    if (user === null) return;
    setUser(null);
  }, [user, setUser]);

  /** Calls the login API, sets the `accessToken` cookie using the response expiry, then navigates to `redirectTo`. */
  const handleSubmit = async () => {
    login(username, password)
      .then((response) => {
        Cookies.set('accessToken', response.accessToken, {
          expires: dayjs(response.expiresAt).toDate(),
        });
        navigate(redirectTo);
      })
      .catch((error) => {
        setError(error?.response?.data?.detail || 'An unknown error occurred');
      });
  };

  /** Toggles whether the password field shows plain text or masked input. */
  const handleClickShowPassword = () => {
    setShowPassword((previous) => !previous);
  };

  return (
    <Container maxWidth="sm">
      <Paper sx={{ p: 2, mt: 4 }}>
        <Box sx={{ my: 4 }}>
          <Stack spacing={2}>
            <TextField
              label="Username"
              name="username"
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                setError('');
              }}
              autoComplete="username"
              error={!!error}
              helperText={error}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSubmit();
                }
              }}
            />
            <TextField
              label="Password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError('');
              }}
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleClickShowPassword}>
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
              autoComplete="current-password"
              error={!!error}
              helperText={error}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSubmit();
                }
              }}
            />
            <SubmitButton label="Login" color="primary" onClick={handleSubmit} />
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
