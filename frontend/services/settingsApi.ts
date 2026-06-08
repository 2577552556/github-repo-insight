import type { SettingsStatus, UpdateSettingsRequest } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getSettings(): Promise<SettingsStatus> {
  const response = await fetch(`${API_BASE_URL}/api/settings`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get settings");
  }

  return response.json();
}

export async function updateSettings(
  request: UpdateSettingsRequest
): Promise<SettingsStatus> {
  const response = await fetch(`${API_BASE_URL}/api/settings`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to update settings");
  }

  return response.json();
}