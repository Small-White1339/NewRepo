import client from './client';
import type { TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse } from '../types';

export async function login(data: UserLoginRequest): Promise<TokenResponse> {
  const res = await client.post<TokenResponse>('/auth/login', data);
  return res.data;
}

export async function register(data: UserRegisterRequest): Promise<UserResponse> {
  const res = await client.post<UserResponse>('/auth/register', data);
  return res.data;
}

export async function getMe(): Promise<UserResponse> {
  const res = await client.get<UserResponse>('/users/me');
  return res.data;
}

export async function updateMe(data: Partial<Pick<UserRegisterRequest, 'username' | 'email'>>): Promise<UserResponse> {
  const res = await client.put<UserResponse>('/users/me', data);
  return res.data;
}
