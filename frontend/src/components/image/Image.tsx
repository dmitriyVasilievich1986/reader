/**
 * Lazy-loaded image with a storefront icon fallback when the URL is missing or fails to load.
 */

import StorefrontIcon from '@mui/icons-material/Storefront';
import { useState } from 'react';

/**
 * Renders an `<img>` when `src` is present and loads successfully; otherwise shows `StorefrontIcon`.
 *
 * @param {object} props - Component props.
 * @param {string | null | undefined} props.src - Image URL; when empty, the fallback icon is shown.
 * @param {number | string | undefined} props.width - Passed to the image or icon sizing (`style` / `sx`).
 * @param {number | string | undefined} props.height - Passed to the image or icon sizing (`style` / `sx`).
 * @param {string | undefined} props.alt - Accessible label for the image or icon fallback.
 * @returns {JSX.Element} Image or Material UI storefront icon.
 */
export function Image(props: {
  src?: string | null;
  width?: number | string;
  height?: number | string;
  alt?: string;
}) {
  const [failed, setFailed] = useState(false);

  if (!props.src || failed) {
    return (
      <StorefrontIcon
        sx={{ width: props.width, height: props.height }}
        aria-label={props.alt ?? 'Storefront icon'}
      />
    );
  }

  return (
    <img
      src={props.src}
      loading="lazy"
      style={{ width: props.width, height: props.height }}
      onError={() => setFailed(true)}
      alt={props.alt ?? 'Image'}
    />
  );
}
