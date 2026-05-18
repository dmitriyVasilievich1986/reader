/**
 * Auth API response types (login and related endpoints).
 */

/**
 * Payload returned after a successful login (`POST /api/login`).
 *
 * @property {string} accessToken - Bearer or session token for authenticated requests.
 * @property {string} expiresAt - Token expiry instant (typically ISO 8601) from the API.
 */
export type LoginResponse = {
  accessToken: string;
  expiresAt: string;
};
