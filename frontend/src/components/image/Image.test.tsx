/**
 * Tests for {@link Image}: host-prefixed lazy image, forwarded props and ref, and the icon fallback.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { Image } from './Image';

const fallbackIcon = (container: HTMLElement) =>
  container.querySelector('[data-testid="StorefrontIcon"]');

describe('Image', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_IMAGES_HOST', '/static/images');
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('renders a lazy image prefixed with the images host', () => {
    render(
      <Image src="/covers/1.png" alt="War and Peace" className="cover" width={200} height="300px" />
    );

    const img = screen.getByRole('img', { name: 'War and Peace' });
    expect(img).toHaveAttribute('src', '/static/images/covers/1.png');
    expect(img).toHaveAttribute('loading', 'lazy');
    expect(img).toHaveClass('cover');
    expect(img).toHaveStyle({ width: '200px', height: '300px' });
  });

  it('uses a default alt text', () => {
    render(<Image src="/covers/1.png" />);

    expect(screen.getByRole('img', { name: 'Image' })).toBeInTheDocument();
  });

  it('forwards data-position and the ref to the img element', () => {
    const ref = createRef<HTMLImageElement>();
    render(<Image ref={ref} src="/pages/3.png" alt="3" data-position={3} />);

    const img = screen.getByRole('img', { name: '3' });
    expect(img).toHaveAttribute('data-position', '3');
    expect(ref.current).toBe(img);
  });

  it.each([undefined, null, ''])('shows the fallback icon when src is %j', (src) => {
    const { container } = render(<Image src={src} alt="Missing cover" />);

    expect(container.querySelector('img')).toBeNull();
    expect(fallbackIcon(container)).toHaveAttribute('aria-label', 'Missing cover');
  });

  it('labels the fallback icon by default', () => {
    const { container } = render(<Image />);

    expect(fallbackIcon(container)).toHaveAttribute('aria-label', 'Storefront icon');
  });

  it('switches to the fallback icon when the image fails to load', () => {
    const { container } = render(<Image src="/covers/broken.png" alt="Broken" width={50} />);

    fireEvent.error(screen.getByRole('img', { name: 'Broken' }));

    expect(container.querySelector('img')).toBeNull();
    expect(fallbackIcon(container)).toHaveAttribute('aria-label', 'Broken');
    expect(fallbackIcon(container)).toHaveStyle({ width: '50px' });
  });
});
