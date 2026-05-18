/**
 * Profile fields (first name, last name, photo URL) bound to the main store; saving calls the user API
 * and writes the response back into `user`.
 *
 * @module pages/profile/ProfileForm
 */

import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useState } from 'react';

import { SubmitButton } from '@components/submitButton';
import { useUserAPIClient } from '@services/apiClient/user';
import { useMainStore } from '@store/main/mainStore';

/**
 * Renders editable profile fields with unsaved-change highlighting and a save action.
 *
 * @returns The profile form inside a paper container.
 */
export function ProfileForm() {
  const { patchUser } = useUserAPIClient();

  const { user } = useMainStore();

  const [newFirstName, setNewFirstName] = useState<string>(user?.firstName ?? '');
  const [newLastName, setNewLastName] = useState<string>(user?.lastName ?? '');
  const [newPhotoUrl, setNewPhotoUrl] = useState<string>(user?.photoUrl ?? '');

  /** Sends the current field values to the API and replaces `user` in the store on success. */
  const handleSave = async () => {
    patchUser({
      firstName: newFirstName,
      lastName: newLastName,
      photoUrl: newPhotoUrl,
    });
  };

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h4" sx={{ mb: 2 }}>
        Profile
      </Typography>
      <Stack direction="column" spacing={2}>
        <TextField
          label="First name"
          name="firstName"
          value={newFirstName}
          onChange={(e) => setNewFirstName(e.target.value)}
          color={newFirstName !== user?.firstName ? 'warning' : 'primary'}
          focused={newFirstName !== user?.firstName ? true : undefined}
        />
        <TextField
          label="Last name"
          name="lastName"
          value={newLastName}
          onChange={(e) => setNewLastName(e.target.value)}
          color={newLastName !== user?.lastName ? 'warning' : 'primary'}
          focused={newLastName !== user?.lastName ? true : undefined}
        />
        <TextField
          label="Photo URL"
          name="photoUrl"
          value={newPhotoUrl}
          onChange={(e) => setNewPhotoUrl(e.target.value)}
          color={newPhotoUrl !== user?.photoUrl ? 'warning' : 'primary'}
          focused={newPhotoUrl !== user?.photoUrl ? true : undefined}
        />
      </Stack>
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <SubmitButton label="Save" onClick={handleSave} color="primary" />
      </Box>
    </Paper>
  );
}
