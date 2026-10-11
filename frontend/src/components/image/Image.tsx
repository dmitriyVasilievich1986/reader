/**
 * Lazy-loaded image with a storefront icon fallback when the URL is missing or fails to load.
 */

import StorefrontIcon from '@mui/icons-material/Storefront';
import { forwardRef, useState } from 'react';

import type { ImageProps } from './types';

export const Image = forwardRef<HTMLImageElement, ImageProps>(function Image(props, ref) {
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
      src={import.meta.env.VITE_IMAGES_HOST + props.src}
      loading="lazy"
      style={{ width: props.width, height: props.height }}
      onError={() => setFailed(true)}
      alt={props.alt ?? 'Image'}
      className={props.className}
      ref={ref}
    />
  );
});
