with open("frontend/src/services/api.js", "r") as f:
    content = f.read()

instagram_api = """
export const instagramAPI = {
  // Search for Instagram posts
  searchPosts: async (searchParams) => {
    try {
      const response = await apiClient.post('/instagram/search', searchParams);
      return response.data;
    } catch (error) {
      console.error('Error searching instagram posts:', error);
      throw error;
    }
  },

  // Get analytics summary
  getAnalyticsSummary: async (searchParams) => {
    try {
      const response = await apiClient.post('/instagram/analytics', searchParams);
      return response.data;
    } catch (error) {
      console.error('Error getting instagram analytics summary:', error);
      throw error;
    }
  }
};
"""

content = content + "\n" + instagram_api

with open("frontend/src/services/api.js", "w") as f:
    f.write(content)
