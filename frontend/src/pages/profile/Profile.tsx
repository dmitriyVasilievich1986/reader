/**
 * Profile page: waits for the signed-in user from the main store, then renders the profile editor.
 *
 * @module pages/profile/Profile
 */

import Container from '@mui/material/Container';
import Skeleton from '@mui/material/Skeleton';

import { useMainStore } from '@store/main/mainStore';

import { ProfileForm } from './ProfileForm';

/**
 * Shows a skeleton while the user is missing or still loading; otherwise wraps {@link ProfileForm} in a container.
 *
 * @returns Loading placeholder or the profile layout.
 */
export function Profile() {
  const { user, isLoading } = useMainStore();

  if (!user || isLoading) {
    return <Skeleton variant="rectangular" width={100} height={400} />;
  }
  return (
    <Container maxWidth="md">
      <ProfileForm />
    </Container>
  );
}
