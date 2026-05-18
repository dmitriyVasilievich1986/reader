/**
 * Type definitions for navbar logout menu navigation entries.
 */

/**
 * Label and route for a page linked from the user menu.
 *
 * @property {string} label - Text shown in the menu for this entry.
 * @property {string} path - Client route path (e.g. `/shop`) when the item is chosen.
 */
export type AvailablePageType = {
  label: string;
  path: string;
};
