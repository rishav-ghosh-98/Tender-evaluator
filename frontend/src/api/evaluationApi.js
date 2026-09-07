const API_URL = 'http://127.0.0.1:8000'

export async function evaluateTender(formData) {
  const response = await fetch(`${API_URL}/evaluate`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let message = `Evaluation failed with status ${response.status}.`

    try {
      const errorBody = await response.json()
      if (Array.isArray(errorBody.detail)) {
        message = errorBody.detail.map((item) => item.msg).join('; ')
      } else if (errorBody.detail) {
        message = errorBody.detail
      }
    } catch {
      // Keep the status-based message when the server does not return JSON.
    }

    throw new Error(message)
  }

  return response.json()
}
