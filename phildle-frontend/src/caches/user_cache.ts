import { initUser } from "../services/history_service"

//let cachedUserUuid: string | null = null

export async function getUser(): Promise<{ user_uuid: string; new_user: boolean }> {
  const cachedUserUuid = sessionStorage.getItem("user_uuid")

  if (!cachedUserUuid) {
    const data = await initUser()
    sessionStorage.setItem("user_uuid", data.user_uuid)
    return { user_uuid: data.user_uuid, new_user: data.new_user }
  } else {
    return { user_uuid: cachedUserUuid, new_user: false }
  }
}

export function clearUserCache() {
  sessionStorage.removeItem("user_uuid")
}