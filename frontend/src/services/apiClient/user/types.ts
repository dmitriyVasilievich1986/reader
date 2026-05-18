/**
 * Request body types for user profile updates to `/api/v1/user`.
 */

/**
 * Payload for replacing editable profile fields (`PATCH /api/v1/user/me`).
 *
 * @property {string} firstName - User's given name.
 * @property {string} lastName - User's family name.
 * @property {(string | null)} photoUrl - Avatar image URL, or null when cleared.
 */
export type UserPatchRequest = {
  firstName?: string | null;
  lastName?: string | null;
  photoUrl?: string | null;
};
