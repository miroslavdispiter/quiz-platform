import { io, Socket } from "socket.io-client";

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5000";

// Data the server sends with every quiz event
export interface QuizSocketEvent {
  quiz_id: string;
  title: string;
  message: string;
  status?: string;
  rejection_reason?: string | null;
}

/**
 * One shared WebSocket connection for the whole app.
 * The JWT is sent when connecting, so the server knows who we are and
 * puts us in the right "rooms" (by role and by user id).
 */
class SocketService {
  private socket: Socket | null = null;
  private token: string | null = null;

  connect(): Socket {
    const token = localStorage.getItem("access_token");

    // Already connected as the same user -> reuse the connection
    if (this.socket && this.token === token) {
      return this.socket;
    }

    // New user (or first connection) -> new connection with the new token
    this.disconnect();
    this.token = token;
    this.socket = io(SOCKET_URL, {
      transports: ["websocket", "polling"],
      auth: { token },
    });
    return this.socket;
  }

  on(event: string, callback: (data: QuizSocketEvent) => void) {
    this.connect().on(event, callback);
  }

  off(event: string, callback: (data: QuizSocketEvent) => void) {
    this.socket?.off(event, callback);
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.token = null;
    }
  }
}

export const socketService = new SocketService();
