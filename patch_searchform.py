with open("frontend/src/components/SearchForm.jsx", "r") as f:
    content = f.read()

content = content.replace("const SearchForm = ({ onSearch, loading }) => {", "const SearchForm = ({ onSearch, loading, platform, setPlatform }) => {")

platform_selector = """
          <div className="flex justify-center mb-6 space-x-4">
            <Button
              type="button"
              onClick={() => setPlatform('YouTube')}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${platform === 'YouTube' ? 'bg-red-600 text-white shadow-lg' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
            >
              YouTube
            </Button>
            <Button
              type="button"
              onClick={() => setPlatform('Instagram')}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${platform === 'Instagram' ? 'bg-pink-600 text-white shadow-lg' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
            >
              Instagram
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
"""

content = content.replace("<div className=\"grid grid-cols-1 md:grid-cols-2 gap-6\">", platform_selector, 1)

content = content.replace("YouTube Trends Search", "{platform} Trends Search")
content = content.replace("from-red-50 to-red-100", "${platform === 'YouTube' ? 'from-red-50 to-red-100' : 'from-pink-50 to-pink-100'}")
content = content.replace("text-red-700", "${platform === 'YouTube' ? 'text-red-700' : 'text-pink-700'}")
content = content.replace("bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-8 py-3 rounded-lg font-semibold transform transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl", "${platform === 'YouTube' ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800' : 'bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800'} text-white px-8 py-3 rounded-lg font-semibold transform transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl")

content = content.replace("<CardHeader className=\"bg-gradient-to-r ${platform === 'YouTube' ? 'from-red-50 to-red-100' : 'from-pink-50 to-pink-100'} rounded-t-lg\">", "<CardHeader className={`bg-gradient-to-r ${platform === 'YouTube' ? 'from-red-50 to-red-100' : 'from-pink-50 to-pink-100'} rounded-t-lg`}>")
content = content.replace("<CardTitle className=\"flex items-center space-x-2 ${platform === 'YouTube' ? 'text-red-700' : 'text-pink-700'}\">", "<CardTitle className={`flex items-center space-x-2 ${platform === 'YouTube' ? 'text-red-700' : 'text-pink-700'}`}>")
content = content.replace("<Button\n              type=\"submit\"\n              disabled={loading}\n              className=\"${platform === 'YouTube' ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800' : 'bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800'} text-white px-8 py-3 rounded-lg font-semibold transform transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl\"\n            >", "<Button\n              type=\"submit\"\n              disabled={loading}\n              className={`${platform === 'YouTube' ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800' : 'bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800'} text-white px-8 py-3 rounded-lg font-semibold transform transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl`}\n            >")

content = content.replace("focus:border-red-500 focus:ring-red-500", "focus:border-red-500 focus:ring-red-500") # Actually let's just make it focus-pink for instagram if we want, but keeping simple

with open("frontend/src/components/SearchForm.jsx", "w") as f:
    f.write(content)
