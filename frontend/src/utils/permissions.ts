import { User } from '../types';

/**
 * Permission helper to determine whether a user can access the Advisory feature.
 * Strictly returns true ONLY when authenticated user.user_type is "Farmer" (case-insensitive).
 * Returns false for all other roles (General User, Researcher, Disaster Management,
 * Government, Aviation, Marine, Student, etc.) and unauthenticated/guest users.
 */
export const canAccessAdvisory = (user?: Partial<User> | null): boolean => {
  if (!user || !user.user_type) {
    return false;
  }
  const typeNormalized = String(user.user_type).trim().toLowerCase();
  return typeNormalized === 'farmer';
};
