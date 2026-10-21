/**
 * Tests for the shared API client: auth/redirect interceptors on {@link apiClientInstance} and the
 * loading-state {@link useApiClientWrapper}.
 */

import { renderHook } from '@testing-library/react';
import { AxiosError, type AxiosAdapter, type InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main';

import { apiClientInstance, useApiClientWrapper } from './base';

const originalLocation = Object.getOwnPropertyDescriptor(window, 'location')!;
const originalAdapter = apiClientInstance.defaults.adapter;

/** Replaces `window.location` with a plain object so redirects can be asserted. */
const stubLocation = (pathname: string) => {
  const location = { pathname, href: `http://localhost${pathname}` };
  Object.defineProperty(window, 'location', { configurable: true, value: location });
  return location;
};

const okResponse = (config: InternalAxiosRequestConfig) => ({
  data: { ok: true },
  status: 200,
  statusText: 'OK',
  headers: {},
  config,
});

const errorResponse = (config: InternalAxiosRequestConfig, status: number) =>
  new AxiosError(`Request failed with status code ${status}`, 'ERR_BAD_REQUEST', config, null, {
    data: { detail: 'error' },
    status,
    statusText: '',
    headers: {},
    config,
  });

describe('apiClientInstance', () => {
  const adapter = vi.fn<AxiosAdapter>(async (config) => okResponse(config));

  beforeEach(() => {
    adapter.mockClear();
    apiClientInstance.defaults.adapter = adapter;
  });

  afterEach(() => {
    apiClientInstance.defaults.adapter = originalAdapter;
    Object.defineProperty(window, 'location', originalLocation);
    Cookies.remove('accessToken');
  });

  it('sends the bearer token, base URL and JSON content type', async () => {
    Cookies.set('accessToken', 'token-123');

    const response = await apiClientInstance.get('/api/v1/book');

    expect(response.data).toEqual({ ok: true });
    const config = adapter.mock.calls[0][0];
    expect(config.baseURL).toBe(import.meta.env.VITE_API_HOST ?? '');
    expect(config.url).toBe('/api/v1/book');
    expect(config.headers.Authorization).toBe('Bearer token-123');
    expect(config.headers['Content-Type']).toBe('application/json');
  });

  it('redirects to login and aborts the request without a token', async () => {
    const location = stubLocation('/book/7');

    await expect(apiClientInstance.get('/api/v1/book')).rejects.toThrow('Unauthorized');

    expect(adapter).not.toHaveBeenCalled();
    expect(location.href).toBe('/login?redirectTo=%2Fbook%2F7');
  });

  it('redirects to login on a 401 response and still rejects', async () => {
    Cookies.set('accessToken', 'expired');
    const location = stubLocation('/profile');
    adapter.mockImplementationOnce(async (config) => Promise.reject(errorResponse(config, 401)));

    await expect(apiClientInstance.get('/api/v1/user/me')).rejects.toMatchObject({
      response: { status: 401 },
    });

    expect(location.href).toBe('/login?redirectTo=%2Fprofile');
  });

  it('does not redirect on a 401 response while already on the login page', async () => {
    Cookies.set('accessToken', 'expired');
    const location = stubLocation('/login');
    adapter.mockImplementationOnce(async (config) => Promise.reject(errorResponse(config, 401)));

    await expect(apiClientInstance.get('/api/v1/user/me')).rejects.toBeInstanceOf(AxiosError);

    expect(location.href).toBe('http://localhost/login');
  });

  it('does not redirect on other error responses', async () => {
    Cookies.set('accessToken', 'token-123');
    const location = stubLocation('/book');
    adapter.mockImplementationOnce(async (config) => Promise.reject(errorResponse(config, 500)));

    await expect(apiClientInstance.get('/api/v1/book')).rejects.toMatchObject({
      response: { status: 500 },
    });

    expect(location.href).toBe('http://localhost/book');
  });
});

describe('useApiClientWrapper', () => {
  beforeEach(() => {
    useMainStore.setState({ isLoading: false });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('sets the loading flag while the call runs and returns its result', async () => {
    const { result } = renderHook(() => useApiClientWrapper());
    let resolveCall: (value: string) => void = () => {};
    const call = vi.fn(() => new Promise<string>((resolve) => (resolveCall = resolve)));

    const promise = result.current.wrapper(call);
    expect(useMainStore.getState().isLoading).toBe(true);

    resolveCall('done');
    await expect(promise).resolves.toBe('done');
    expect(useMainStore.getState().isLoading).toBe(false);
    expect(call).toHaveBeenCalledOnce();
  });

  it('logs and rethrows errors and clears the loading flag', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const { result } = renderHook(() => useApiClientWrapper());
    const error = new Error('Network error');

    await expect(result.current.wrapper(() => Promise.reject(error))).rejects.toBe(error);

    expect(consoleError).toHaveBeenCalledWith('Error:', error);
    expect(useMainStore.getState().isLoading).toBe(false);
  });
});
