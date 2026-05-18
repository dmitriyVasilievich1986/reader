/**
 * Navbar logout control: removes the `accessToken` cookie and navigates to `/login`.
 * The trigger is hidden when that cookie is absent.
 */
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import Cookies from 'js-cookie';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { Avatar } from '@components/avatar';
import { useUserAPIClient } from '@services/apiClient/user';
import { useMainStore } from '@store/main/mainStore';

/**
 * Renders a clickable "Logout" label when an `accessToken` cookie exists; otherwise returns null.
 *
 * @returns {JSX.Element | null} MUI Typography that clears the token and navigates to login, or nothing if logged out.
 */
export function Logout() {
  const navigate = useNavigate();

  const { user, setUser } = useMainStore();
  const { getUser } = useUserAPIClient();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  useEffect(() => {
    if (user === null && !!Cookies.get('accessToken')) {
      getUser().then((user) => {
        setUser(user);
      });
    }
  }, [user, Cookies.get('accessToken')]);

  /** Removes session cookie and redirects to the login route. */
  const handleLogout = () => {
    handleClose();
    Cookies.remove('accessToken');
    navigate('/login');
  };

  const avatarLabel = () => {
    if (user?.firstName && user?.lastName) {
      return `${user.firstName.charAt(0)}${user.lastName.charAt(0)}`;
    }
    return user?.username ?? '';
  };

  const getUsername = () => {
    if (!user) return 'Logout';

    if (user.firstName && user.lastName) {
      return `${user.firstName} ${user.lastName}`;
    }
    return user.username;
  };

  if (!Cookies.get('accessToken')) {
    return null;
  }
  return (
    <Box>
      <Box
        sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer' }}
        onClick={handleClick}
      >
        {open ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        {user && <Avatar src={user.photoUrl} label={avatarLabel()} />}
        <Typography variant="h6">{getUsername()}</Typography>
      </Box>
      <Menu
        sx={{ mt: 2 }}
        id="logout-menu"
        anchorEl={anchorEl}
        open={open}
        disableAutoFocusItem
        onClose={handleClose}
        slotProps={{
          list: {
            'aria-labelledby': 'logout-menu',
          },
        }}
      >
        <MenuItem
          onClick={() => {
            handleClose();
            navigate('/profile');
          }}
        >
          Profile
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>Logout</MenuItem>
        <Divider />
        <MenuItem
          disabled
          sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mx: 1 }}
        >
          <Typography variant="caption">Version {import.meta.env.VITE_APP_VERSION}</Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
}
