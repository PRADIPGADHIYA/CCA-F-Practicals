import { logEvent } from "./analytics";

export function sendOrderShipped(orderId: string, email: string): void {
  // ... send the "your order shipped" email ...
  logEvent("order_shipped_email", { orderId, email });
}

export function sendReturnApproved(orderId: string): void {
  // ... send the "return approved" email ...
  logEvent("return_approved_email", { orderId });
}
