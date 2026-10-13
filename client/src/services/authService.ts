import { socketService } from "./socketService";

// --------------------
// TOKEN HELPERS
// --------------------

export const getToken = (): string | null => {
  return localStorage.getItem("access_token");
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};

export const logout = (): void => {
  localStorage.removeItem("access_token");
  socketService.disconnect();
};
