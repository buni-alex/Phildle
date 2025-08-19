import { initUser } from "../services/history_service"

let cachedUserUuid: string | null = null

export async function getUser(): Promise<{ user_uuid: string; new_user: boolean }> {
  if (!cachedUserUuid) {
    const data = await initUser() 
    cachedUserUuid = data.user_uuid
    return { user_uuid: cachedUserUuid, new_user: data.new_user }
  }
  else
    return { user_uuid: cachedUserUuid, new_user: false }
}

export function clearUserCache() {
  cachedUserUuid = null
}