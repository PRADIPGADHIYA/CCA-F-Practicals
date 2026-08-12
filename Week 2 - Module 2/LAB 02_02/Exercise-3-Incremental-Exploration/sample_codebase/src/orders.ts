import { logEvent } from "./analytics";

export function markDelivered(orderId: string): void {
  logEvent("order_delivered", { orderId });
}

export function cancelOrder(orderId: string, reason: string): void {
  logEvent("order_cancelled", { orderId, reason });
}
