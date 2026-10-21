/**
 * Tests for {@link Avatar}: photo rendering and the initials fallback for missing or broken URLs.
 */

import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vite-plus/test';

import { Avatar } from './Avatar';

const avatarImage = (container: HTMLElement) => container.querySelector('img');

describe('Avatar', () => {
  it.each([undefined, null, ''])('shows initials when src is %j', (src) => {
    const { container } = render(<Avatar src={src} label="reader" />);

    expect(screen.getByLabelText('avatar')).toHaveTextContent(/^RE$/);
    expect(avatarImage(container)).toBeNull();
  });

  it('uses the whole label when it is shorter than two characters', () => {
    render(<Avatar label="r" />);

    expect(screen.getByLabelText('avatar')).toHaveTextContent(/^R$/);
  });

  it('shows the photo when src is set', () => {
    const { container } = render(<Avatar src="/images/me.png" label="reader" />);

    expect(avatarImage(container)).toHaveAttribute('src', '/images/me.png');
    expect(screen.getByLabelText('avatar')).not.toHaveTextContent('RE');
  });

  it('falls back to initials when the photo fails to load', () => {
    const { container } = render(<Avatar src="/images/broken.png" label="reader" />);

    fireEvent.error(avatarImage(container)!);

    expect(avatarImage(container)).toBeNull();
    expect(screen.getByLabelText('avatar')).toHaveTextContent(/^RE$/);
  });

  it('tries a new photo after the previous one failed', () => {
    const { container, rerender } = render(<Avatar src="/images/broken.png" label="reader" />);
    fireEvent.error(avatarImage(container)!);

    rerender(<Avatar src="/images/new.png" label="reader" />);

    expect(avatarImage(container)).toHaveAttribute('src', '/images/new.png');
  });
});
