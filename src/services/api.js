import axios from 'axios'

const API_BASE_URL = '/api'

const apiService = {
  async uploadPhoto(file) {
    const formData = new FormData()
    formData.append('photo', file)

    const response = await axios.post(`${API_BASE_URL}/upload-photo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  },

  async getGarments() {
    const response = await axios.get(`${API_BASE_URL}/garments`)
    return response.data
  },

  async tryOn(userPhoto, garmentId) {
    const response = await axios.post(`${API_BASE_URL}/try-on`, {
      user_photo: userPhoto,
      garment_id: garmentId,
    })

    return response.data
  },

  async healthCheck() {
    const response = await axios.get(`${API_BASE_URL}/health`)
    return response.data
  },
}

export default apiService
